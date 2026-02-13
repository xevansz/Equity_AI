"""Vector Store Management"""

import chromadb
from config import settings


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection("equity_research")

    def add_documents(self, documents: list, metadatas: list = None):
        ids = [f"doc_{i}" for i in range(len(documents))]
        self.collection.add(documents=documents, ids=ids, metadatas=metadatas)

    def search(self, query: str, top_k: int = None):
        top_k = top_k or settings.TOP_K_RETRIEVAL
        results = self.collection.query(query_texts=[query], n_results=top_k)
        return results


vector_store = VectorStore()
