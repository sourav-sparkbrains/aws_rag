from typing import Optional
from pydantic import BaseModel

class UploadUrlRequest(BaseModel):
    filename: str

class UploadUrlResponse(BaseModel):
    upload_url: str
    s3_key: str

class IngestRequest(BaseModel):
    s3_key: str

class IngestResponse(BaseModel):
    message: str
    s3_key: str

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    sources: list[str]
