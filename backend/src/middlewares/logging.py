import time
import uuid

import logfire
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        with logfire.span(
            f"{request.method} {request.url.path}",
            request_id=request_id,
            http_method=request.method,
            http_url=str(request.url),
            http_user_agent=request.headers.get("user-agent"),
            user_id=request.headers.get("x-user-id"),
        ) as span:
            try:
                response = await call_next(request)

                process_time_ms = (time.perf_counter() - start_time) * 1000

                span.set_attribute("http_status_code", response.status_code)

                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"

                return response

            except Exception as e:
                process_time_ms = (time.perf_counter() - start_time) * 1000

                span.set_attribute("error", True)
                span.set_attribute("error_message", str(e))

                logfire.exception(
                    f"Error en request: {request.method} {request.url.path}",
                    error=str(e),
                    duration_ms=process_time_ms,
                )
                raise
