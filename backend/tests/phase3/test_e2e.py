"""
Phase 3 end-to-end reasoning tests: TC-01-P3-E2E-01 to 06.

These are the ones that actually matter. Every test above proves a tool works;
these prove the agent *chooses* the right one, which the blueprint says plainly
is what is really being graded. E2E-02 is the benchmark: a question that needs
two different tools, where answering with one is a wrong answer.

All of them share one agent (the session-scoped `executor` fixture) because the
free Gemini tier allows only a handful of requests a minute, and a ReAct loop
spends one call per thinking step.
"""

from app.config import settings

STATUSES = ["submitted", "under_review", "approved", "rejected", "disbursed"]


def _tools_used(result) -> list[str]:
    """Which tools the agent actually called, in order."""
    return [step[0].tool for step in result.get("intermediate_steps", [])]


def test_agent_answers_status_query(running_api, executor):
    """
    TC-01-P3-E2E-01: a question about one application gets a real status.

    The trainer's own version of this test checks for the literal enum
    spelling, "under_review", with the underscore. A correct agent does not
    write like that — it answers in plain English, "is currently under
    review", with a space. That is the whole point of putting an LLM in
    front of the data; forcing it to parrot the database's own spelling back
    verbatim would be a worse answer for no test that actually needs it. So
    this copy checks for either spelling, the same way T-36 adapted a Phase 1
    test that would have failed against any correct implementation.
    """
    from agent.agent import run_agent

    result = run_agent("What is the status of application 1?", executor)
    output = result.get("output", "").lower()

    assert len(output) > 10
    normalised = output.replace("_", " ")
    assert any(status in output or status.replace("_", " ") in normalised
               for status in STATUSES + ["not found"])


def test_agent_uses_multiple_tools(running_api, executor):
    """
    TC-01-P3-E2E-02: the benchmark — one question, two tools, both called.

    "What is the status of application 1 and what documents are needed for a
    home loan?" cannot be answered from live data alone or from the manual
    alone. The agent has to notice it needs both and combine them.
    """
    from agent.agent import run_agent

    result = run_agent(
        "What is the status of application 1 and what documents are needed for a home loan?",
        executor,
    )
    used = _tools_used(result)

    assert len(used) >= 2, f"Only used {used}"
    assert "get_application_details" in used, f"Never looked up the application: {used}"
    assert "search_loan_policy" in used, f"Never consulted the manual: {used}"


def test_agent_answers_policy_only_query(running_api, executor):
    """
    TC-01-P3-E2E-03: a pure policy question uses the manual, not the database.

    The interesting half of this is what it must *not* do — reaching for the
    application API on a question about policy would be the classic wrong-tool
    failure.
    """
    from agent.agent import run_agent

    result = run_agent("What is the minimum income required for a home loan?", executor)
    used = _tools_used(result)
    output = result.get("output", "").lower()

    assert "search_loan_policy" in used, f"Used {used} instead of the manual"
    assert any(term in output for term in ["income", "monthly", "annual", "4,80,000", "480000"])


def test_agent_summarizes_multiple_applications(running_api, executor):
    """TC-01-P3-E2E-04: a "how many" question comes back with a number."""
    from agent.agent import run_agent

    result = run_agent("How many applications are currently pending review?", executor)
    output = result.get("output", "")

    assert len(output) > 0
    assert any(char.isdigit() for char in output) or "no application" in output.lower()


def test_agent_handles_ambiguous_query(running_api, executor):
    """TC-01-P3-E2E-05: a vague question still gets a coherent reply, not a crash."""
    from agent.agent import run_agent

    result = run_agent("Tell me about loans", executor)
    output = result.get("output", "")

    assert len(output) > 10
    assert "traceback" not in output.lower()


def test_agent_refuses_out_of_scope(running_api, executor):
    """
    Ours, not the trainer's. The system prompt tells the agent to decline
    anything that isn't about loans. An assistant that cheerfully answers
    questions about the weather in a bank demo undermines everything else on
    screen, so it is worth proving rather than assuming.
    """
    from agent.agent import run_agent

    result = run_agent("What is the best recipe for pasta carbonara?", executor)
    output = result.get("output", "").lower()

    assert any(phrase in output for phrase in
               ["loan", "can only", "cannot help", "not able", "unable", "sorry"]), \
        f"Did not decline an off-topic question: {output}"


def test_full_reasoning_chain_traced(running_api, executor):
    """
    TC-01-P3-E2E-06: the reasoning shows up in this phase's LangSmith project.

    The very first trace this project (`AI-Readiness-POC-01-P3`) ever
    receives has to create the project on LangSmith's side before anyone can
    query it, and that can take longer than the trainer's fixed 3-second
    sleep — the project genuinely does not exist yet, not just "not synced".
    `list_runs` raises `LangSmithNotFoundError` in that case, not an empty
    list, so a plain retry loop is needed rather than a longer sleep.
    """
    import time

    import pytest
    from langsmith import Client
    from langsmith.utils import LangSmithNotFoundError

    from agent.agent import LANGSMITH_PROJECT, run_agent

    if not settings.langchain_api_key:
        pytest.skip("LANGCHAIN_API_KEY is not set")

    run_agent("What is the dashboard summary?", executor)

    client = Client(api_key=settings.langchain_api_key)
    runs: list = []
    for _ in range(6):   # up to ~15s: traces upload in the background
        time.sleep(2.5)
        try:
            runs = list(client.list_runs(project_name=LANGSMITH_PROJECT, limit=3))
        except LangSmithNotFoundError:
            continue   # the project itself hasn't been created server-side yet
        if runs:
            break

    assert len(runs) > 0, f"No traces found in {LANGSMITH_PROJECT}"
