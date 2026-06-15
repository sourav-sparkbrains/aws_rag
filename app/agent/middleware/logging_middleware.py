from typing import Any
from langgraph.runtime import Runtime
from langchain.agents.middleware import AgentMiddleware, AgentState

from app.core.logs import get_logger

logger = get_logger()

class LoggingMiddleware(AgentMiddleware):

    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        logger.info(f"[AGENT] Starting with: {state['messages'][-1].content}")
        return None

    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        logger.info(f"[AGENT] Calling model, message count: {len(state['messages'])}")
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        logger.info(f"[AGENT] Model responded: {str(state['messages'][-1].content)[:100]}")
        return None

    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        logger.info(f"[AGENT] Completed")
        return None