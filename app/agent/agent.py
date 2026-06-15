from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph

from app.agent.tools.retriever_tool import RetrieverTool
from app.agent.tools.document_tool import DocumentTool
from app.agent.tools.summarizer_tool import SummarizerTool
from app.agent.prompts.system_prompt import RAG_SYSTEM_PROMPT
from app.agent.middleware.logging_middleware import LoggingMiddleware


def create_rag_agent(llm, retriever, docstore, reranker, memory) -> CompiledStateGraph:
    tools = [
        RetrieverTool(retriever=retriever, reranker=reranker),
        DocumentTool(docstore=docstore),
        SummarizerTool(llm=llm),
    ]

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=RAG_SYSTEM_PROMPT,
        middleware=[LoggingMiddleware()],
        checkpointer=memory,
    )