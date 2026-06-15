import json
import boto3
import asyncio
import logging
from typing import Any
from langchain_core.documents import Document
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from app.core.config import settings
from app.core.logs import get_logger
from app.services.docstore.base import DocstoreProvider
from app.core.exceptions import DocumentNotFoundException, DatabaseFailedException

logger = get_logger()

class DynamoDBProvider(DocstoreProvider):

    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
    )
    def create_instance(self) -> Any:
        try:
            self._client = boto3.client(
                'dynamodb',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            return self

        except Exception as e:
            logger.error(f"Database failed due to: {e}")
            raise DatabaseFailedException(
                message="DynamoDB operation failed",
                context={"details": str(e)}
            )


    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
    )
    async def store_parents(self, documents: list[Document]) -> None:
        loop = asyncio.get_event_loop()
        for i in range(0, len(documents), 25):
            batch = documents[i:i + 25]
            await loop.run_in_executor(
                None,
                lambda: self._client.batch_write_item(
                RequestItems={
                    settings.DYNAMODB_TABLE_NAME: [
                        {
                            'PutRequest': {
                                'Item': {
                                    'parent_id': {'S': doc.metadata.get('parent_id')},
                                    'content': {'S': doc.page_content},
                                    'metadata': {'S': json.dumps(doc.metadata)},
                                }
                            }
                        }
                        for doc in batch
                    ]
                }
            ))
        logger.info("Parent documents stored in DynamoDB")


    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
    )
    async def fetch_parent(self, parent_id: str) -> Document:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.get_item(
                TableName=settings.DYNAMODB_TABLE_NAME,
                Key={'parent_id': {'S': parent_id}}
            )
        )
        item = response.get('Item')
        if not item:
            logger.error("Parent document not found")
            raise DocumentNotFoundException(
                message="Parent document not found",
                context={"parent_id": parent_id}
            )
        return Document(
            page_content=item['content']['S'],
            metadata=json.loads(item['metadata']['S'])
        )
