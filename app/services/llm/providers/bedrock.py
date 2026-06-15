import logging
from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import BaseChatModel
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from app.core.logs import get_logger
from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.core.exceptions import BedrockFailedException

logger = get_logger()

class BedrockProvider(LLMProvider):
    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
    )
    def create_instance(self, model_name: str, temperature: float, **kwargs) -> BaseChatModel:
        try:
            return ChatBedrockConverse(
                model=model_name,
                temperature=temperature,
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
        except Exception as e:
            logger.error(f"Bedrock failed due to : {e}")
            raise BedrockFailedException(
                message="Bedrock initialization failed",
                context={"details": str(e)}
            )