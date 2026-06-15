from typing import Type

from app.core.logs import get_logger
from app.services.reranker.base import RerankerProvider
from app.core.exceptions import RerankingProviderException
from app.services.reranker.providers.bedrock import BedrockRerankerProvider

logger = get_logger()

class RerankerFactory:
    """The dynamic registry system handling runtime rerank engine assignments."""

    _registry: dict[str, Type[RerankerProvider]] = {
        'bedrock': BedrockRerankerProvider,
    }

    @classmethod
    def resolve(cls, provider_type: str, model_name: str, top_n: int, **kwargs) -> RerankerProvider:
        """
            This class method will be used everywhere to call
        :param provider_type:
        :param model_name:
        :param top_n:
        :param kwargs:
        :return:
        """
        provider_key = provider_type.lower().strip()

        if provider_key not in cls._registry:
            logger.error(f"Reranker initialization error due to unknown provider {provider_key}")
            raise RerankingProviderException(
                message="Kindly enter a valid rerank provider",
                context={"details":f"Unknown rerank provider:{provider_key}"},
            )

        logger.info(f"Initializing core rerank client engine -> Provider: {provider_key}, Model: {model_name}")
        return cls._registry[provider_key]().create_instance(model_name, top_n, **kwargs)
