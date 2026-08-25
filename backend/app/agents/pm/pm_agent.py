from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class PMAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "PM Agent",
            "Senior Project Manager",
            agent_key="pm",
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.plan_project(task)

    async def plan_project(self, task: str):

        print("PM Agent Started")

        ceo_summary = self._limit(
            memory.get("ceo") or "",
            1800,
        )

        project = self._limit(
            task,
            900,
        )

        prompt = f"""
You are a Senior Project Manager.

Create a concise implementation plan for the project.

ORIGINAL PROJECT:
{project}

CEO ANALYSIS:
{ceo_summary}

Return Markdown.

# Project Plan

## Project Objective

## Scope

## Functional Requirements

## Technical Workstreams

## Milestones

## Dependencies

## Risks

## Testing

## Deployment

## Delivery Priorities

Rules:
- Be concrete and concise.
- Do not invent completed work.
- Use only the project request and CEO analysis.
- Keep the response under approximately 1,500 words.
"""

        # IMPORTANT:
        # Use the short direct generation path rather than the
        # context-heavy think_with_context() path.
        result = await self.think(prompt)

        self.remember(
            task,
            result,
        )

        memory.save(
            "pm",
            result,
        )

        workspace.save(
            "project_manager.md",
            result,
        )

        workspace.save(
            "pm.md",
            result,
        )

        workspace.save(
            "planning/project_plan.md",
            result,
        )

        print("PM plan saved")

        return result

    @staticmethod
    def _limit(
        value: str,
        maximum: int,
    ) -> str:

        value = str(value or "")

        if len(value) <= maximum:
            return value

        return (
            value[:maximum]
            + "\n[Context truncated.]"
        )
