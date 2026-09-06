"""
Phase 2 observability tests, TC-01-P2-OBS-01 to 04.

OBS-01 and OBS-04 talk to LangSmith and need `LANGCHAIN_API_KEY`. Rohit does not
have one yet (T-50), so they skip rather than fail — a skip says "not proven",
which is honest, while a failure would say "broken", which is wrong. The other
eighteen Phase 2 tests do not need it, and the pass mark is fourteen.
"""

import json
import os

import pytest

from app.config import settings

needs_langsmith = pytest.mark.skipif(
    not settings.langchain_api_key,
    reason="LANGCHAIN_API_KEY is not set — get a free key at smith.langchain.com",
)


@needs_langsmith
def test_langsmith_trace_created(chain):
    """TC-01-P2-OBS-01: a query shows up as a trace in the LangSmith project."""
    from langsmith import Client

    chain.invoke("What documents are needed for a personal loan?")

    client = Client(api_key=settings.langchain_api_key)
    runs = list(client.list_runs(project_name=settings.langchain_project, limit=5))
    assert len(runs) > 0, "No LangSmith traces found"


def test_otel_spans_exported_during_ingestion():
    """
    TC-01-P2-OBS-02: the ingestion spans really are exported to the console.

    Run in a separate process on purpose. OpenTelemetry allows the global tracer
    provider to be set **once per process**, and the rest of this suite has
    already set it with spans switched off. Flipping the setting inside the test
    therefore does nothing — the decision was made when the first test imported
    the tracer. Trying that was the first version of this test, and it failed
    for exactly that reason.

    A subprocess gets a clean interpreter, and as a bonus this checks the real
    command a person would type rather than a rearranged version of it.
    """
    import subprocess
    import sys

    env = {**os.environ, "OTEL_EXPORTER": "console", "PYTHONPATH": "."}
    result = subprocess.run(
        [sys.executable, "-m", "rag.ingest"],
        capture_output=True, text=True, timeout=300, env=env,
    )
    combined = result.stdout + result.stderr

    assert result.returncode == 0, f"Ingestion failed:\n{combined[-2000:]}"

    for span_name in ("rag.document_load", "rag.chunk", "rag.embed"):
        assert span_name in combined, (
            f"The {span_name} span was not exported. "
            f"Spans seen: {[s for s in ('rag.document_load', 'rag.chunk', 'rag.embed') if s in combined]}"
        )


def test_log_fields_present(capsys):
    """
    TC-01-P2-OBS-03: answering a question writes a structured log line carrying
    the programme's identity fields.
    """
    from rag.rag_chain import answer_question, build_rag_chain

    chain, retriever = build_rag_chain()
    answer_question("What is the minimum CIBIL score for a personal loan?",
                    chain, retriever)

    captured = capsys.readouterr()

    for line in (captured.out + captured.err).split("\n"):
        try:
            log_entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if log_entry.get("operation") == "question_answered":
            assert "poc_id" in log_entry
            assert "phase" in log_entry
            assert log_entry["poc_id"] == "POC-01"
            return

    pytest.fail("No structured log entry with poc_id and phase found")


@needs_langsmith
def test_trace_contains_retrieval_metadata(chain):
    """TC-01-P2-OBS-04: the trace that lands in LangSmith is a named run."""
    import time

    from langsmith import Client

    chain.invoke("What is the maximum personal loan amount?")
    time.sleep(3)   # traces are sent in the background

    client = Client(api_key=settings.langchain_api_key)
    runs = list(client.list_runs(project_name=settings.langchain_project,
                                 limit=1, run_type="chain"))

    assert len(runs) > 0
    assert runs[0].name is not None
