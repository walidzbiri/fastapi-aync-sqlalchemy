import json
import logging
import time
import traceback
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        # Ignore certain paths like openapi.json
        if request.url.path in ["/openapi.json", "/docs"]:
            return await call_next(request)


        start_time = time.perf_counter()

        # Read request body
        request_body_bytes = await request.body()
        try:
            request_body = request_body_bytes.decode("utf-8")
            try:
                request_body = json.loads(request_body)
            except json.JSONDecodeError:
                pass
        except Exception:
            request_body = "<unreadable>"

        # Clone request stream for downstream usage
        async def receive():
            return {"type": "http.request", "body": request_body_bytes}

        request._receive = receive  # allow downstream to read again

        response = None
        exception = None
        tb = None
        response_body = b""

        try:
            response = await call_next(request)

            # Read response body
            async for chunk in response.body_iterator:
                response_body += chunk

            # Recreate response
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        except Exception as exc:
            exception = str(exc)
            tb = traceback.format_exc()

            # Log the exception context here (before re-raising)
            duration = time.perf_counter() - start_time
            logger.error(
                "HTTP Request Exception Context Log",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "duration": f"{duration:.4f} seconds",
                    "request_body": request_body,
                    "client": request.client.host if request.client else "-",
                    "user_agent": request.headers.get("user-agent", "-"),
                    "exception": exception,
                    "traceback": tb,
                },
            )

            # Re-raise the exception so FastAPI exception handlers can process it
            raise exc

        # Log successful requests
        duration = time.perf_counter() - start_time
        logger.info(
            "HTTP Request Context Log",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "status_code": response.status_code if response else "N/A",
                "duration": f"{duration:.4f} seconds",
                "request_body": request_body,
                "response_body": self._safe_json(response_body),
                "client": request.client.host if request.client else "-",
                "user_agent": request.headers.get("user-agent", "-"),
            },
        )

        return response

    def _safe_json(self, body: bytes):
        try:
            decoded = body.decode("utf-8")
            return json.loads(decoded)
        except Exception:
            return decoded if decoded else "<empty>"
