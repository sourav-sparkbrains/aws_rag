from typing import Type
from langchain_core.embeddings import Embeddings

from app.core.logs import get_logger
from app.core.exceptions import EmbeddingProviderException
from app.services.embeddings.base import EmbeddingsProvider
from app.services.embeddings.providers.titan import TitanProvider

logger = get_logger()

class EmbeddingsFactory:

    _registry: dict[str, Type[EmbeddingsProvider]] = {
        'titan' : TitanProvider,
    }

    @classmethod
    def resolve(cls, provider_type: str, model_name: str, **kwargs) -> Embeddings:
        """
            This class method will be used everywhere to call embeddings
        :param provider_type:
        :param model_name:
        :param kwargs:
        :return:
        """

        provider_key = provider_type.lower().strip()

        if provider_key not in cls._registry:
            logger.error(f"Embedding model initialization error due to unknown provider {provider_key}")
            raise EmbeddingProviderException(
                message=f"Kindly enter a valid embedding provider",
                context={"details": f"Invalid embedding provider:{provider_key}"},
            )

        logger.info(f"Initializing core embedding client engine -> Provider: {provider_key}, Model: {model_name}")
        return cls._registry[provider_key]().create_instance(model_name, **kwargs)

