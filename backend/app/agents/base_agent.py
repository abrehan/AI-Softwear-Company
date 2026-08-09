from pathlib import Path

from app.services.ollama_service import OllamaService
from app.memory.project_memory import project_memory, memory
from app.context.context_manager import context_manager
from app.services.model_router import ModelRouter
from app.tools.file_tool import tools
from app.tools.terminal_tool import terminal


class BaseAgent:

    def __init__(self, name: str, role: str):

        self.name = name
        self.role = role

        self.files = tools
        self.terminal = terminal

        self.model = ModelRouter.get(name)

        self.ai = OllamaService()

        self.memory = memory
        self.project_memory = project_memory

        self.context = context_manager

        self.workspace = Path("app/workspace")

    async def think(self, prompt: str) -> str:
        """
        Send prompt to Ollama using this agent's assigned model.
        """

        response = await self.ai.generate(
            prompt=prompt,
            model=self.model
        )

        return response

    async def think_with_context(self, prompt: str) -> str:
        """
        Adds global memory/context before sending to Ollama.
        """

        context = ""

        try:
            context = self.context.build_context()
        except Exception:
            pass

        full_prompt = f"""
Role:
{self.role}

Context:
{context}

Task:
{prompt}
"""

        response = await self.ai.generate(
            prompt=full_prompt,
            model=self.model
        )

        return response

    def remember(self, key: str, value: str):
        """
        Save information into project memory.
        """

        self.project_memory.save(key, value)

    def recall(self, key: str):
        """
        Retrieve information from project memory.
        """

        return self.project_memory.get(key)