from abc import ABC, abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel

class LLMProvider(ABC):

    @abstractmethod
    def create_instance(self, model_name: str, temperature: float, **kwargs) -> BaseChatModel:
        pass
