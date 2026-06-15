from typing import Type

from app.core.logs import get_logger
from app.services.docstore.base import DocstoreProvider
from app.core.exceptions import DocstoreProviderException
from app.services.docstore.providers.dynamodb import DynamoDBProvider

logger = get_logger()

class DocstoreFactory:

    _registry: dict[str, Type[DocstoreProvider]] = {
        'dynamodb': DynamoDBProvider,
    }

    @classmethod
    def resolve(cls, provider_type: str) -> DocstoreProvider:
        provider_key = provider_type.lower().strip()

        if provider_key not in cls._registry:
            logger.error(f"Docstore initialization error due to unknown provider {provider_key}")
            raise DocstoreProviderException(
                message="Kindly enter a valid docstore provider",
                context={"details": f"Unknown docstore provider: {provider_key}"},
            )

        logger.info(f"Initializing docstore -> Provider: {provider_key}")
        return cls._registry[provider_key]().create_instance()