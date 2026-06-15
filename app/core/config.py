from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # AWS Secrets
    AWS_ACCESS_KEY: str = Field(...)
    AWS_SECRET_ACCESS_KEY: str = Field(...)
    AWS_REGION: str = Field(default='us-east-1')

    #Bedrock Configurations
    BEDROCK_MODEL_ID: str = Field(default="us.meta.llama3-3-70b-instruct-v1:0")
    BEDROCK_TEMPERATURE: float = Field(default=0.0)
    BEDROCK_EMBEDDING_MODEL_ID: str = Field(default="amazon.titan-embed-text-v2:0")

    #Reranker Configuration
    BEDROCK_RERANK_MODEL: str = Field(default="amazon.rerank-v1:0")
    BEDROCK_RERANK_REGION: str = Field(default="us-west-2")
    RERANK_TOP_N: int = Field(default=3)

    #DynamoDB Configuration
    DYNAMODB_TABLE_NAME: str = Field(default="rag-parent-docs")

    #s3 Configuration
    S3_BUCKET: str = Field(default="rag-documents-bucket")

    #ChormaDB Configuration
    CHROMA_HOST: str = Field(default="localhost")
    CHROMA_PORT: int = Field(default=8080)
    CHROMA_COLLECTION: str = Field(default="AWSRAG")

    #Langfuse Configuration
    LANGFUSE_SECRET_KEY: str = Field(...)
    LANGFUSE_PUBLIC_KEY: str = Field(...)
    LANGFUSE_BASE_URL: str = Field(default="https: // cloud.langfuse.com")

    #App Configurations
    APP_NAME: str = Field(default="AWS_RAG")
    APP_ENV: str = Field(default='development')
    APP_DEBUG: bool = Field(default=False)
    APP_VERSION: str = Field(default='0.1.0')
    API_VERSION: str = Field(default='v1')
    LLM_PROVIDER: str = Field(default='bedrock')
    EMBEDDING_PROVIDER: str = Field(default='titan')
    RETRIEVER_PROVIDER: str = Field(default='chromadb')
    DOCSTORE_PROVIDER: str = Field(default='dynamodb')
    INGESTION_PROVIDER: str = Field(default='pdf')
    RERANKER_PROVIDER: str = Field(default="bedrock")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive = False,
        extra="ignore"
    )

settings = Settings()