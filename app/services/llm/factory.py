from typing import Type
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.logs import get_logger
from app.services.llm.base import LLMProvider
from app.core.exceptions import LLMProviderException
from app.services.llm.providers.bedrock import BedrockProvider

logger = get_logger()

class LLMFactory:
    """The dynamic registry system handling runtime LLM engine assignments."""

    _registry: dict[str, Type[LLMProvider]] = {
        'bedrock': BedrockProvider,
    }

    @classmethod
    def resolve(cls, provider_type: str, model_name: str, temperature: float, **kwargs) -> BaseChatModel:
        """
            This class method will be used everywhere to call
        :param provider_type:
        :param model_name:
        :param temperature:
        :param kwargs:
        :return:
        """
        provider_key = provider_type.lower().strip()

        if provider_key not in cls._registry:
            logger.error(f"LLM initialization error due to unknown provider {provider_key}")
            raise LLMProviderException(
                message="Kindly enter a valid llm provider",
                context={"details":f"Unknown llm provider:{provider_key}"},
            )

        logger.info(f"Initializing core LLM client engine -> Provider: {provider_key}, Model: {model_name}")
        return cls._registry[provider_key]().create_instance(model_name, temperature, **kwargs)
