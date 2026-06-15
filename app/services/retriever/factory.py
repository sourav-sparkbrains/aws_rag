from typing import Type
from langchain_core.embeddings  import Embeddings

from app.core.logs import get_logger
from app.services.retriever.base import RetrieverProvider
from app.core.exceptions import RetrieverProviderException
from app.services.retriever.providers.chromadb import ChromaDBProvider

logger = get_logger()

class RetrieverFactory:

    _registry: dict[str, Type[RetrieverProvider]] = {
        'chromadb': ChromaDBProvider,
    }

    @classmethod
    def resolve(cls, provider_type: str, embeddings: Embeddings) -> RetrieverProvider:
        """
            This class method will be used everywhere to call retriever
        :param provider_type:
        :param embeddings:
        :return:
        """

        provider_key = provider_type.lower().strip()

        if provider_key not in cls._registry:
            logger.error(f"Retriever initialization error due to unknown provider {provider_key}")
            raise RetrieverProviderException(
                message="Kindly enter a valid retriever provider",
                context={"details": f"Unknown retriever provider: {provider_key}"},
            )

        logger.info(f"Initializing core retriever client engine -> Provider: {provider_key}")
        provider = cls._registry[provider_key]()
        provider.create_instance(embeddings)
        return provider