from typing import Optional
from contextvars import ContextVar

request_id : ContextVar[Optional[str]] = ContextVar("request_id", default=None)
