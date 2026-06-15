class AWSRAGException(Exception):
    def __init__(self, message: str, context: dict | None = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)

class IngestionFailedException(AWSRAGException):
    pass

class QueryFailedException(AWSRAGException):
    pass

class DatabaseFailedException(AWSRAGException):
    pass

class BedrockFailedException(AWSRAGException):
    pass

class DocumentNotFoundException(AWSRAGException):
    pass

class LLMProviderException(AWSRAGException):
    pass

class EmbeddingProviderException(AWSRAGException):
    pass

class RetrieverProviderException(AWSRAGException):
    pass

class ContentNotFoundException(AWSRAGException):
    pass

class DocstoreProviderException(AWSRAGException):
    pass

class RerankingProviderException(AWSRAGException):
    pass