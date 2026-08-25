from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class DatabaseAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Database Agent",
            "Senior Database Architect",
            agent_key="database",
        )

    async def run(self, task: str):
        return await self.design_database(task)

    async def design_database(self, task: str):

        print("Database Agent Started")

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
        backend_design = self._limit(backend_design, 800)
        task = self._limit(task or "", 350)

        prompt = f"""
You are the Database Architect for an AI Software Company.

Create a concise database design for the TARGET PROJECT.

IMPORTANT SYSTEM SEPARATION:

The AI Software Company is the internal orchestration platform.

The target project is the product being managed by that platform.

Do not confuse the internal AI Software Company database with the
target project's database.

SOURCE RULES:

1. CEO, PM, CTO, and Backend outputs are planning inputs.
2. Do not claim anything is already implemented unless confirmed.
3. Do not invent existing tables or migrations.
4. Recommended database decisions must be labeled:
   Recommended:
5. Unknown information must say:
   Not provided in current project context.
6. Keep the response concise.
7. Do not invent credentials or secrets.
8. Do not claim migrations or schema deployment has happened.

RETURN EXACTLY:

# Database Design

## Recommended Database

## Why This Database

## Database Schema

## Tables

## Columns

## Primary Keys

## Foreign Keys

## Relationships

## Indexes

## Constraints

## Views

## Stored Procedures

## Transactions

## Backup Strategy

## Security

## Performance Optimization

## Scalability

## Migration Strategy

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
Use "Not provided in current project context." when needed.
Prefix proposals with "Recommended:".
"""

        result = await self.think(prompt)

        result = self._normalize(result)

        if not result:
            raise RuntimeError(
                "Database Agent returned an empty design."
            )

        self.remember("database", result)
        memory.save("database", result)

        workspace.save(
            "database/database_design.md",
            result,
        )

        print("Database design saved")

        return result

    @staticmethod
    def _limit(value: str, maximum: int) -> str:

        value = str(value or "")

        if len(value) <= maximum:
            return value

        return value[:maximum] + "\n[Context truncated.]"

    @staticmethod
    def _normalize(result: str) -> str:

        result = (result or "").strip()

        result = result.replace("\\r\\n", "\n")
        result = result.replace("\\n", "\n")
        result = result.replace("`r`n", "\n")
        result = result.replace("`n", "\n")

        return result.strip()
