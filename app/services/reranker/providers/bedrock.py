import logging
from pydantic import SecretStr
from langchain_aws import BedrockRerank
from langchain_core.documents import Document
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from app.core.logs import get_logger
from app.core.config import settings
from app.services.reranker.base import RerankerProvider
from app.core.exceptions import RerankingProviderException

logger = get_logger()

class BedrockRerankerProvider(RerankerProvider):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
    )
    def create_instance(self, model_name: str, top_n: int, **kwargs) -> RerankerProvider:
        try:
            self._reranker = BedrockRerank(
                model_arn=f"arn:aws:bedrock:{settings.BEDROCK_RERANK_REGION}::foundation-model/{model_name}",
                top_n=top_n,
                region_name=settings.BEDROCK_RERANK_REGION,
                aws_access_key_id=SecretStr(settings.AWS_ACCESS_KEY),
                aws_secret_access_key=SecretStr(settings.AWS_SECRET_ACCESS_KEY),
            )
            return self
        except Exception as e:
            logger.error(f"Reranker failed due to :{e}")
            raise RerankingProviderException(
                message="Reranker failed",
                context={"detail": str(e)},
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
    )
    async def rerank(self, query: str, documents: list[Document]) -> list[Document]:
        try:
            logger.info(f"[RERANKING] Reranking query: {query}")
            result = await self._reranker.acompress_documents(documents, query)
            return list(result)
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            raise RerankingProviderException(
                message="Reranking failed",
                context={"detail": str(e)}
            )

