from typing import Any
from langchain_core.tools import BaseTool

from app.core.logs import get_logger

logger = get_logger()

class SummarizerTool(BaseTool):
    name: str = "summarizer"
    description: str = (
        "Summarize a long document or multiple chunks into a concise response. "
        "Use when the content is too long or user explicitly asks for a summary."
    )

    llm: Any

    def _run(self, content: str) -> str:
        raise NotImplementedError("Use async version")

    async def _arun(self, content: str) -> str:
        logger.info(f"[SUMMARIZER TOOL] summarizing content...")
        from langchain_core.messages import HumanMessage
        response = await self.llm.ainvoke([
            HumanMessage(content=f"Summarize the following content concisely:\n\n{content}")
        ])
        return response.content