from app.services.ollama_service import OllamaService
from app.services.model_router import ModelRouter
import re


class MainGenerator:

    def __init__(self):
        self.ai = OllamaService()
        self.model = ModelRouter.get("backend")

    async def generate(
        self,
        filepath,
        ceo_summary,
        project_plan,
        architecture,
        task
    ):

        prompt = f"""
You are a Senior FastAPI Backend Engineer.

Generate ONLY this file:

{filepath}

Project Summary:
{ceo_summary}

Project Plan:
{project_plan}

Architecture:
{architecture}

Task:
{task}

Rules:
- Generate ONLY this file.
- No markdown.
- No explanations.
- No ``` blocks.
"""

        code = await self.ai.generate(
            prompt,
            self.model
        )

        code = re.sub(r"^```[a-zA-Z]*", "", code)
        code = re.sub(r"```$", "", code)
        code = code.strip()

        return code