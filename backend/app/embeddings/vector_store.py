import chromadb
from app.config import settings
import hashlib


class VectorStore:
  """Vector Store Management"""

  def __init__(self):
    self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    self.collection = self.client.get_or_create_collection("equity_research")

  def add_documents(self, documents: list, metadatas: list = None):
    ids = [f"doc_{hashlib.sha256(doc.encode()).hexdigest()[:16]}" for doc in documents]
    self.collection.upsert(documents=documents, ids=ids, metadatas=metadatas)

  def search(self, query: str, top_k: int = None):
    top_k = top_k or settings.TOP_K_RETRIEVAL
    results = self.collection.query(query_texts=[query], n_results=top_k)
    return results


vector_store = VectorStore()
