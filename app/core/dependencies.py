import boto3
from functools import lru_cache
from langgraph.checkpoint.memory import InMemorySaver

from app.core.config import settings
from app.agent.agent import create_rag_agent
from app.services.llm.factory import LLMFactory
from app.pipeline.query_pipeline import QueryPipeline
from app.services.docstore.factory import DocstoreFactory
from app.services.reranker.factory import RerankerFactory
from app.services.ingestion.factory import IngestionFactory
from app.services.retriever.factory import RetrieverFactory
from app.services.embeddings.factory import EmbeddingsFactory
from app.pipeline.ingestion_pipeline import IngestionPipeline

#INGESTION PIPELINE

@lru_cache()
def get_llm():
    return LLMFactory.resolve(
        provider_type=settings.LLM_PROVIDER,
        model_name=settings.BEDROCK_MODEL_ID,
        temperature=settings.BEDROCK_TEMPERATURE,
    )

@lru_cache()
def get_embeddings():
    return EmbeddingsFactory.resolve(
        provider_type=settings.EMBEDDING_PROVIDER,
        model_name=settings.BEDROCK_EMBEDDING_MODEL_ID
    )

@lru_cache()
def get_retriever():
    embeddings = get_embeddings()
    return RetrieverFactory.resolve(
        provider_type=settings.RETRIEVER_PROVIDER,
        embeddings=embeddings
    )

@lru_cache()
def get_docstore():
    return DocstoreFactory.resolve(
        provider_type=settings.DOCSTORE_PROVIDER,
    )

@lru_cache()
def get_ingestion():
    return IngestionFactory.resolve(
        provider_type=settings.INGESTION_PROVIDER
    )

@lru_cache()
def get_s3_client():
    return boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
@lru_cache()
def get_ingestion_pipeline():
    return IngestionPipeline(
        ingestion=get_ingestion(),
        retrieval=get_retriever(),
        docstore=get_docstore(),
        s3_client=get_s3_client()
    )


#QUERY PIPELINE

@lru_cache()
def get_memory():
    return InMemorySaver()

@lru_cache()
def get_reranker():
    return RerankerFactory.resolve(
        provider_type=settings.RERANKER_PROVIDER,
        model_name=settings.BEDROCK_RERANK_MODEL,
        top_n=settings.RERANK_TOP_N
    )

@lru_cache()
def get_agent():
    return create_rag_agent(
        llm=get_llm(),
        retriever=get_retriever(),
        docstore=get_docstore(),
        reranker=get_reranker(),
        memory=get_memory()
    )

@lru_cache()
def get_query_pipeline():
    return QueryPipeline(agent=get_agent())