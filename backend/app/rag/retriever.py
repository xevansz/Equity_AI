"""RAG Retriever"""

from embeddings.vector_store import vector_store


class Retriever:
    async def retrieve(self, query: str, top_k: int = 5):
        results = vector_store.search(query, top_k)
        return results["documents"][0] if results["documents"] else []


retriever = Retriever()
