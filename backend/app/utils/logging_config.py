"""
Structured logging: every log line is one line of JSON.

The observability guide requires these fields on every line:
  timestamp, level, poc_id, phase, associate_id
plus whatever the event itself adds (operation, duration_ms, status, ...).

The three identity fields come from the settings file and are stamped on by
a processor, so no piece of code has to remember them. Within a request,
the middleware binds request_id, method and path into "contextvars", and
`merge_contextvars` copies them onto every line logged during that request.
"""

import logging
import sys

import structlog

from app.config import settings


def _add_program_identity(logger, method_name, event_dict):
    """Stamp poc_id, phase and associate_id onto every log line."""
    event_dict.setdefault("poc_id", settings.poc_id)
    event_dict.setdefault("phase", settings.phase)
    event_dict.setdefault("associate_id", settings.associate_id)
    return event_dict


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,     # request_id, method, path
            structlog.stdlib.add_log_level,              # "level": "info"
            _add_program_identity,                       # poc_id, phase, associate_id
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,        # turns exc_info into a stack trace string
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,   # so tests that reconfigure still work
    )

    # Standard-library logging (uvicorn, sqlalchemy) prints through the same stream.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        force=True,
    )
    # SQLAlchemy is chatty at INFO; keep it to warnings unless debugging.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
