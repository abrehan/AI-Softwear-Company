from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class DatabaseAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Database Agent",
            "Senior Database Architect"
        )

        self.model = "qwen2.5-coder:0.5b"

    async def run(self, task: str):
        return await self.design_database(task)

    async def design_database(self, task: str):

        print("🗄️ Database Agent Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        backend_design = memory.get("backend") or ""

        prompt = f"""
You are a Senior Database Architect.

==================================================
CEO PROJECT ANALYSIS
==================================================

{ceo_summary}

==================================================
PROJECT PLAN
==================================================

{pm_plan}

==================================================
SYSTEM ARCHITECTURE
==================================================

{cto_architecture}

==================================================
BACKEND DESIGN
==================================================

{backend_design}

==================================================
ORIGINAL PROJECT
==================================================

{task}

Design the complete database.

Return the result in Markdown.

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
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("database", result)

        workspace.save(
            "database/database_design.md",
            result
        )

        print("💾 Database design saved")

        return result