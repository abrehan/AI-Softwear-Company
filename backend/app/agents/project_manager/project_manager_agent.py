from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class ProjectManagerAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Project Manager",
            "Project Planning"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.plan_project(task)

    async def plan_project(self, task: str):

        # Read CEO analysis from shared memory
        ceo_summary = memory.get("ceo")

        prompt = f"""
You are the Project Manager of an AI Software Company.

CEO Analysis:

{ceo_summary}

Original Project Request:

{task}

Create a complete project management plan including:

- Project Roadmap
- Milestones
- Timeline
- Sprint Plan
- Risks
- Deliverables
- Team Assignments
- Dependencies
- Success Criteria
"""

        result = await self.think_with_context(task)

        # Save in local memory
        self.remember(task, result)

        # Save for other agents
        memory.save("pm", result)

        # Save inside workspace
        workspace.save(
            "planning/project_plan.md",
            result
        )

        return result