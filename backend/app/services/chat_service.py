"""Chat Service"""

import time
from rag.rag_pipeline import rag_pipeline
from conversational.response_generator import response_generator
from conversational.memory import ConversationMemory
from schemas.chat import ChatRequest, ChatResponse


class ChatService:
    # 🔒 In-memory cache to avoid repeated Gemini calls
    _cache = {}

    # ⏱ Rate limiting (Gemini free tier safety)
    _last_call_time = 0
    _MIN_INTERVAL_SECONDS = 4  # 1 request every 4 seconds

    def __init__(self, db):
        self.memory = ConversationMemory(db)

    async def process_query(self, request: ChatRequest):
        query = request.query.strip()

        # ===============================
        # 1️⃣ RETURN CACHED RESPONSE
        # ===============================
        if query in self._cache:
            print("⚡ Gemini cache hit")
            cached_answer = self._cache[query]

            await self._save_conversation(request, cached_answer)
            return ChatResponse(answer=cached_answer, sources=[])

        try:
            # ===============================
            # 2️⃣ RUN RAG PIPELINE
            # ===============================
            print("Running RAG pipeline...")
            context = await rag_pipeline.run(query)

            if not context or not context.strip():
                print("⚠️ Empty RAG context – skipping Gemini")
                answer = "No sufficient contextual data found for this query."
            else:
                print("RAG Context (preview):", context[:200])

                # ===============================
                # 3️⃣ RATE LIMIT GEMINI CALL
                # ===============================
                now = time.time()
                elapsed = now - self._last_call_time
                if elapsed < self._MIN_INTERVAL_SECONDS:
                    sleep_time = self._MIN_INTERVAL_SECONDS - elapsed
                    print(f"⏳ Rate limiting Gemini ({sleep_time:.2f}s)")
                    time.sleep(sleep_time)

                self._last_call_time = time.time()

                # ===============================
                # 4️⃣ CALL GEMINI
                # ===============================
                print("Calling Gemini...")
                answer = await response_generator.generate_response(query, context)
                print("Gemini Answer (preview):", answer[:200])

        except Exception as e:
            # ===============================
            # 5️⃣ FAIL GRACEFULLY (NO 500)
            # ===============================
            print("🚨 LLM / RAG ERROR:", repr(e))
            answer = (
                "⚠️ AI response is temporarily unavailable due to usage limits. "
                "Financial data and analysis are still available."
            )

        # ===============================
        # 6️⃣ CACHE RESULT
        # ===============================
        self._cache[query] = answer

        # ===============================
        # 7️⃣ SAVE MEMORY (NON-BLOCKING)
        # ===============================
        await self._save_conversation(request, answer)

        return ChatResponse(answer=answer, sources=[])

    async def _save_conversation(self, request: ChatRequest, answer: str):
        """Save conversation safely without breaking flow"""
        try:
            await self.memory.save_message(request.session_id, "user", request.query)
            await self.memory.save_message(request.session_id, "assistant", answer)
        except Exception as e:
            print("⚠️ Memory save skipped:", repr(e))
