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
    async def generate_response(self, query: str, context: str, intent: str = "general_query"):
        template = _INTENT_PROMPT_MAP.get(intent, CHAT_PROMPT)
        prompt = template.format(query=query, context=context)
        response = await gemini.generate(prompt)
        return response


response_generator = ResponseGenerator()
