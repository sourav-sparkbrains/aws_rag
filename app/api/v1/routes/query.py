from typing import Annotated
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import APIRouter, Depends, Request

from app.core.logs import get_logger
from app.core.dependencies import get_query_pipeline
from app.pipeline.query_pipeline import QueryPipeline
from app.models.schemas import QueryRequest, QueryResponse

query_router = APIRouter(prefix="/query", tags=["Query"])

logger = get_logger()
limiter = Limiter(key_func=get_remote_address)

@query_router.post("/ask", response_model=QueryResponse)
@limiter.limit("20/minute")
async def query_endpoint(request: Request, query_request: QueryRequest, pipeline: QueryPipeline = Depends(get_query_pipeline)) -> QueryResponse:
    result = await pipeline.run(
        query=query_request.query,
        session_id=query_request.session_id
    )
    return QueryResponse(
        answer=result["answer"],
        session_id=result["session_id"],
        sources=result["sources"]
    )



