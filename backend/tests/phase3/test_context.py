"""
Phase 3 context-management tests: TC-01-P3-CTX-01 to 04.

One adaptation, forced and documented: CTX-04's `from langchain.prompts import
PromptTemplate` no longer exists in LangChain 1.x — the class moved to
`langchain_core.prompts` (same class, same behaviour, different address). This
is the same category of change as T-53, which hit the text splitter in Phase 2.
"""

from langchain_core.prompts import PromptTemplate

from agent.prompts import LOAN_AGENT_SYSTEM_PROMPT
from agent.summarizer import SUMMARIZE_ABOVE_CHARS, summarize_text
from agent.tools import _summarize_if_long


def test_system_prompt_contains_context():
    """TC-01-P3-CTX-01: the prompt says who the agent is and when to use what."""
    prompt = LOAN_AGENT_SYSTEM_PROMPT.lower()

    assert "loan" in prompt
    assert "assistant" in prompt
    assert len(LOAN_AGENT_SYSTEM_PROMPT) > 200
    assert "when" in prompt          # tool-selection guidance


def test_long_response_summarized():
    """TC-01-P3-CTX-02: output too long to hand back gets condensed."""
    long_text = "Application data: " + ("ID: 1, Status: submitted, Amount: 100000. " * 100)
    assert len(long_text) > 2000

    summary = summarize_text(long_text)

    assert isinstance(summary, str)
    assert len(summary) > 0
    assert len(summary) < len(long_text), "Summary should be shorter than the original"


def test_short_response_not_summarized():
    """
    TC-01-P3-CTX-03: a short result is passed through completely untouched.

    Worth asserting exactly rather than loosely: summarising a short tool result
    would cost an extra model call on every single tool call, and would quietly
    reword figures that were already correct.
    """
    short_text = "Application 1: Personal loan, Rs 100,000, Status: Approved"
    assert len(short_text) < SUMMARIZE_ABOVE_CHARS

    result = _summarize_if_long(short_text)

    assert result == short_text


def test_prompt_template_renders_correctly():
    """TC-01-P3-CTX-04: the ReAct template renders with all four variables."""
    prompt = PromptTemplate.from_template(LOAN_AGENT_SYSTEM_PROMPT + """
Tools: {tools}
Tool names: {tool_names}
Input: {input}
Scratchpad: {agent_scratchpad}""")

    rendered = prompt.format(
        tools="tool list",
        tool_names="tool_name_list",
        input="test question",
        agent_scratchpad="",
    )

    assert "test question" in rendered
    assert len(rendered) > 0


def test_the_real_agent_template_renders():
    """
    Ours, not the trainer's. CTX-04 renders a template built inside the test,
    which proves LangChain works but not that *our* prompt does. This renders
    the actual template the agent runs on, which is the one that would break a
    demo if a stray brace ever crept into it.
    """
    from agent.agent import REACT_TEMPLATE

    rendered = PromptTemplate.from_template(REACT_TEMPLATE).format(
        tools="get_application_details: looks up one application",
        tool_names="get_application_details",
        input="What is the status of application 1?",
        agent_scratchpad="",
    )

    assert "What is the status of application 1?" in rendered
    assert "get_application_details" in rendered
