from abc import ABC, abstractmethod
from langchain_core.documents import Document


class RerankerProvider(ABC):

    @abstractmethod
    def create_instance(self, model_name: str, top_n: int, **kwargs) -> "RerankerProvider":
        pass

    @abstractmethod
    async def rerank(self, query: str, documents: list[Document]) -> list[Document]:
        pass