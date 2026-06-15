import asyncio
from pathlib import Path

from app.core.logs import get_logger
from app.core.config import settings
from app.services.docstore.base import DocstoreProvider
from app.core.exceptions import IngestionFailedException
from app.services.ingestion.base import IngestionProvider
from app.services.retriever.base import RetrieverProvider

logger = get_logger()

class IngestionPipeline:

    def __init__(
        self,
        ingestion: IngestionProvider,
        retrieval: RetrieverProvider,
        docstore: DocstoreProvider,
        s3_client,
    ):
        self.ingestion = ingestion
        self.retrieval = retrieval
        self.docstore = docstore
        self.s3_client = s3_client

    async def run(self, s3_key: str) -> None:

        logger.info("Initializing Ingestion pipeline...")
        local_path = f"/tmp/{s3_key.split('/')[-1]}"

        logger.info(f"[INGESTION] ingesting the {local_path} file...")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.s3_client.download_file(
                settings.S3_BUCKET,
                s3_key,
                local_path
            )
        )

        try:
            documents = self.ingestion.load(local_path)
            parent_documents, child_documents = self.ingestion.chunk(documents)
            await self.docstore.store_parents(parent_documents)
            await self.retrieval.add_documents(child_documents)
        except Exception as e:
            logger.error(f"[INGESTION] pipeline failed: {e}")
            raise IngestionFailedException(
                message="Document ingestion failed",
                context={"s3_key": s3_key, "error": str(e)}
            )
        finally:
            Path(local_path).unlink(missing_ok=True)
            logger.info(f"[INGESTION] cleaned up temp file {local_path}")
            logger.info("[INGESTION] services is completed")






