"""
The one place that decides which AI provider we are talking to.

**No other file in this project may import ChatGoogleGenerativeAI, ChatOllama,
or either embeddings class.** Everything else — the Phase 2 ingestion and RAG
chain, the Phase 3 tools, the Phase 4 MCP server, the Phase 5 agents — calls
`get_llm()`, `get_embeddings()` and `get_collection_name()` from here.

Why it is worth a whole file for three functions: Gemini was blocked on the
company network for six weeks and the entire cohort had to move to Ollama
mid-programme. It can happen again, including during a presentation. With this
file, switching providers is one line in `.env`. Without it, it is an edit to
fourteen files while somebody watches.

Two things this file quietly protects us from
---------------------------------------------

1. **Mixing one provider's vectors with another's.** ChromaDB compares numbers;
   it has no idea which model produced them. Ask a Gemini question against a
   collection built by Ollama and — if the sizes happen to match — you get no
   error at all, just confident, plausible, completely wrong answers. That is
   the worst kind of failure in a demo, because it looks like the AI is simply
   stupid. `get_collection_name()` keeps each provider in its own collection so
   the two can never meet.

2. **Models being withdrawn.** The models the trainer specified,
   `gemini-2.0-flash` and `models/text-embedding-004`, no longer exist. Because
   the names live in `.env` and are read here, that was a one-line fix rather
   than a rewrite.
"""

from __future__ import annotations

import os

import structlog

from app.config import settings

logger = structlog.get_logger()

GEMINI = "gemini"
OLLAMA = "ollama"


def enable_langsmith(project: str) -> bool:
    """
    Turn on LangSmith tracing for the given project, if a key is configured.

    LangChain reads `LANGCHAIN_TRACING_V2` and `LANGCHAIN_API_KEY` straight from
    the process environment at call time, not from our settings object, so this
    copies them across. Each phase has its own project name
    (`AI-Readiness-POC-01-P2`, `-P3`, `-P4`, `-P5`) because the trainer's
    observability tests look for traces in one specific project each, and a
    single shared project would mix them together.

    Called once per phase, right before building that phase's chain or agent.
    Safe to call with no key set: it simply leaves tracing off and says so once.
    """
    if not settings.langchain_tracing_v2 or not settings.langchain_api_key:
        return False
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"] = project
    logger.info("langsmith_enabled", operation="langsmith_enabled", project=project)
    return True


def current_provider() -> str:
    """Whichever provider `.env` asks for, normalised. Anything unknown is refused."""
    provider = (settings.llm_provider or GEMINI).strip().lower()
    if provider not in (GEMINI, OLLAMA):
        raise ValueError(
            f"LLM_PROVIDER is '{provider}'. It must be '{GEMINI}' or '{OLLAMA}'."
        )
    return provider


def get_collection_name(provider: str | None = None) -> str:
    """
    The ChromaDB collection to read and write for the provider in use.

    Gemini keeps the bare name because the trainer's `TC-01-P2-ING-04` and
    `TC-01-P2-RET-01` open it by that exact literal string:

        client.get_collection("poc_01_loan_manual")

    A suffix there would fail both tests instantly. Ollama, which no test names,
    gets `poc_01_loan_manual_ollama`. So the tests pass on the default provider
    and the two providers still never share a collection (T-46).
    """
    provider = provider or current_provider()
    base = settings.chroma_collection
    return base if provider == GEMINI else f"{base}_{provider}"


def _build_gemini_llm(temperature: float, **kwargs):
    """Gemini's chat model on its own, with no fallback wrapped around it."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    if not settings.google_api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is empty. Put the key in backend/.env, or set "
            "LLM_PROVIDER=ollama to use the local fallback."
        )
    return ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        google_api_key=settings.google_api_key,
        temperature=temperature,
        **kwargs,
    )


def _build_ollama_llm(temperature: float, **kwargs):
    """Ollama's chat model on its own."""
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=settings.ollama_chat_model,
        base_url=settings.ollama_base_url,
        temperature=temperature,
        **kwargs,
    )


def ollama_reachable(timeout: float = 1.0) -> bool:
    """
    Is there an Ollama server answering on this machine right now?

    Asked before we bother attaching Ollama as a fallback. Without this check, a
    laptop with no Ollama installed would wrap every Gemini call in a fallback
    that can only fail a second time — turning one clear error into two, and
    doubling how long the user waits for it.

    Deliberately cheap and deliberately silent: one HTTP GET with a short
    timeout, and any failure at all means "no".
    """
    import urllib.request

    try:
        urllib.request.urlopen(settings.ollama_base_url, timeout=timeout).read(1)
        return True
    except Exception:                                       # noqa: BLE001
        return False


def get_llm(temperature: float = 0.1, fallback: bool = True, **kwargs):
    """
    The chat model, with an automatic fallback to the other provider.

    Temperature 0.1 is the Phase 2 default: predictable and factual rather than
    creative. Phase 3's agent asks for 0 instead, so it picks the same tool for
    the same question every time.

    **Why this falls back on its own.** Gemini is the default provider and it is
    the better model, but its free tier has a daily cap that has run out in the
    middle of a working session before, and the company network has blocked it
    outright for weeks at a time. Either one used to mean editing `.env` and
    restarting the server — impossible while somebody is watching a demo. Now
    the first call that fails is retried against Ollama on the same machine, and
    the answer still arrives.

    LangChain's own `.with_fallbacks()` does the work: it returns a model that
    tries the first one and moves to the second on **any** exception, which is
    what we want here, since a quota refusal, a network block and a withdrawn
    model all look different but all mean "ask the other one".

    Two things it deliberately does not do:

    - **It never falls back the other way.** If `.env` names Ollama, Ollama is
      what runs. Someone who chose the local model chose it for a reason, and
      quietly sending their question to Google would be a worse surprise than an
      error.
    - **It does not touch embeddings.** See `get_embeddings()` for why that one
      must never switch by itself.

    Pass `fallback=False` for a bare model with nothing wrapped around it, which
    is what `check_ready()` uses to report on one provider honestly.
    """
    provider = current_provider()

    if provider == OLLAMA:
        return _build_ollama_llm(temperature, **kwargs)

    primary = _build_gemini_llm(temperature, **kwargs)

    # Only attach a fallback if Ollama is actually there to answer.
    if not fallback or not ollama_reachable():
        return primary

    logger.info(
        "llm_fallback_armed",
        operation="llm_fallback_armed",
        primary=settings.gemini_chat_model,
        fallback=settings.ollama_chat_model,
    )
    return primary.with_fallbacks([_build_ollama_llm(temperature, **kwargs)])


def get_embeddings():
    """
    The model that turns a piece of text into a list of numbers representing its
    meaning. Gemini's returns 3072 numbers per chunk; Ollama's nomic-embed-text
    returns 768.

    **This one has no automatic fallback, and that is on purpose.** `get_llm()`
    falls back to Ollama the moment Gemini refuses, because one chat model can
    always answer in another's place. Embeddings cannot. Each provider's numbers
    live in their own ChromaDB collection, and the manual has to have been
    ingested into that collection first. If this silently switched provider, the
    retriever would go looking in a collection that is very likely empty and the
    chatbot would answer from nothing at all — confidently, with no error and no
    sources. A visible failure is far better than a confident wrong answer.

    So switching embedding provider stays a deliberate act: change
    `LLM_PROVIDER` in `.env` and re-run `python -m rag.ingest`.
    """
    provider = current_provider()

    if provider == GEMINI:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        if not settings.google_api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is empty. Put the key in backend/.env, or set "
                "LLM_PROVIDER=ollama to use the local fallback."
            )
        return GoogleGenerativeAIEmbeddings(
            model=settings.gemini_embed_model,
            google_api_key=settings.google_api_key,
        )

    from langchain_ollama import OllamaEmbeddings

    return OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url,
    )


def describe() -> dict:
    """
    What is actually in use, for logging and for the demo. Never includes the
    API key.
    """
    provider = current_provider()
    if provider == GEMINI:
        chat, embed = settings.gemini_chat_model, settings.gemini_embed_model
    else:
        chat, embed = settings.ollama_chat_model, settings.ollama_embed_model
    out = {
        "provider": provider,
        "chat_model": chat,
        "embed_model": embed,
        "collection": get_collection_name(provider),
    }
    # Worth surfacing: on Gemini, whether the automatic Ollama fallback has
    # something to fall back to. Answers "is the safety net actually there?"
    # without anyone having to break Gemini to find out.
    if provider == GEMINI:
        out["chat_fallback"] = (
            settings.ollama_chat_model if ollama_reachable() else None
        )
    return out


def check_ready() -> tuple[bool, str]:
    """
    A cheap "can we actually talk to the provider?" check, for startup and for
    the health endpoint. Returns (ok, message) and never raises, so a dead
    provider degrades the app instead of stopping it from booting.
    """
    try:
        provider = current_provider()
        if provider == GEMINI and not settings.google_api_key:
            return False, "GOOGLE_API_KEY is not set"
        # fallback=False on purpose: this is a health check, and a check that
        # quietly passes because the *other* provider answered would be telling
        # us the opposite of what we asked.
        get_llm(fallback=False).invoke("Reply with the single word: ready")
        return True, f"{provider} responded"
    except Exception as e:                                  # noqa: BLE001
        logger.warning("llm_provider_unavailable", error=str(e)[:200])
        return False, f"{type(e).__name__}: {str(e)[:200]}"
