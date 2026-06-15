import asyncio
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import APIRouter, Depends, Request

from app.core.config import settings
from app.core.logs import get_logger
from app.pipeline.ingestion_pipeline import IngestionPipeline
from app.core.dependencies import get_s3_client, get_ingestion_pipeline
from app.models.schemas import UploadUrlRequest, UploadUrlResponse, IngestRequest, IngestResponse

document_router = APIRouter(prefix="/documents", tags=["Upload File"])

logger = get_logger()
limiter = Limiter(key_func=get_remote_address)

@document_router.post("/upload_url", response_model=UploadUrlResponse)
@limiter.limit("10/minute")
async def upload_url(request: Request, upload_request: UploadUrlRequest, s3_client = Depends(get_s3_client))-> UploadUrlResponse:
    loop = asyncio.get_event_loop()
    s3_object_key = f"uploads/{upload_request.filename}"

    upload_file_url = await loop.run_in_executor(
        None,
        lambda: s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': settings.S3_BUCKET, 'Key': s3_object_key,'ContentType': 'application/pdf'},
            ExpiresIn=300
        )
    )
    return UploadUrlResponse(upload_url=upload_file_url, s3_key=s3_object_key)


@document_router.post("/ingest", response_model=IngestResponse)
@limiter.limit("5/minute")
async def ingest(request: Request,ingest_request: IngestRequest, ingestion: IngestionPipeline = Depends(get_ingestion_pipeline)) -> IngestResponse:
    s3_key = ingest_request.s3_key
    await ingestion.run(s3_key)
    return IngestResponse(message="Document ingested successfully", s3_key=s3_key)