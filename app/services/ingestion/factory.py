from typing import Type

from app.core.logs import get_logger
from app.services.ingestion.base import IngestionProvider
from app.core.exceptions import IngestionFailedException
from app.services.ingestion.providers.pdf import PDFIngestionProvider

logger = get_logger()

class IngestionFactory:
    """The dynamic registry system handling runtime Ingestion engine assignments."""

    _registry: dict[str, Type[IngestionProvider]] = {
        'pdf': PDFIngestionProvider,
    }

    @classmethod
    def resolve(cls, provider_type: str, **kwargs) -> IngestionProvider:
        """
            This class method will be used everywhere to call ingestion
        :param provider_type:
        :param kwargs:
        :return:
        """
        provider_key = provider_type.lower().strip()

        if provider_key not in cls._registry:
            logger.error(f"Ingestion initialization error due to unknown provider {provider_key}")
            raise IngestionFailedException(
                message="Kindly enter a valid ingestion provider",
                context={"details":f"Unknown ingestion provider:{provider_key}"},
            )

        logger.info(f"Initializing core ingestion client engine -> Provider: {provider_key}")
        return cls._registry[provider_key]()