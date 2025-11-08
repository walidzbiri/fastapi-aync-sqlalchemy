import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

# Context variable to store correlation ID across async calls
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="NaN")


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records"""

    def filter(self, record: logging.LogRecord):
        record.correlation_id = correlation_id_ctx.get("NaN")
        return True


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", ""),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "correlation_id",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


def setup_logging(app_level="INFO", sql_level="WARNING"):
    json_formatter = JSONFormatter()
    correlation_filter = CorrelationIdFilter()

    # Global handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(json_formatter)
    handler.addFilter(correlation_filter)

    # Root logger
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(app_level)

    def configure_logger(name: str, level: str, propagate=False):
        logger = logging.getLogger(name)
        logger.handlers = []  # remove default handlers
        logger.setLevel(level)
        logger.propagate = propagate
        # No filters on loggers; handler already has filter
        return logger

    # Uvicorn loggers
    configure_logger("uvicorn", app_level, propagate=True)
    configure_logger("uvicorn.error", app_level, propagate=True)
    configure_logger("uvicorn.access", app_level, propagate=True)

    # SQLAlchemy
    configure_logger("sqlalchemy.engine", sql_level, propagate=True)
