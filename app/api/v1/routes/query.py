from typing import Annotated
from fastapi import APIRouter, Depends

from app.core.logs import get_logger
from app.core.dependencies import get_query_pipeline
from app.pipeline.query_pipeline import QueryPipeline
from app.models.schemas import QueryRequest, QueryResponse

query_router = APIRouter(prefix="/query", tags=["Query"])

logger = get_logger()

@query_router.post("/ask", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest, pipeline: QueryPipeline = Depends(get_query_pipeline)) -> QueryResponse:
    result = await pipeline.run(
        query=request.query,
        session_id=request.session_id
    )
    return QueryResponse(
        answer=result["answer"],
        session_id=result["session_id"],
        sources=result["sources"]
    )



