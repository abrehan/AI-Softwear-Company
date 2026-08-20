# backend/app/core/config.py

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    APP_TITLE: str = Field(..., env="APP_TITLE")
    APP_DESCRIPTION: str = Field(..., env="APP_DESCRIPTION")
    API_VERSION: str = Field("1.0", env="API_VERSION")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
