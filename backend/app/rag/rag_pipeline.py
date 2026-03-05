"""RAG Pipeline Orchestration"""

from app.embeddings.vector_store import VectorStore
from app.rag.context_builder import context_builder
from app.rag.retriever import retriever


class RAGPipeline:
    async def run(self, vector_store: VectorStore, query: str):
        # Retrieve relevant documents
        documents = await retriever.retrieve(vector_store, query)

        # Build context
        context = context_builder.build_context(documents, query)

        return context


rag_pipeline = RAGPipeline()
