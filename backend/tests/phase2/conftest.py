"""
Shared setup for the Phase 2 tests.

Two things matter here.

**The chain is built once for the whole file.** Building it is not free, and
every generation test would otherwise make its own connection. More importantly
the free tier allows only a handful of requests a minute (T-55), so we make as
few calls as we can get away with.

**Ingestion runs once, if it needs to.** The trainer's note says "always run
ingest.py before running tests". Rather than rely on remembering, the fixture
checks whether the collection already holds anything and ingests only if it is
empty. That makes `pytest tests/phase2/` work from a clean clone.
"""

import os

import pytest

# Spans off by default so the test output stays readable. The one test that
# checks span output turns them back on for itself.
os.environ.setdefault("OTEL_EXPORTER", "none")


@pytest.fixture(scope="session")
def ingested():
    """Make sure the manual is in ChromaDB before any retrieval or generation test."""
    import chromadb

    from app.config import settings
    from llm_provider import get_collection_name

    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    try:
        count = client.get_collection(get_collection_name()).count()
    except Exception:
        count = 0

    if count == 0:
        from rag.ingest import ingest_manual

        count = ingest_manual()
    return count


@pytest.fixture(scope="session")
def rag(ingested):
    """The built chain and retriever, shared by every test that needs them."""
    from rag.rag_chain import build_rag_chain

    chain, retriever = build_rag_chain()
    return chain, retriever


@pytest.fixture(scope="session")
def chain(rag):
    return rag[0]


@pytest.fixture(scope="session")
def retriever(rag):
    return rag[1]
