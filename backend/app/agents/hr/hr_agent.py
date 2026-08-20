from app.agents.base_agent import BaseAgent


class HRAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "HR Manager",
            "Human Resource Manager"
        )
        self.model = "llama3.2:1b"

    async def run(self, task):
        print("âœ… hr_plan() called")

        prompt = f"""
Human resource planning.

{task}

Include:

- Policies
- Hiring
- Culture
- Training
"""

        result = await self.think_with_context(task)
        self.remember(task, result)
        return result

