"""
Middleware for correlation ID tracking across requests.
"""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import set_correlation_id


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures every request has a correlation ID.

    - Reads X-Correlation-ID header if present
    - Generates new ID if not present
    - Sets ID in context for logging
    - Adds ID to response headers
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Set in context for logging
        set_correlation_id(correlation_id)

        # Process request
        response = await call_next(request)

        # Add to response headers for client tracking
        response.headers["X-Correlation-ID"] = correlation_id

        return response
