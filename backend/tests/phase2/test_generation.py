"""
Phase 2 generation tests, TC-01-P2-GEN-01 to 06.

These make real calls to the model, so they are the slow ones. The chain is
built once per session (see conftest) to keep the number of calls down — the
free tier allows only a handful a minute (T-55).

The trainer's note says to re-run a generation test before concluding it has
failed, because a model's wording varies. Every assertion here is written
against *facts* the answer must carry, never against an exact sentence, which
is the only way these stay stable.
"""


def test_answer_grounded_in_context(chain):
    """TC-01-P2-GEN-01: the answer carries the real figure from the manual."""
    answer = chain.invoke("What is the minimum CIBIL score for a personal loan?")

    assert isinstance(answer, str)
    assert len(answer) > 10
    assert "650" in answer


def test_answer_references_correct_doc_type(chain):
    """TC-01-P2-GEN-02: a home loan's documents are listed correctly."""
    answer = chain.invoke("What documents are required for a home loan?")
    answer_lower = answer.lower()

    required_terms = ["id", "income", "bank_statement", "property"]
    found = [term for term in required_terms if term in answer_lower]
    assert len(found) >= 3, f"Answer missing key documents: {answer}"


def test_answer_for_faq_question(chain):
    """TC-01-P2-GEN-03: an FAQ question gets a real timeframe back."""
    answer = chain.invoke("How long does the personal loan approval process take?")

    assert any(word in answer.lower()
               for word in ["day", "week", "business", "hours"])


def test_no_hallucination_on_out_of_scope(chain):
    """
    TC-01-P2-GEN-04: the assistant refuses what the manual does not cover.

    The most important test in Phase 2. LAMS does not offer gold loans, so
    there is no honest answer. A chatbot that invents a plausible interest rate
    here is worse than useless to a bank — it is a liability.
    """
    answer = chain.invoke("What is the interest rate for gold loans?")

    out_of_scope_indicators = [
        "don't have", "not available", "contact", "helpdesk",
        "not in", "unable to", "no information",
    ]
    assert any(phrase in answer.lower() for phrase in out_of_scope_indicators), \
        f"Chatbot may have hallucinated: {answer}"


def test_response_format_is_string(chain):
    """TC-01-P2-GEN-05: the chain gives back a plain, non-empty string."""
    answer = chain.invoke("What are the age requirements for a personal loan?")

    assert isinstance(answer, str)
    assert len(answer.strip()) > 0


def test_answer_about_rejection_process(chain):
    """TC-01-P2-GEN-06: the rejection rules come back correctly."""
    answer = chain.invoke("What happens if my loan application is rejected?")

    assert any(phrase in answer.lower() for phrase in
               ["new application", "90 day", "rejection reason", "reason", "reapply"])


def test_answer_does_not_contradict_the_code(chain):
    """
    Ours, not the trainer's, and the one that protects the demo.

    The manual is what the chatbot quotes; `rules.py` is what the API enforces.
    If they drift, the assistant contradicts the product live in front of
    whoever is watching (Rule 12). This asks the assistant for the numbers and
    checks them against the code itself.
    """
    from app.domain import rules

    answer = chain.invoke(
        "What is the maximum amount and the tenure range for a personal loan?"
    ).lower()

    # 25,00,000 may be written with or without separators.
    cap = rules.amount_limit("personal")                      # 2_500_000
    assert any(form in answer for form in
               ["25,00,000", "2,500,000", "25 lakh", str(cap)]), \
        f"Answer does not state the real personal cap of {cap}: {answer}"

    low, high = rules.tenure_range("personal")                # (12, 60)
    assert str(low) in answer and str(high) in answer, \
        f"Answer does not state the real tenure range {low}-{high}: {answer}"
