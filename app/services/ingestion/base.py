from abc import ABC, abstractmethod
from langchain_core.documents import Document

class IngestionProvider(ABC):

    @abstractmethod
    def load(self, path: str) -> list[Document]:
        pass

    @abstractmethod
    def chunk(self, documents: list[Document]) -> tuple[list[Document], list[Document]]:
        pass