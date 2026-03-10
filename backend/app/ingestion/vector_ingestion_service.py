"""Vector Ingestion Service — chunks Mongo ingested_documents and upserts into Chroma."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.embeddings.chunker import chunker
from app.embeddings.vector_store import VectorStore
from app.logging_config import get_logger
from app.schemas.ingestion import IngestionDocument

logger = get_logger(__name__)

COLLECTION = "ingested_documents"

_DEFAULT_DOC_TYPES = ["earnings_transcript", "sec_filing"]


class VectorIngestionService:
    async def ingest(
        self,
        symbol: str,
        db: AsyncIOMotorDatabase,
        vector_store: VectorStore,
        doc_types: list[str] | None = None,
    ) -> dict:
        """
        Pull documents for *symbol* from Mongo, chunk them, and upsert into Chroma.

        Returns a summary dict with counts.
        """
        doc_types = doc_types or _DEFAULT_DOC_TYPES
        symbol = symbol.upper()

        docs_cursor = db[COLLECTION].find({"symbol": symbol, "type": {"$in": doc_types}})
        docs = [IngestionDocument.from_mongo(d) async for d in docs_cursor]

        return await self._embed_docs(docs, vector_store)

    async def reindex(
        self,
        symbol: str,
        db: AsyncIOMotorDatabase,
        vector_store: VectorStore,
    ) -> dict:
        """Re-chunk and re-upsert all doc types from Mongo for *symbol* (no re-fetch)."""
        return await self.ingest(symbol, db, vector_store, doc_types=_DEFAULT_DOC_TYPES)

    async def _embed_docs(self, docs: list[IngestionDocument], vector_store: VectorStore) -> dict:
        total_chunks = 0
        docs_embedded = 0

        for doc in docs:
            # Skip unavailable / empty docs
            if not doc.text or not doc.text.strip():
                continue
            if doc.raw and doc.raw.get("available") is False:
                continue

            chunks = chunker.chunk_text(doc.text)
            if not chunks:
                continue

            ids = [f"{doc.id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "symbol": doc.symbol,
                    "doc_type": doc.type,
                    "source": doc.source,
                    "title": doc.title,
                    "url": doc.url,
                    "published_at": doc.published_at,
                    "mongo_doc_id": doc.id,
                    "chunk_index": i,
                }
                for i in range(len(chunks))
            ]

            try:
                vector_store.add_documents(chunks, metadatas=metadatas, ids=ids)
                docs_embedded += 1
                total_chunks += len(chunks)
                logger.info(
                    "Embedded %d chunks for doc %s (%s / %s)",
                    len(chunks),
                    doc.id,
                    doc.type,
                    doc.symbol,
                )
            except Exception:
                logger.exception("Failed to embed doc %s (%s)", doc.id, doc.symbol)

        return {
            "docs_embedded": docs_embedded,
            "chunks_embedded": total_chunks,
        }
