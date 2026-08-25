class ModelRouter:

    MODELS = {
        # Executive agents
        "ceo": "llama3.2:1b",
        "pm": "llama3.2:1b",
        "project_manager": "llama3.2:1b",
        "cto": "llama3.2:1b",

        # Engineering agents
        "backend": "qwen2.5-coder:3b",
        "frontend": "qwen2.5-coder:3b",
        "database": "qwen2.5-coder:3b",
        "devops": "llama3.2:1b",
        "qa": "llama3.2:1b",
        "security": "llama3.2:1b",
        "devsecops": "llama3.2:1b",
        "reviewer": "qwen2.5-coder:3b",

        # AI / ML
        "ai": "llama3.2:1b",
        "ml": "llama3.2:1b",
        "prompt": "llama3.2:1b",

        # Product / business
        "business": "llama3.2:1b",
        "uiux": "llama3.2:1b",
        "writer": "llama3.2:1b",

        # Operations
        "git": "llama3.2:1b",
        "marketing": "llama3.2:1b",
        "seo": "llama3.2:1b",
        "social": "llama3.2:1b",
        "sales": "llama3.2:1b",
        "support": "llama3.2:1b",
        "finance": "llama3.2:1b",
        "legal": "llama3.2:1b",
        "hr": "llama3.2:1b",
        "recruiter": "llama3.2:1b",
    }

    DEFAULT = "llama3.2:1b"

    @classmethod
    def get(cls, agent):
        return cls.MODELS.get(agent, cls.DEFAULT)

