"""Chat Service"""

import asyncio
import time

from app.conversational.memory import ConversationMemory
from app.conversational.response_generator import response_generator
from app.embeddings.vector_store import VectorStore
from app.logging_config import get_logger
from app.rag.rag_pipeline import rag_pipeline
from app.schemas.chat import ChatRequest, ChatResponse

logger = get_logger(__name__)


class ChatService:
    _cache = {}  # in memory cache

    _last_call_time = 0  # rate limiting
    _MIN_INTERVAL_SECONDS = 6  # change to 60 later

    def __init__(self, db, user_id: str | None = None, vector_store: VectorStore | None = None) -> None:
        self.memory = ConversationMemory(db)
        self.user_id = user_id
        self.vector_store = vector_store or VectorStore()

    async def process_query(self, request: ChatRequest) -> ChatResponse:
        query = request.query.strip()
        if query in self._cache:
            cached_answer = self._cache[query]

            await self._save_conversation(request, cached_answer)
            return ChatResponse(answer=cached_answer, sources=[])

        try:
            logger.info("Running RAG pipeline")
            context = await rag_pipeline.run(self.vector_store, query)

            if not context or not context.strip():
                answer = "No sufficient contextual data found for this query."
            else:
                logger.debug("RAG context preview: %s", context[:200])

                now = time.time()
                elapsed = now - self._last_call_time
                if elapsed < self._MIN_INTERVAL_SECONDS:
                    sleep_time = self._MIN_INTERVAL_SECONDS - elapsed
                    logger.info("Rate limiting Gemini (sleep=%.2fs)", sleep_time)
                    await asyncio.sleep(sleep_time)

                self._last_call_time = time.time()
                logger.info("Calling Gemini")
                answer = await response_generator.generate_response(query, context)
                logger.debug("Gemini answer preview: %s", answer[:200])

        except Exception as e:
            logger.exception("LLM/RAG error: %s", repr(e))
            answer = (
                "WARNING: AI response is temporarily unavailable due to usage limits. "
                "Financial data and analysis are still available."
            )

        self._cache[query] = answer

        await self._save_conversation(request, answer)

        return ChatResponse(answer=answer, sources=[])

    async def _save_conversation(self, request: ChatRequest, answer: str) -> None:
        """Save conversation safely without breaking flow"""
        try:
            await self.memory.save_message(request.session_id, "user", request.query, self.user_id)
            await self.memory.save_message(request.session_id, "assistant", answer, self.user_id)
        except Exception as e:
            logger.warning("Memory save skipped: %s", repr(e))
