"""Chat Service"""

import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.conversational.memory import ConversationMemory
from app.conversational.query_router import query_router
from app.conversational.response_generator import response_generator
from app.embeddings.vector_store import VectorStore
from app.exceptions import LLMError
from app.logging_config import get_logger
from app.rag.rag_pipeline import rag_pipeline
from app.schemas.chat import ChatRequest, ChatResponse

logger = get_logger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with value and metadata."""

    value: str
    timestamp: float
    access_count: int = 0


class ChatService:
    """Service for handling conversational chat with equity research."""

    _cache: OrderedDict[str, CacheEntry] = OrderedDict()
    _last_call_time: float = 0
    _MIN_INTERVAL_SECONDS: int = 6
    _MAX_CACHE_SIZE: int = 100
    _CACHE_TTL_SECONDS: int = 3600
    _cache_hits: int = 0
    _cache_misses: int = 0

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        user_id: str | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        """Initialize chat service.

        Args:
            db: Database connection
            user_id: Optional user ID for conversation tracking
            vector_store: Optional vector store instance for RAG
        """
        self.memory = ConversationMemory(db)
        self.user_id = user_id
        self.vector_store = vector_store or VectorStore()

    async def process_query(self, request: ChatRequest) -> ChatResponse:
        """Process a chat query with RAG and LLM.

        Args:
            request: Chat request with query and session_id

        Returns:
            ChatResponse with answer and sources

        Raises:
            LLMError: If LLM processing fails
        """
        query = request.query.strip()

        intent, service_name = query_router.route(query)
        logger.info("Detected intent=%s routed_to=%s", intent, service_name)

        cached_entry = self._get_from_cache(query)
        if cached_entry:
            self._cache_hits += 1
            logger.info("Cache hit for query (hits=%d, misses=%d)", self._cache_hits, self._cache_misses)
            await self._save_conversation(request, cached_entry.value)
            return ChatResponse(answer=cached_entry.value, sources=[])

        self._cache_misses += 1

        try:
            _RAG_INTENTS = {"research_query", "general_query"}
            if intent in _RAG_INTENTS:
                logger.info("Running RAG pipeline (intent=%s)", intent)
                context = await rag_pipeline.run(self.vector_store, query)
                if not context or not context.strip():
                    logger.info("RAG returned no context — proceeding with empty context")
                    context = ""
                else:
                    logger.debug("RAG context preview: %s", context[:200])
            else:
                logger.info("Skipping RAG for intent=%s (API-only path)", intent)
                context = ""

            now = time.time()
            elapsed = now - self._last_call_time
            if elapsed < self._MIN_INTERVAL_SECONDS:
                sleep_time = self._MIN_INTERVAL_SECONDS - elapsed
                logger.info("Rate limiting Gemini (sleep=%.2fs)", sleep_time)
                await asyncio.sleep(sleep_time)

            self._last_call_time = time.time()
            logger.info("Calling Gemini")
            answer = await response_generator.generate_response(query, context, intent=intent)
            logger.debug("Gemini answer preview: %s", answer[:200])

        except Exception as e:
            logger.exception("LLM/RAG error: %s", repr(e))
            answer = (
                "WARNING: AI response is temporarily unavailable due to usage limits. "
                "Financial data and analysis are still available."
            )
            raise LLMError("LLM processing failed", details={"query": query, "error": str(e)}) from e

        self._add_to_cache(query, answer)

        await self._save_conversation(request, answer)

        return ChatResponse(answer=answer, sources=[])

    async def _save_conversation(self, request: ChatRequest, answer: str) -> None:
        """Save conversation safely without breaking flow.

        Args:
            request: Original chat request
            answer: Generated answer to save
        """
        try:
            await self.memory.save_message(request.session_id, "user", request.query, self.user_id)
            await self.memory.save_message(request.session_id, "assistant", answer, self.user_id)
        except Exception as e:
            logger.warning("Memory save skipped: %s", repr(e))

    def _get_from_cache(self, query: str) -> CacheEntry | None:
        """Get entry from cache if valid.

        Args:
            query: Query string to lookup

        Returns:
            CacheEntry if found and valid, None otherwise
        """
        if query not in self._cache:
            return None

        entry = self._cache[query]
        current_time = time.time()

        if current_time - entry.timestamp > self._CACHE_TTL_SECONDS:
            logger.debug("Cache entry expired for query: %s", query[:50])
            del self._cache[query]
            return None

        entry.access_count += 1
        self._cache.move_to_end(query)
        return entry

    def _add_to_cache(self, query: str, answer: str) -> None:
        """Add entry to cache with LRU eviction.

        Args:
            query: Query string as key
            answer: Answer to cache
        """
        if len(self._cache) >= self._MAX_CACHE_SIZE:
            evicted_key, evicted_entry = self._cache.popitem(last=False)
            logger.info(
                "Cache eviction: size=%d, evicted_key=%s, access_count=%d",
                len(self._cache),
                evicted_key[:50],
                evicted_entry.access_count,
            )

        self._cache[query] = CacheEntry(value=answer, timestamp=time.time())
        logger.debug("Added to cache: size=%d", len(self._cache))

    def _evict_expired_entries(self) -> int:
        """Evict all expired cache entries.

        Returns:
            Number of entries evicted
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items() if current_time - entry.timestamp > self._CACHE_TTL_SECONDS
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info("Evicted %d expired cache entries", len(expired_keys))

        return len(expired_keys)

    def get_cache_stats(self) -> dict[str, int | float]:
        """Get cache statistics.

        Returns:
            Dictionary with cache metrics
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0.0

        return {
            "size": len(self._cache),
            "max_size": self._MAX_CACHE_SIZE,
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self._CACHE_TTL_SECONDS,
        }

    def clear_cache(self) -> None:
        """Clear all cache entries."""
        cache_size = len(self._cache)
        self._cache.clear()
        logger.info("Cache cleared: %d entries removed", cache_size)
