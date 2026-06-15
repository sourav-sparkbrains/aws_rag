import inspect
import logging
from pathlib import Path

from app.core.config import settings
from app.core.context import request_id

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id.get() or "no-request-id"
        return True

def _configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.addFilter(RequestIDFilter())

    logging.basicConfig(
        level=logging.DEBUG if settings.APP_DEBUG else logging.WARNING,
        format=f"%(asctime)s - %(request_id)s - {settings.APP_NAME} - %(name)s - %(levelname)s - %(lineno)d - %(message)s",
        force=True,
        handlers=[handler],
    )

def get_logger() -> logging.Logger:
    frame = inspect.stack()[1]
    try:
        file_path = Path(frame[1]).relative_to(Path.cwd()).with_suffix('')
        name = '.'.join(file_path.parts)
    except ValueError:
        name = Path(frame[1]).stem
    return logging.getLogger(name)

_configure_logging()