"""Intent Detection"""


class IntentDetector:
    def detect_intent(self, query: str) -> str:
        query_lower = query.lower()

        if any(word in query_lower for word in ["price", "stock", "quote"]):
            return "price_query"
        elif any(word in query_lower for word in ["financial", "earnings", "revenue"]):
            return "financial_query"
        elif any(word in query_lower for word in ["news", "latest", "recent"]):
            return "news_query"
        elif any(word in query_lower for word in ["report", "analysis", "research"]):
            return "research_query"
        else:
            return "general_query"


intent_detector = IntentDetector()
