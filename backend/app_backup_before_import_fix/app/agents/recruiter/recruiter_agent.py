from backend.app.agents.base_agent import BaseAgent


class RecruiterAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Recruiter",
            "Talent Acquisition Specialist"
        )
        self.model = "llama3.2:1b"

    async def run(self, task):
        print("âœ… recruit_team() called")

        prompt = f"""
Recruitment plan.

{task}

Include:

- Required Roles
- Job Descriptions
- Hiring Process
- Interview Questions
"""

        result = await self.think_with_context(task)
        self.remember(task, result)
        return result
