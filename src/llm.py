"""One place that creates every chat and embedding model, so a setting can switch providers.

With LLM_PROFILE=local (see config/settings.py) the app's models are served by a local
OpenAI-compatible server such as Ollama. The evaluation judge always uses OpenAI.
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from config.settings import settings

# OpenAI-only options that local servers reject or don't implement
_OPENAI_ONLY = ("reasoning_effort", "use_responses_api")


def chat_model(model=None, **kwargs):
    """A chat model for the app (answers, planning, query expansion, input classification)."""
    model = model or settings.chat_model
    if not settings.llm_base_url:
        return ChatOpenAI(model=model, api_key=settings.openai_api_key, **kwargs)
    for key in _OPENAI_ONLY:
        kwargs.pop(key, None)
    return ChatOpenAI(model=model, base_url=settings.llm_base_url, api_key=settings.llm_api_key or "local", **kwargs)


def judge_model():
    """The evaluation grader: always OpenAI, whatever the app is running on."""
    return ChatOpenAI(model=settings.judge_model, api_key=settings.openai_api_key)


def embeddings():
    if not settings.embedding_base_url:
        return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
    # Local servers take raw strings: skip LangChain's tiktoken pre-splitting, which sends token ids
    return OpenAIEmbeddings(model=settings.embedding_model, base_url=settings.embedding_base_url,
                            api_key=settings.llm_api_key or "local", check_embedding_ctx_length=False)


def describe():
    """The models in use, for result files and reports."""
    return {"profile": settings.llm_profile, "chat_model": settings.chat_model, "rewrite_model": settings.rewrite_model,
            "embedding_model": settings.embedding_model, "judge_model": settings.judge_model}
