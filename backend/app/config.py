import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    cors_origins: str = "http://localhost:5173"
    upload_dir: str = "./uploads"
    duckdb_path: str = "./data/datafriend.duckdb"
    llm_provider: str = "anthropic"
    llm_api_key: str = ""
    llm_model: str = ""

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")
        extra = "ignore"

settings = Settings()
