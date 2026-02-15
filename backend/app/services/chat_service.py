"""Chat Service"""

import time
from rag.rag_pipeline import rag_pipeline
from conversational.response_generator import response_generator
from conversational.memory import ConversationMemory
from schemas.chat import ChatRequest, ChatResponse
import asyncio


class ChatService:
    _cache = {}  # in memory cache

    _last_call_time = 0  # rate limiting
    _MIN_INTERVAL_SECONDS = 6  # change to 60 later

    def __init__(self, db):
        self.memory = ConversationMemory(db)

    async def process_query(self, request: ChatRequest):
        query = request.query.strip()
        if query in self._cache:
            cached_answer = self._cache[query]

            await self._save_conversation(request, cached_answer)
            return ChatResponse(answer=cached_answer, sources=[])

        try:
            print("Running RAG pipeline...")
            context = await rag_pipeline.run(query)

            if not context or not context.strip():
                answer = "No sufficient contextual data found for this query."
            else:
                print("RAG Context (preview):", context[:200])

                now = time.time()
                elapsed = now - self._last_call_time
                if elapsed < self._MIN_INTERVAL_SECONDS:
                    sleep_time = self._MIN_INTERVAL_SECONDS - elapsed
                    print(f"⏳ Rate limiting Gemini ({sleep_time:.2f}s)")
                    await asyncio.sleep(sleep_time)

                self._last_call_time = time.time()
                print("Calling Gemini...")
                answer = await response_generator.generate_response(query, context)
                print("Gemini Answer (preview):", answer[:200])

        except Exception as e:
            print("🚨 LLM / RAG ERROR:", repr(e))
            answer = (
                "⚠️ AI response is temporarily unavailable due to usage limits. "
                "Financial data and analysis are still available."
            )

        self._cache[query] = answer

        await self._save_conversation(request, answer)

        return ChatResponse(answer=answer, sources=[])

    async def _save_conversation(self, request: ChatRequest, answer: str):
        """Save conversation safely without breaking flow"""
        try:
            await self.memory.save_message(request.session_id, "user", request.query)
            await self.memory.save_message(request.session_id, "assistant", answer)
        except Exception as e:
            print("⚠️ Memory save skipped:", repr(e))
