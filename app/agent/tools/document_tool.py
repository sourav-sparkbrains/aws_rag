import logging
from typing import Any
from langchain_core.tools import BaseTool
from langchain_core.documents import Document
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from app.core.logs import get_logger

logger = get_logger()

class DocumentTool(BaseTool):
    name: str = "document"
    description: str = (
        "Fetch the full parent document from the knowledge base using a parent_id."
        "Use when retrieved chunks need more context."
    )

    docstore: Any

    def _run(self, parent_id: str) -> Document:
        raise NotImplementedError("Use async version")

    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
    )
    async def _arun(self, parent_id: str) -> Document:
        logger.info(f"[DOCUMENT TOOL] async fetching for: {parent_id}")
        return await self.docstore.fetch_parent(parent_id)