"""Text Embedding with lazy model loading."""

from sentence_transformers import SentenceTransformer

from app.config import settings


class Embedder:
    def __init__(self):
        self.model: SentenceTransformer | None = None

    def _ensure_model(self):
        if self.model is None:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed(self, text: str):
        self._ensure_model()
        return self.model.encode(text)

    def embed_batch(self, texts: list[str]):
        self._ensure_model()
        return self.model.encode(texts)


# Module-level instance; model is loaded lazily on first use
embedder = Embedder()
