"""Central configuration. Override any value with an environment variable or .env entry."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    openai_api_key: str = ""

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

    # API and operations
    api_auth_token: str = ""  # if set, API requests must send this in the X-API-Key header
    rate_limit_per_minute: int = 20  # per client, for the API
    log_dir: Path = BASE_DIR / "logs"
    # Optional cost estimates (USD per 1M tokens). Leave at 0 to report tokens only.
    price_input_per_million: float = 0.0
    price_output_per_million: float = 0.0


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
