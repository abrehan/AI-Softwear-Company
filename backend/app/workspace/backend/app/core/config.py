import os


class Settings:

    APP_NAME: str = os.getenv(
        "APP_NAME",
        "AI Software Company",
    )

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./app.db",
    )

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "development-only-change-this",
    )

    ALGORITHM: str = os.getenv(
        "ALGORITHM",
        "HS256",
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "30",
        )
    )

    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434",
    )

    DEBUG: bool = (
        os.getenv("DEBUG", "false").lower()
        == "true"
    )


settings = Settings()


def get_settings():
    return settings