"""Response Generator"""

from app.llm.gemini import gemini
from app.llm.prompt_templates import (
    CHAT_PROMPT,
    FINANCIAL_CHAT_PROMPT,
    NEWS_CHAT_PROMPT,
    RESEARCH_CHAT_PROMPT,
)

_INTENT_PROMPT_MAP = {
    "price_query": FINANCIAL_CHAT_PROMPT,
    "financial_query": FINANCIAL_CHAT_PROMPT,
    "news_query": NEWS_CHAT_PROMPT,
    "research_query": RESEARCH_CHAT_PROMPT,
    "general_query": CHAT_PROMPT,
}


class ResponseGenerator:
    async def generate_response(
        self, query: str, context: str, intent: str = "general_query", history: list[dict] | None = None
    ):
        """Generate response with optional conversation history.

        Args:
            query: Current user query
            context: RAG context or financial data
            intent: Query intent type
            history: Optional list of previous messages (role, content)

        Returns:
            Generated response text
        """
        template = _INTENT_PROMPT_MAP.get(intent, CHAT_PROMPT)
        current_prompt = template.format(query=query, context=context)

        if history:
            # Build multi-turn conversation
            messages = []
            for msg in history:
                # Map 'assistant' to 'model' for Gemini API
                role = "model" if msg["role"] == "assistant" else msg["role"]
                messages.append({"role": role, "content": msg["content"]})
            # Add current query as final user message
            messages.append({"role": "user", "content": current_prompt})
            response = await gemini.generate_conversation(messages)
        else:
            # Single-turn for first messages (allows caching)
            response = await gemini.generate(current_prompt)

        return response


response_generator = ResponseGenerator()
