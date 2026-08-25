from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class DeveloperAgent(BaseAgent):
    """Developer Agent - Converts approved PM and CTO outputs into implementation tasks."""

    def __init__(self):
        super().__init__(
            "Developer Agent",
            "Software Development",
            agent_key="developer",
        )

    async def run(self, task: str):
        return await self.create_implementation_plan(task)

    async def create_implementation_plan(self, task: str):

        print("Developer Agent Started")

        pm_plan = memory.get("pm") or (
            "Not provided in current project context."
        )

        cto_architecture = memory.get("cto") or (
            "Not provided in current project context."
        )

        project_context = self._load_project_context()

        pm_plan = self._limit(pm_plan, 900)
        cto_architecture = self._limit(cto_architecture, 1200)
        project_context = self._limit(project_context, 700)
        task = self._limit(task or "", 350)

        prompt = f"""
You are the Developer Agent of an AI Software Company.

Your job is to convert the approved PM plan and CTO architecture
into a concise implementation plan.

IMPORTANT SYSTEM SEPARATION:

The AI Software Company is the INTERNAL AI orchestration platform.

Its FastAPI, Ollama, Agent Registry, Memory, Workspace, and Model Router
are internal infrastructure.

Do NOT automatically treat those technologies as the backend of the
TARGET hotel booking platform.

SOURCE RULES:

1. Project context is the source of confirmed facts.
2. PM output describes project planning.
3. CTO output describes architecture.
4. Do not invent completed work.
5. Do not invent files, APIs, databases, credentials, services,
   deployments, or infrastructure.
6. Recommended technologies remain recommendations.
7. Unknown information must say:
   Not provided in current project context.
8. Do not claim that you actually changed code.
9. Do not claim that tests passed unless testing information confirms it.
10. Keep the output concise.

RETURN EXACTLY:

# Developer Implementation Plan

## Objective

## Confirmed Inputs

## Implementation Tasks

1. Task
2. Task
3. Task
4. Task
5. Task

## Backend Work

- Item

## Frontend Work

- Item

## Database Work

- Item

## Integration Work

- Item

## Testing Work

- Item

## Security Work

- Item

## Dependencies

- Item

## Unknowns

- Not provided in current project context.

## Next Developer Action

One specific recommended next action.

PROJECT CONTEXT:
{project_context}

PM PLAN:
{pm_plan}

CTO ARCHITECTURE:
{cto_architecture}

CURRENT TASK:
{task}
"""

        result = await self.think(prompt)

        result = (result or "").strip()

        result = result.replace("\\r\\n", "\n")
        result = result.replace("\\n", "\n")
        result = result.replace("`r`n", "\n")
        result = result.replace("`n", "\n")

        if not result:
            raise RuntimeError(
                "Developer Agent returned an empty implementation plan."
            )

        self.remember("developer", result)
        memory.save("developer", result)

        workspace.save(
            "development/developer_plan.md",
            result,
        )

        print(
            "Developer plan saved: "
            "app/workspace/development/developer_plan.md"
        )

        return result

    def _load_project_context(self):

        file = self.workspace / "project_context.md"

        if not file.exists():
            return "Not provided in current project context."

        return file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    @staticmethod
    def _limit(value, maximum):

        value = value or ""

        if len(value) <= maximum:
            return value

        return value[:maximum] + "\n[Context truncated.]"
