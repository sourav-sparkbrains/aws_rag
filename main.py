from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


from app.core.config import settings
from app.core.logs import get_logger
from app.core.exceptions import AWSRAGException
from app.api.v1.routes.query import query_router
from app.api.v1.routes.documents import document_router
from app.core.middleware import timer_middleware, request_middleware
from app.core.dependencies import (
    get_llm,get_embeddings,get_retriever,get_docstore,get_ingestion,get_agent
)

logger = get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    get_llm()
    get_embeddings()
    get_retriever()
    get_docstore()
    get_ingestion()
    get_agent()
    logger.info("All services initialized")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.APP_DEBUG,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)
app.add_middleware(BaseHTTPMiddleware, dispatch=timer_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=request_middleware)

app.include_router(
    document_router,
    prefix=f"/api/{settings.API_VERSION}",
)

app.include_router(
    query_router,
    prefix=f"/api/{settings.API_VERSION}",
)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.APP_ENV}

@app.exception_handler(AWSRAGException)
async def rag_exception_handler(request: Request, exc: AWSRAGException):
    return JSONResponse(
        content={"detail": exc.message, "context": exc.context},
        status_code=400
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        content={"detail": "Internal server error"},
        status_code=500
    )