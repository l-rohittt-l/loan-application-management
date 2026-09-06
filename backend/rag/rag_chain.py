"""
The RAG chain: answer a question using only what the user manual actually says.

RAG means Retrieval Augmented Generation. Rather than asking the model "what
documents does a home loan need?" and hoping it knows, we:

  1. search our own manual for the paragraphs closest in meaning to the question
  2. paste those paragraphs into the prompt
  3. tell the model to answer using only that text

The answer is then grounded in our document instead of the model's imagination,
and when the manual does not cover something the model is told to say so rather
than invent a plausible number. For a bank that matters: a chatbot that guesses
an interest rate is worse than one that admits it does not know.

Shapes the trainer's tests depend on
------------------------------------
  build_rag_chain()                     -> (chain, retriever)
  chain.invoke("a question")            -> a plain string
  answer_question(query, chain, retriever)

`chain.invoke` must take a string and give back a string, which is why the last
step of the pipeline is `StrOutputParser()`.

Built to be reused by the later phases
--------------------------------------
Phase 3 gives the assistant a `search_loan_policy` tool, Phase 4 exposes the
same ability over MCP, and Phase 5's compliance agent needs to quote policy
too. All of them call `answer_policy_question()` below rather than building
their own chain, so there is exactly one definition of "what the manual says"
in the whole project.
"""

from __future__ import annotations

import time

import structlog
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from app.config import settings
from app.utils.logging_config import configure_logging
from app.utils.otel_config import get_tracer, setup_telemetry
from llm_provider import describe, enable_langsmith, get_collection_name, get_embeddings, get_llm

logger = structlog.get_logger()

LANGSMITH_PROJECT = "AI-Readiness-POC-01-P2"

# The exact sentence the Phase 2 spec requires when the manual does not cover
# the question. The test looks for "don't have", "contact" and "helpdesk".
OUT_OF_SCOPE_ANSWER = (
    "I don't have information about that in the user manual. "
    "Please contact our helpdesk."
)

SYSTEM_PROMPT = """You are the assistant for LAMS, the bank's Loan Application \
Management System. You answer questions from customers and from bank staff.

Answer using ONLY the manual extracts given to you below. They are the bank's \
official policy. Do not use anything you know from outside them, and never \
guess a number.

Rules you must follow:
- If the extracts contain the answer, give it directly and quote the exact \
figures, amounts and timeframes as they are written.
- If the extracts do not contain the answer, reply with exactly this sentence \
and nothing else: "{out_of_scope}"
- Never invent an interest rate, a fee, a limit or a timeframe.
- Keep the answer short and plain. Two or three sentences is usually enough.
- Write amounts the way the manual writes them, for example Rs 25,00,000.
- When you list required documents, name them exactly as the manual names them, \
including the underscore form such as id_proof and bank_statement.

Manual extracts:
{context}"""


def format_context(documents) -> str:
    """Lay the retrieved chunks out for the prompt, numbered so they can be cited."""
    if not documents:
        return "(no relevant extracts were found in the manual)"
    parts = []
    for i, doc in enumerate(documents, start=1):
        parts.append(f"[Extract {i}]\n{doc.page_content.strip()}")
    return "\n\n".join(parts)


def get_vectorstore():
    """The ChromaDB collection holding the manual, for the provider in use."""
    from langchain_chroma import Chroma

    return Chroma(
        collection_name=get_collection_name(),
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


class SafeRetriever(BaseRetriever):
    """
    A retriever that survives a blank question.

    Asking the embedding model to describe the meaning of an empty string is not
    a sensible request, and Google refuses it outright with `400 Bad Request`.
    That surfaced as a crash rather than an empty result, both in the trainer's
    `TC-01-P2-RET-05` and, more importantly, in the chat box whenever somebody
    pressed enter on an empty input. There is nothing to search for, so we
    return nothing instead of asking.
    """

    inner: object

    def _get_relevant_documents(self, query: str, *, run_manager=None):
        if not (query or "").strip():
            return []
        return self.inner.invoke(query)


def get_retriever(k: int | None = None):
    """
    The thing that finds the k chunks closest in meaning to a question.
    k comes from TOP_K_RESULTS, which the Phase 2 spec fixes at 4.
    """
    inner = get_vectorstore().as_retriever(
        search_kwargs={"k": k or settings.top_k_results}
    )
    return SafeRetriever(inner=inner)


def _retrieve_with_span(question: str, retriever):
    """Retrieve, wrapped in the `rag.retrieve` span the observability guide wants."""
    tracer = get_tracer()
    with tracer.start_as_current_span("rag.retrieve") as span:
        started = time.perf_counter()
        # An empty question has nothing to match on. ChromaDB would still hand
        # back four arbitrary chunks, so we stop here instead (RET-05).
        documents = [] if not (question or "").strip() else retriever.invoke(question)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        span.set_attribute("rag.question", (question or "")[:200])
        span.set_attribute("rag.retrieved", len(documents))
        span.set_attribute("rag.duration_ms", duration_ms)
        logger.info("rag_retrieved", operation="retrieve",
                    retrieved=len(documents), duration_ms=duration_ms)
        return documents


def build_rag_chain(k: int | None = None):
    """
    Build the question-answering chain.

    Returns `(chain, retriever)`, in that order, because the trainer's
    generation tests unpack it exactly that way. `chain.invoke("...")` takes a
    plain string and returns a plain string.
    """
    configure_logging()
    setup_telemetry()
    enable_langsmith(LANGSMITH_PROJECT)

    retriever = get_retriever(k)
    llm = get_llm(temperature=0.1)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ]).partial(out_of_scope=OUT_OF_SCOPE_ANSWER)

    def retrieve_context(question: str) -> str:
        return format_context(_retrieve_with_span(question, retriever))

    def generate(prompt_value):
        """The `rag.generate` span, around the actual call to the model."""
        tracer = get_tracer()
        with tracer.start_as_current_span("rag.generate") as span:
            started = time.perf_counter()
            reply = llm.invoke(prompt_value)
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            span.set_attribute("rag.duration_ms", duration_ms)
            span.set_attribute("rag.chat_model", describe()["chat_model"])
            logger.info("rag_generated", operation="generate", duration_ms=duration_ms)
            return reply

    chain = (
        {"context": RunnableLambda(retrieve_context), "question": RunnablePassthrough()}
        | prompt
        | RunnableLambda(generate)
        | StrOutputParser()
    )
    return chain, retriever


def answer_question(query: str, chain=None, retriever=None) -> dict:
    """
    Answer one question and report everything about how it was answered: the
    answer itself, the extracts it came from, and how long each part took.

    The screens use this rather than `chain.invoke` because they show the source
    extracts underneath the answer, which is what lets a person check the
    assistant rather than simply trust it.

    The trainer's `TC-01-P2-OBS-03` calls this and then looks for a JSON log
    line whose `operation` is `question_answered`, carrying `poc_id` and `phase`.
    """
    configure_logging()
    setup_telemetry()

    if chain is None or retriever is None:
        chain, retriever = build_rag_chain()

    started = time.perf_counter()
    documents = _retrieve_with_span(query, retriever)

    if not documents:
        # Nothing to ground an answer in, so do not call the model at all.
        answer = OUT_OF_SCOPE_ANSWER
    else:
        answer = chain.invoke(query)

    duration_ms = round((time.perf_counter() - started) * 1000, 2)

    logger.info(
        "rag_question_answered",
        operation="question_answered",
        question=query[:200],
        answer_chars=len(answer),
        sources=len(documents),
        duration_ms=duration_ms,
        provider=describe()["provider"],
    )

    return {
        "question": query,
        "answer": answer,
        "sources": [
            {
                "chunk_id": d.metadata.get("chunk_id"),
                "source": d.metadata.get("source"),
                "excerpt": d.page_content.strip(),
            }
            for d in documents
        ],
        "duration_ms": duration_ms,
    }


# --------------------------------------------------------------------------
# One built chain, shared. Building it is cheap but not free, and the later
# phases call this on every message.
# --------------------------------------------------------------------------

_cached: tuple | None = None


def get_chain():
    """The shared chain and retriever, built on first use."""
    global _cached
    if _cached is None:
        _cached = build_rag_chain()
    return _cached


def answer_policy_question(query: str) -> str:
    """
    Just the answer, as a string.

    This is the single entry point the later phases use: Phase 3's
    `search_loan_policy` tool, Phase 4's MCP resource, and Phase 5's compliance
    agent all call this, so "what the manual says" is defined in exactly one
    place across the whole project.
    """
    chain, retriever = get_chain()
    return answer_question(query, chain, retriever)["answer"]


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]) or "What is the minimum CIBIL score for a personal loan?"
    result = answer_question(question)
    print("\nQ:", result["question"])
    print("\nA:", result["answer"])
    print(f"\n({len(result['sources'])} extracts, {result['duration_ms']} ms)")
