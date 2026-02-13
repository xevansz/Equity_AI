"""Query Router"""

from conversational.intent_detector import intent_detector


class QueryRouter:
    def route(self, query: str):
        intent = intent_detector.detect_intent(query)

        routing = {
            "price_query": "financial_service",
            "financial_query": "financial_service",
            "news_query": "news_service",
            "research_query": "research_service",
            "general_query": "chat_service",
        }

        return routing.get(intent, "chat_service")


query_router = QueryRouter()
