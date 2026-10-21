"""The provider switch: LLM_PROFILE=local points the app at a local OpenAI-compatible server."""
from config.settings import BASE_DIR, Settings
from src import llm


def test_openai_is_the_default():
    s = Settings(_env_file=None)
    assert s.llm_profile == "openai" and s.llm_base_url == "" and s.index_dir == BASE_DIR / "vector_db"


def test_local_profile_fills_ollama_defaults_and_keeps_a_separate_index():
    s = Settings(_env_file=None, llm_profile="local")
    assert s.llm_base_url == "http://localhost:11434/v1" and s.embedding_base_url == s.llm_base_url
    assert s.chat_model == "qwen2.5:7b" and s.embedding_model == "nomic-embed-text"
    assert s.index_dir == BASE_DIR / "vector_db_local"
    assert s.judge_model == Settings(_env_file=None).judge_model  # the grader doesn't change


def test_explicit_settings_override_the_local_defaults():
    s = Settings(_env_file=None, llm_profile="local", chat_model="qwen2.5:14b")
    assert s.chat_model == "qwen2.5:14b" and s.rewrite_model == "qwen2.5:7b"


def test_local_chat_model_drops_openai_only_options(monkeypatch):
    monkeypatch.setattr(llm.settings, "llm_base_url", "http://localhost:11434/v1")
    m = llm.chat_model("qwen2.5:7b", reasoning_effort="low", use_responses_api=True)
    assert m.model_name == "qwen2.5:7b"
    assert m.openai_api_base == "http://localhost:11434/v1"
    assert m.reasoning_effort is None and not m.use_responses_api


def test_judge_stays_on_openai_under_the_local_profile(monkeypatch):
    monkeypatch.setattr(llm.settings, "llm_base_url", "http://localhost:11434/v1")
    monkeypatch.setattr(llm.settings, "openai_api_key", "sk-test")
    assert llm.judge_model().openai_api_base is None
