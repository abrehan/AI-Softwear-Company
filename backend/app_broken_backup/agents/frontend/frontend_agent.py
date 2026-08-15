from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class FrontendAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Frontend Agent",
            "Frontend Engineer"
        )

        self.model = "llama3.2:3b"

    async def run(self, task: str):
        return await self.develop_frontend(task)

    async def develop_frontend(self, task: str):

        print("🎨 Frontend Agent Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        backend_design = memory.get("backend") or ""

        prompt = f"""
You are a Senior React + Next.js Frontend Engineer.

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

Design the complete frontend.

Return the result in Markdown.

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
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("frontend", result)

        workspace.save(
            "frontend/frontend_design.md",
            result
        )

        print("💾 Frontend design saved")

        return result