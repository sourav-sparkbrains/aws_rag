from abc import ABC, abstractmethod
from langchain_core.embeddings import Embeddings

class EmbeddingsProvider(ABC):

    @abstractmethod
    def create_instance(self, model_name: str, **kwargs) -> Embeddings:
        pass