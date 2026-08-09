from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class CEOAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "CEO Agent",
            "Chief Executive Officer"
        )
        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.analyze_project(task)

    async def analyze_project(self, task: str):

        prompt = f"""
You are the CEO of an AI software company.

Analyze this project:

{task}

Return:

- Project Summary
- Priority
- Complexity
- Required Teams
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("ceo", result)

        workspace.save(
            "requirements/project_summary.md",
            result
        )

        return result