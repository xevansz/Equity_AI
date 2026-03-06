"""Query Router"""

from app.conversational.intent_detector import intent_detector

_INTENT_SERVICE_MAP = {
    "price_query": "financial_service",
    "financial_query": "financial_service",
    "news_query": "news_service",
    "research_query": "research_service",
    "general_query": "chat_service",
}


class QueryRouter:
    def route(self, query: str) -> tuple[str, str]:
        intent = intent_detector.detect_intent(query)
        service_name = _INTENT_SERVICE_MAP.get(intent, "chat_service")
        return intent, service_name


query_router = QueryRouter()
