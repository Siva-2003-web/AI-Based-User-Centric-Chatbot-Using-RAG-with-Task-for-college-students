import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field("", env="ANTHROPIC_API_KEY")
    groq_api_key: str = Field("", env="GROQ_API_KEY")
    model_name: str = Field("gpt-4o-mini", env="MODEL_NAME")
    embedding_model: str = Field("text-embedding-3-small", env="EMBEDDING_MODEL")
    vector_store: str = Field("chroma", env="VECTOR_STORE")

    # Local LLM endpoint (e.g., Ollama). Used when MODEL_NAME starts with "local-".
    local_llm_url: str = Field("http://127.0.0.1:11434/api/chat", env="LOCAL_LLM_URL")

    chroma_dir: str = Field("./data/chroma", env="CHROMA_DIR")

    pinecone_api_key: str = Field("", env="PINECONE_API_KEY")
    pinecone_environment: str = Field("", env="PINECONE_ENVIRONMENT")
    pinecone_index: str = Field("", env="PINECONE_INDEX")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "protected_namespaces": ("settings_",)  # Fix model_name conflict
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Cached settings avoid reloading env for each request.
    return Settings()  # type: ignore[arg-type]


def ensure_required_keys(settings: Settings) -> None:
    if settings.vector_store == "pinecone" and not settings.pinecone_api_key:
        raise ValueError("Pinecone selected but PINECONE_API_KEY is missing")
    if settings.vector_store == "chroma":
        os.makedirs(settings.chroma_dir, exist_ok=True)
