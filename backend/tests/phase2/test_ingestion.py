"""
Phase 2 ingestion tests, TC-01-P2-ING-01 to 04.

Taken from the trainer's phase2-test-spec.md. Two adaptations, both forced and
both documented next to the line that changes:

  * ING-02 imports the splitter from `langchain_text_splitters`. The spec's
    `from langchain.text_splitter import ...` path was removed in LangChain 1.x
    (T-53). Same class, same behaviour, different address.

  * ING-03 embeds with `models/gemini-embedding-001`. The spec names
    `models/text-embedding-004`, which Google has withdrawn (T-51). The model
    name is read from settings so it is not hardcoded twice.
"""

import chromadb
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from llm_provider import get_collection_name, get_embeddings

MANUAL = "rag/user_manual.md"


def test_document_loads_successfully():
    """TC-01-P2-ING-01: the user manual loads and is not empty."""
    loader = TextLoader(MANUAL, encoding="utf-8")
    documents = loader.load()

    assert len(documents) >= 1
    assert len(documents[0].page_content) > 100


def test_chunking_produces_correct_sizes():
    """TC-01-P2-ING-02: chunking gives at least 20 chunks, none oversized."""
    documents = TextLoader(MANUAL, encoding="utf-8").load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(documents)

    assert len(chunks) >= 20, f"Only {len(chunks)} chunks; the manual is too short"
    for chunk in chunks:
        assert len(chunk.page_content) <= 600, f"Chunk too large: {len(chunk.page_content)}"


def test_embeddings_generated():
    """TC-01-P2-ING-03: a chunk turns into a non-empty list of floats."""
    embeddings = get_embeddings()

    result = embeddings.embed_query(
        "The minimum CIBIL score for a personal loan is 650."
    )

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(x, float) for x in result)


def test_chromadb_persists_vectors(ingested):
    """TC-01-P2-ING-04: the collection survives on disk between runs."""
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_collection(get_collection_name())

    assert collection is not None
    count = collection.count()
    assert count > 0, "Collection empty — run `python -m rag.ingest` first"


def test_reingesting_does_not_duplicate(ingested):
    """
    Ours, not the trainer's. Chunks are stored under fixed ids (`chunk_0`,
    `chunk_1`, ...) so that running ingestion again overwrites the manual in
    place. Without that the collection quietly fills with duplicates and
    retrieval starts returning the same paragraph four times.
    """
    from rag.ingest import ingest_manual

    before = ingest_manual()
    after = ingest_manual()

    assert before == after, "Re-ingesting changed the count, so chunks are duplicating"
