"""RAG Pipeline Orchestration"""

from app.rag.retriever import retriever
from app.rag.context_builder import context_builder


class RAGPipeline:
    async def run(self, query: str):
        # Retrieve relevant documents
        documents = await retriever.retrieve(query)

        # Build context
        context = context_builder.build_context(documents, query)

        return context


rag_pipeline = RAGPipeline()
