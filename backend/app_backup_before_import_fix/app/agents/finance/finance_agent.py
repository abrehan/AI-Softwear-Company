from backend.app.agents.base_agent import BaseAgent


class FinanceAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Finance Manager",
            "Finance Expert"
        )
        self.model = "llama3.2:1b"

    async def run(self, task):
        print("âœ… finance_plan() called")

        prompt = f"""
Financial planning.

{task}

Include:

- Budget
- Revenue
- Cost
- Forecast
"""

        result = await self.think_with_context(task)
        self.remember(task, result)
        return result
