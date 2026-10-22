"""Central configuration. Override any value with an environment variable or .env entry."""
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    openai_api_key: str = ""

    # Model provider. "openai" (default) or "local": a local OpenAI-compatible server such as Ollama
    # answers, expands queries, classifies input and embeds. The eval judge always stays on OpenAI so
    # both systems are graded identically. Any value below can still be overridden in .env.
    llm_profile: str = "openai"
    llm_base_url: str = ""  # OpenAI-compatible endpoint for the app's models, e.g. http://localhost:11434/v1
    llm_api_key: str = ""  # local servers usually ignore it
    embedding_base_url: str = ""  # endpoint for embeddings; empty means OpenAI

    # Paths
    data_dir: Path = BASE_DIR / "data"
    ocr_dir: Path = BASE_DIR / "data" / "ocr"
    index_dir: Path = BASE_DIR / "vector_db"

    # Models
    chat_model: str = "gpt-5.4-mini"
    judge_model: str = "gpt-5.5"
    vision_model: str = "gpt-5.4-mini"
    rewrite_model: str = "gpt-5.4-nano"  # cheap model for query expansion
    embedding_model: str = "text-embedding-3-small"

    # Ingestion
    chunk_size: int = 1200
    chunk_overlap: int = 150
    min_page_chars: int = 200  # pages with less extractable text are transcribed from the image

    # Retrieval
    retriever_k: int = 10  # chunks passed to the LLM
    candidate_k: int = 30  # candidates per retriever before fusion
    rrf_k: int = 60  # reciprocal rank fusion constant
    query_expansion: bool = True  # add LLM-written search queries in annual-report terminology

    # Guardrails
    max_question_chars: int = 1000
    llm_input_classifier: bool = True  # second layer after pattern checks: off-topic / injection classifier
    # An "off_topic" verdict is overruled when the question names one of the companies (an "injection" verdict
    # never is). The local profile turns this on: its small classifier calls plain company questions off-topic.
    company_names_overrule_off_topic: bool = False

    # API and operations
    api_auth_token: str = ""  # if set, API requests must send this in the X-API-Key header
    rate_limit_per_minute: int = 20  # per client, for the API
    log_dir: Path = BASE_DIR / "logs"
    # Optional cost estimates (USD per 1M tokens). Leave at 0 to report tokens only.
    price_input_per_million: float = 0.0
    price_output_per_million: float = 0.0

    @model_validator(mode="after")
    def _local_profile_defaults(self):
        """LLM_PROFILE=local fills in Ollama defaults for anything the .env doesn't set, and keeps
        its own index, since the vectors from a different embedding model aren't interchangeable.
        The chat model is qwen2.5:7b with a 16k context (config/ollama/qwen2.5-7b-16k.Modelfile):
        Ollama's 4k default truncates the answer prompt."""
        if self.llm_profile != "local":
            return self
        defaults = {"llm_base_url": "http://localhost:11434/v1", "embedding_base_url": "http://localhost:11434/v1",
                    "chat_model": "qwen2.5-7b-16k", "rewrite_model": "qwen2.5-7b-16k",
                    "embedding_model": "nomic-embed-text", "index_dir": BASE_DIR / "vector_db_local",
                    "company_names_overrule_off_topic": True}
        for field, value in defaults.items():
            if field not in self.model_fields_set:
                object.__setattr__(self, field, value)
        return self


settings = Settings()

# Company name -> document metadata. Aliases drive deterministic company filtering.
COMPANIES = {
    "Michelin": {"file": "Michelin_2025.pdf", "doc": "Michelin 2025 Universal Registration Document",
                 "aliases": ["michelin"],
                 # Section 5.3: statutory accounts of the parent company (CGEM), not the consolidated group
                 "parent_company_pages": [(448, 473)]},
    "Goodyear": {"file": "Goodyear_2025.pdf", "doc": "Goodyear 2025 Form 10-K",
                 "aliases": ["goodyear", "good year"]},
    "Continental": {"file": "Continental_2025.pdf", "doc": "Continental 2025 Annual Report",
                    "aliases": ["continental", "conti"]},
    "Bridgestone": {"file": "Bridgestone_2025.pdf", "doc": "Bridgestone 2025 Integrated Report",
                    "aliases": ["bridgestone"]},
}
