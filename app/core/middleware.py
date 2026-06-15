import time
import uuid
from fastapi import Request

from app.core.logs import get_logger
from app.core.context import request_id

logger = get_logger()

async def timer_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} took {duration:.2f}s")
    response.headers["X-Process-Time"] = str(duration)
    return response

async def request_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = request_id.set(req_id)
    try:
        response = await call_next(request)
        response.headers["X-Process-ID"] = req_id
        return response
    finally:
        request_id.reset(token)