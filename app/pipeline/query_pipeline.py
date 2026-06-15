from uuid import uuid4

from app.core.logs import get_logger
from app.core.exceptions import QueryFailedException

logger = get_logger()


class QueryPipeline:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, query: str, session_id: str | None) -> dict:
        logger.info("[QUERY] starting the query pipeline...")

        session_id = session_id or str(uuid4())

        thread_config = {
            "configurable": {"thread_id": session_id},
        }

        try:
            response = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": query}]},
                thread_config
            )

            messages = response["messages"]
            last_message = messages[-1]

            if isinstance(last_message.content, str):
                answer = last_message.content
            else:
                answer = ""
                for block in last_message.content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        answer = block["text"]
                        break

            sources = []
            for msg in messages:
                if hasattr(msg, 'name') and msg.name == 'retriever':
                    sources.append(msg.content)

            logger.info("[QUERY] query pipeline is completed")

            return {
                "answer": answer,
                "session_id": session_id,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"[QUERY] pipeline failed: {e}")
            raise QueryFailedException(
                message="Query failed",
                context={"query": query, "error": str(e)}
            )

