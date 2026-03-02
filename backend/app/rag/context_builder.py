"""Context Builder"""


class ContextBuilder:
    def build_context(self, documents: list, query: str) -> str:
        context = f"Query: {query}\n\nRelevant Information:\n"
        for i, doc in enumerate(documents, 1):
            context += f"\n{i}. {doc}\n"
        return context


context_builder = ContextBuilder()
