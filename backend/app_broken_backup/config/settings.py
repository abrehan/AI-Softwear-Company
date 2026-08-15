from dataclasses import dataclass


@dataclass
class AISettings:

    OLLAMA_URL = "http://127.0.0.1:11434"

    MODELS = {

        "ceo": "llama3.2:3b",

        "project_manager": "llama3.2:3b",

        "cto": "llama3.2:3b",

        "backend": "qwen2.5-coder:7b",

        "frontend": "qwen2.5-coder:7b",

        "database": "qwen2.5-coder:7b",

        "security": "llama3.2:1b",

        "qa": "llama3.2:1b",

        "devops": "llama3.2:1b",

        "devsecops": "llama3.2:1b",

        "code_reviewer": "qwen2.5-coder:7b",

        "technical_writer": "llama3.2:1b",

        "prompt_engineer": "llama3.2:1b",

        "marketing": "llama3.2:1b",

        "seo": "llama3.2:1b",

        "social_media": "llama3.2:1b",

        "sales": "llama3.2:1b",

        "finance": "llama3.2:1b",

        "legal": "llama3.2:1b",

        "hr": "llama3.2:1b",

        "recruiter": "llama3.2:1b",

        "customer_support": "llama3.2:1b",

        "business_analyst": "llama3.2:3b",

        "ai_engineer": "deepseek-coder-v2",

        "ml_engineer": "deepseek-coder-v2"
    }


settings = AISettings()