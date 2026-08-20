from backend.app.agents.base_agent import BaseAgent


class LegalAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Legal Advisor",
            "Legal Expert"
        )
        self.model = "llama3.2:1b"

    async def run(self, task):
        print("âœ… legal_review() called")

        prompt = f"""
Legal review.

{task}

Include:

- Privacy Policy
- Terms
- GDPR
- Compliance
"""

        result = await self.think_with_context(task)
        self.remember(task, result)
        return result
