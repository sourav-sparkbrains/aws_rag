import asyncio
import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.core.logs import get_logger
from app.core.config import settings
from app.core.exceptions import DatabaseFailedException
from app.services.retriever.base import RetrieverProvider

logger = get_logger()

class ChromaDBProvider(RetrieverProvider):

    def create_instance(self, embeddings: Embeddings) -> RetrieverProvider:
        try:
            client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
            self._store = Chroma(
                client=client,
                collection_name=settings.CHROMA_COLLECTION,
                embedding_function=embeddings,
            )
            return self

        except Exception as e:
            logger.error(f"Database failed due to: {e}")
            raise DatabaseFailedException(
                message="ChromaDB connection failed",
                context={"details": str(e)}
            )

    async def add_documents(self, documents: list[Document]) -> None:
        await self._store.aadd_documents(documents)

    async def asimilarity_search(self, query: str, k: int = 3) -> list[Document]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._store.similarity_search(query, k=k)
        )
