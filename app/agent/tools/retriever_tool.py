import logging
from typing import Any
from langchain_core.tools import BaseTool
from langchain_core.documents import Document
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log


from app.core.logs import get_logger

logger = get_logger()

class RetrieverTool(BaseTool):
    name: str = "retriever"
    description: str = (
        "Use this tool to search and retrieve the most relevant information "
        "from the document knowledge base. Results are automatically reranked "
        "by relevance before being returned. Use this for any factual questions "
        "about the documents."
    )
    retriever: Any
    reranker: Any

    def _run(self, query: str) -> list[Document]:
        logger.info(f"[RETRIEVER TOOL] searching for: {query}")
        return self.retriever.similarity_search(query)

    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
    )
    async def _arun(self, query: str) -> list[Document]:
        logger.info(f"[RETRIEVER TOOL] async searching for: {query}")
        docs = await self.retriever.asimilarity_search(query, k = 10)
        return await self.reranker.rerank(query, docs)