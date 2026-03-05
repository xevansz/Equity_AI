import hashlib

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.config import settings


class VectorStore:
    """Vector Store Management"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

        embedding_fn = SentenceTransformerEmbeddingFunction(model_name=settings.EMBEDDING_MODEL)

        self.collection = self.client.get_or_create_collection(name="equity_research", embedding_function=embedding_fn)

    def add_documents(self, documents: list[str], metadatas: list[dict] | None = None) -> None:
        ids = [f"doc_{hashlib.sha256(doc.encode('utf-8')).hexdigest()[:16]}" for doc in documents]
        self.collection.upsert(documents=documents, ids=ids, metadatas=metadatas)

    def search(self, query: str, top_k: int | None = None) -> dict:
        top_k = top_k or settings.TOP_K_RETRIEVAL
        results = self.collection.query(query_texts=[query], n_results=top_k)
        return results


vector_store = VectorStore()
