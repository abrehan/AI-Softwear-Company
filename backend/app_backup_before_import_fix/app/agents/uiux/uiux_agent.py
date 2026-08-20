from backend.app.agents.base_agent import BaseAgent
from backend.app.memory.project_memory import memory
from backend.app.workspace.workspace import workspace


class UIUXAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "UI/UX Agent",
            "Senior UI/UX Designer"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.design_uiux(task)

    async def design_uiux(self, task: str):

        print("ðŸŽ¨ UI/UX Agent Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        frontend_design = memory.get("frontend") or ""
        database_design = memory.get("database") or ""

        prompt = f"""
You are a Senior UI/UX Designer.

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
FRONTEND DESIGN
==================================================

{frontend_design}

==================================================
DATABASE DESIGN
==================================================

{database_design}

==================================================
ORIGINAL PROJECT
==================================================

{task}

Design the complete UI/UX.

Return the result in Markdown.

# UI/UX Design

## Design Philosophy

## Brand Identity

## Color Palette

## Typography

## Icons

## Design System

## Layout Guidelines

## Navigation

## Dashboard Design

## Mobile Responsive Design

## Forms

## Tables

## Charts

## Accessibility (WCAG)

## Dark Mode

## Light Mode

## User Journey

## Wireframe Suggestions

## Future Improvements
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("uiux", result)

        workspace.save(
            "uiux/uiux_design.md",
            result
        )

        print("ðŸ’¾ UI/UX design saved")

        return result
