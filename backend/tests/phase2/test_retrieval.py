"""
Phase 2 retrieval tests, TC-01-P2-RET-01 to 06.

These use the retriever from our own `build_rag_chain()` rather than building a
fresh one, so they test the code the app actually runs.
"""

import time

from app.config import settings


def test_relevant_chunk_retrieved_for_doc_query(retriever):
    """TC-01-P2-RET-01: a document question retrieves document-related text."""
    docs = retriever.invoke("What documents are required for a home loan?")

    combined_text = " ".join(doc.page_content.lower() for doc in docs)
    assert any(term in combined_text for term in
               ["id_proof", "income_proof", "property", "bank_statement"])


def test_top_k_returns_k_results(retriever):
    """TC-01-P2-RET-02: exactly TOP_K_RESULTS chunks come back."""
    docs = retriever.invoke("loan application status")

    assert len(docs) == settings.top_k_results


def test_irrelevant_query_low_similarity(retriever):
    """
    TC-01-P2-RET-03: an out-of-scope question does not retrieve out-of-scope text.

    The retriever always returns its top k — that is how a vector search works,
    it has no notion of "nothing matched". What this proves is that the chunks
    it returns are still loan chunks, so the generation step is refusing based
    on genuinely irrelevant context rather than on invented content.
    """
    docs = retriever.invoke("What is the best recipe for pasta carbonara?")

    combined = " ".join(doc.page_content.lower() for doc in docs)
    assert "pasta" not in combined
    assert "recipe" not in combined
    assert "carbonara" not in combined


def test_retrieval_for_credit_score_query(retriever):
    """TC-01-P2-RET-04: a credit-score question retrieves credit-score text."""
    docs = retriever.invoke("What is the minimum credit score for a home loan?")

    combined = " ".join(doc.page_content.lower() for doc in docs)
    assert "credit" in combined or "cibil" in combined


def test_empty_query_handled(retriever):
    """
    TC-01-P2-RET-05: a blank question is handled, not crashed on.

    This one found a real bug. Asking the embedding model for the meaning of an
    empty string is refused by Google with `400 Bad Request`, so the raw
    retriever raised instead of returning nothing — and it did the same in the
    chat box when somebody pressed enter on an empty input. `SafeRetriever`
    now short-circuits a blank question (T-56).
    """
    docs = retriever.invoke("")

    assert isinstance(docs, list)
    assert docs == []


def test_retrieval_latency_under_threshold(retriever):
    """TC-01-P2-RET-06: retrieval finishes well within 5 seconds."""
    start = time.time()
    retriever.invoke("How long does loan approval take?")
    elapsed = time.time() - start

    assert elapsed < 5.0, f"Retrieval took {elapsed:.2f}s, expected < 5s"
