from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class FrontendAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Frontend Agent",
            "Frontend Engineer",
            agent_key="frontend",
        )

    async def run(self, task: str):
        return await self.develop_frontend(task)

    async def develop_frontend(self, task: str):

        print("Frontend Agent Started")

        ceo_summary = memory.get("ceo") or (
            "Not provided in current project context."
        )

        pm_plan = memory.get("pm") or (
            "Not provided in current project context."
        )

        cto_architecture = memory.get("cto") or (
            "Not provided in current project context."
        )

        backend_design = memory.get("backend") or (
            "Not provided in current project context."
        )

        ceo_summary = self._limit(ceo_summary, 500)
        pm_plan = self._limit(pm_plan, 700)
        cto_architecture = self._limit(cto_architecture, 1000)
        backend_design = self._limit(backend_design, 700)
        task = self._limit(task or "", 350)

        prompt = f"""
You are the Frontend Engineer for an AI Software Company.

Create a concise frontend implementation/design document for the
TARGET PROJECT.

IMPORTANT SYSTEM SEPARATION:

The AI Software Company is the internal AI orchestration platform.

The target project is the product being designed.

Do not confuse the internal FastAPI/Ollama system with the target
frontend.

SOURCE RULES:

1. CEO, PM, CTO, and backend outputs are planning inputs.
2. Do not claim frontend features are already implemented.
3. Do not invent APIs, routes, components, users, or completed work.
4. Unknown information must say:
   Not provided in current project context.
5. Recommendations must be labeled:
   Recommended:
6. Keep the response concise.
7. Do not add unrelated technologies.

RETURN EXACTLY:

# Frontend Design

## Technology Stack

## Folder Structure

## Project Structure

## Routing

## Layout

## Authentication Pages

## Dashboard

## Components

## Reusable Components

## State Management

## API Integration

## Forms

## Tables

## Charts

## Responsive Design

## Dark Mode

## Performance Optimization

## Accessibility

## Future Improvements

CEO INPUT:
{ceo_summary}

PM INPUT:
{pm_plan}

CTO INPUT:
{cto_architecture}

BACKEND INPUT:
{backend_design}

TASK:
{task}

Finish every section.
Use "Not provided in current project context." when necessary.
"""

        result = await self.think(prompt)

        result = (result or "").strip()
        result = result.replace("\\r\\n", "\n")
        result = result.replace("\\n", "\n")
        result = result.replace("`r`n", "\n")
        result = result.replace("`n", "\n")

        if not result:
            raise RuntimeError(
                "Frontend Agent returned an empty design."
            )

        self.remember("frontend", result)
        memory.save("frontend", result)

        workspace.save(
            "frontend/frontend_design.md",
            result,
        )

        print("Frontend design saved")

        return result

    @staticmethod
    def _limit(value: str, maximum: int) -> str:

        value = str(value or "")

        if len(value) <= maximum:
            return value

        return value[:maximum] + "\n[Context truncated.]"
