from typing import Any
from abc import ABC, abstractmethod
from langchain_core.documents import Document

class DocstoreProvider(ABC):

    @abstractmethod
    def create_instance(self) -> Any:
        pass

    @abstractmethod
    async def store_parents(self, document: list[Document]) -> None:
        pass

    @abstractmethod
    async def fetch_parent(self, parent_id: str) -> Document:
        pass
