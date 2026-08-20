class ModelRouter:

    MODELS = {
        "ceo": "llama3.2:3b",
        "pm": "llama3.2:3b",
        "cto": "llama3.2:3b",

        "backend": "qwen2.5-coder:7b",
        "frontend": "qwen2.5-coder:7b",
        "database": "qwen2.5-coder:7b",
        "reviewer": "qwen2.5-coder:7b",
    }

    DEFAULT = "llama3.2:1b"

    @classmethod
    def get(cls, agent):
        return cls.MODELS.get(agent, cls.DEFAULT)

