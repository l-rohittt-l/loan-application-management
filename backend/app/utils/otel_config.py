"""
OpenTelemetry: timed, labelled steps called "spans".

Phase 1 must produce three span names (TECH_STACK_REFERENCE section 8.4):
  http.request   one per request, made automatically by FastAPIInstrumentor
  db.query       one per database statement, made here by hooking SQLAlchemy
  auth.validate  one per token check, made in dependencies.py

Spans print to the console when OTEL_EXPORTER=console, which is what the
program wants to see. OTEL_EXPORTER=none switches them off for tests.
"""

import time

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.config import settings

_configured = False


def setup_telemetry() -> trace.Tracer:
    """Set up the tracer once. Safe to call more than once."""
    global _configured
    if not _configured:
        resource = Resource.create({
            "service.name": settings.otel_service_name,
            "poc.id": settings.poc_id,
            "poc.phase": str(settings.phase),
        })
        provider = TracerProvider(resource=resource)
        if settings.otel_exporter.lower() == "console":
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        _configured = True
    return trace.get_tracer(settings.otel_service_name)


def get_tracer() -> trace.Tracer:
    return trace.get_tracer(settings.otel_service_name)


def instrument_sqlalchemy(engine: Engine) -> None:
    """
    Open a `db.query` span around every SQL statement. Uses SQLAlchemy's
    cursor events, so every query anywhere in the app is covered without
    touching the services.
    """
    tracer = get_tracer()

    @event.listens_for(engine, "before_cursor_execute")
    def _before(conn, cursor, statement, parameters, context, executemany):
        span = tracer.start_span("db.query")
        span.set_attribute("db.system", "sqlite")
        span.set_attribute("db.operation", statement.split(None, 1)[0].upper() if statement else "")
        span.set_attribute("db.statement", statement[:200])   # trimmed: no giant statements in traces
        # Stash the span and start time on the connection so `_after` can find them.
        conn.info["otel_span"] = span
        conn.info["otel_start"] = time.perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def _after(conn, cursor, statement, parameters, context, executemany):
        span = conn.info.pop("otel_span", None)
        start = conn.info.pop("otel_start", None)
        if span is not None:
            if start is not None:
                span.set_attribute("db.duration_ms", int((time.perf_counter() - start) * 1000))
            span.end()
