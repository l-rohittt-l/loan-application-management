"""
Runs around every request.

  1. Makes a request id, or reuses the one the caller sent in X-Request-ID.
  2. Binds request_id, method and path so every log line in this request
     carries them (structlog contextvars).
  3. Logs request_started, times the work, logs request_completed with the
     status code and duration_ms.
  4. Returns the id to the caller in the X-Request-ID response header.
  5. If anything crashes, logs the full stack trace with the request id and
     returns a clean 500 that quotes the id, so a user can report it and we
     can find the exact log lines.

The request id is a UUID, not a timestamp: two requests in the same
millisecond would otherwise share one (T-21).
"""

import time
import uuid

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:16]}"
    request.state.request_id = request_id   # read by activity_service.request_meta

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    start = time.perf_counter()
    logger.info("request_started")
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.error(
            "unhandled_exception",
            error_type=type(exc).__name__,
            error_message=str(exc),
            duration_ms=duration_ms,
            status="failure",
            exc_info=True,            # format_exc_info turns this into stack_trace
        )
        structlog.contextvars.clear_contextvars()
        return JSONResponse(
            status_code=500,
            content={"detail": "Something went wrong on our side. Quote this id when reporting it.",
                     "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )

    duration_ms = int((time.perf_counter() - start) * 1000)
    logger.info(
        "request_completed",
        status_code=response.status_code,
        duration_ms=duration_ms,
        status="success" if response.status_code < 400 else "failure",
    )
    response.headers["X-Request-ID"] = request_id
    structlog.contextvars.clear_contextvars()
    return response
