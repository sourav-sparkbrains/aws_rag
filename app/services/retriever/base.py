from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

class RetrieverProvider(ABC):

    @abstractmethod
    def create_instance(self, embeddings: Embeddings) -> "RetrieverProvider":
        pass

    @abstractmethod
    async def add_documents(self, documents: list[Document]) -> None:
        pass

    @abstractmethod
    async def asimilarity_search(self, query: str, k: int = 10) -> list[Document]:
        pass