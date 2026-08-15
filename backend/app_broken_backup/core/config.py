from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Software Company"

    OLLAMA_URL: str = "http://localhost:11434"

    DEFAULT_MODEL: str = "llama3.1:8b"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()