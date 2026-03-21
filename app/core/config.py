from typing import List
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    ROOT_DIR = Path(__file__).parent.parent.parent

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Cloud Companion"
    APP_VERSION: str = "0.1.0"
    DESCRIPTION: str = "AI-Powered Cloud Resource Troubleshooting Assistant"
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = Field(default="INFO")

    ALLOWED_HOSTS: List[str] = Field(default=["*"])
    CORS_ORIGINS: List[str] = Field(default=["*"])

    @field_validator("ALLOWED_HOSTS", "CORS_ORIGINS", mode="before")
    @classmethod
    def parse_comma_separated(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    NEO4J_URI: str = Field(default="bolt://localhost:7687")
    NEO4J_USER: str = Field(default="neo4j")
    NEO4J_PASSWORD: str = Field(default="")
    NEO4J_DATABASE: str = Field(default="neo4j")

    @field_validator("NEO4J_PASSWORD")
    @classmethod
    def validate_neo4j_password(cls, v: str) -> str:
        if not v:
            raise ValueError("NEO4J_PASSWORD cannot be empty")
        return v

    WEAVIATE_HOST: str = Field(default="localhost")

    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")

    LLM_PROVIDER: str = Field(default="ollama")
    LLM_MODEL: str = Field(default="gpt-4o-mini")
    MINI_LLM_MODEL: str = Field(default="gpt-4o-mini")
    LLM_API_KEY: str = Field(default="")

    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")

    LLM_TEMPERATURE: float = Field(default=0.2)
    LLM_MAX_TOKENS: int = Field(default=1024)

    API_HMAC_SECRET: str = Field(default="")

    @field_validator("API_HMAC_SECRET")
    @classmethod
    def validate_api_hmac_secret(cls, v: str) -> str:
        if not v:
            raise ValueError("API_HMAC_SECRET must be set for secure operations")
        return v

    AWS_PROFILE_MODE: str = Field(default="DEFAULT")

    AWS_REGIONS: List[str] = Field(default=["us-east-1", "us-west-2"])

    @field_validator("AWS_REGIONS")
    @classmethod
    def validate_aws_regions(cls, v) -> List[str]:
        if isinstance(v, str):
            v = [item.strip() for item in v.split(",")]
        return v

    AZURE_SP_AUTH: bool = Field(default=False)
    AZURE_TENANT_ID: str = Field(default="")
    AZURE_CLIENT_ID: str = Field(default="")
    AZURE_CLIENT_SECRET: str = Field(default="")

    AZURE_SUBSCRIPTION_ID: str = Field(default="")

    GCP_PROJECT_ID: str = Field(default="")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
