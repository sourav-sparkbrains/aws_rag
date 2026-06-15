import logging
from langchain_aws import BedrockEmbeddings
from langchain_core.embeddings import Embeddings
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from app.core.config import settings
from app.services.embeddings.base import EmbeddingsProvider

class TitanProvider(EmbeddingsProvider):
    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
    )
    def create_instance(self, model_name: str, **kwargs) -> Embeddings:
        return BedrockEmbeddings(
            model_id=model_name,
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )