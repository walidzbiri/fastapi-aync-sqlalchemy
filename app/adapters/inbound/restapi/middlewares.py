import logging
import uuid

from starlette.types import ASGIApp, Receive, Scope, Send

from app.adapters.inbound.restapi.logging_config import correlation_id_ctx

logger = logging.getLogger(__name__)


class CorrelationIdMiddleware:
    """Raw ASGI middleware to add correlation ID to each request"""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Get or generate correlation ID
        headers = dict(scope.get("headers", []))
        correlation_id = headers.get(b"x-correlation-id", b"").decode("utf-8")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Set in context var for logging
        correlation_id_ctx.set(correlation_id)

        # Store in scope for access in routes
        scope["state"] = getattr(scope, "state", {})
        scope["state"]["correlation_id"] = correlation_id

        # Wrap send to add correlation ID to response headers
        async def send_with_correlation_id(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-correlation-id", correlation_id.encode("utf-8")))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_correlation_id)
