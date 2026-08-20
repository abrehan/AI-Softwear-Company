import os
from pathlib import Path

from app.services.ollama_service import OllamaService
from app.memory.project_memory import project_memory, memory
from app.context.context_manager import context_manager
from app.services.model_router import ModelRouter
from app.tools.file_tool import tools
from app.tools.terminal_tool import terminal


class BaseAgent:

    def __init__(
        self,
        name: str,
        role: str,
        agent_key: str | None = None,
    ):
        self.name = name
        self.role = role

        self.agent_key = agent_key or name.lower().replace(" ", "_")
        self.model = ModelRouter.get(self.agent_key)

        self.files = tools
        self.terminal = terminal

        self.ai = OllamaService()

        self.memory = memory
        self.project_memory = project_memory

        self.context = context_manager

        if os.getenv("VERCEL"):
            self.workspace = Path("/tmp/ai-software-company/workspace")
        else:
            self.workspace = Path(__file__).resolve().parents[1] / "workspace"

        self.workspace.mkdir(parents=True, exist_ok=True)

    async def think(self, prompt: str) -> str:
        """
        Send a prompt to the configured AI provider.
        """
        return await self.ai.generate(
            prompt=prompt,
            model=self.model,
        )

    async def think_with_context(
        self,
        prompt: str,
        controlled_context: str | None = None,
    ) -> str:
        """
        Send a prompt to the AI provider.

        When controlled_context is supplied, use only that context.
        Otherwise, use the existing workspace context.
        """

        if controlled_context is None:
            try:
                context = self.context.build_context()
            except Exception:
                context = ""
        else:
            context = controlled_context

        full_prompt = f"""
Role:
{self.role}

Project Context:
{context}

Task:
{prompt}
"""

        return await self.ai.generate(
            prompt=full_prompt,
            model=self.model,
        )

    def remember(self, key: str, value: str):
        """
        Save information into project memory.
        """
        return self.project_memory.save(key, value)

    def recall(self, key: str):
        """
        Retrieve information from project memory.
        """
        return self.project_memory.get(key)

