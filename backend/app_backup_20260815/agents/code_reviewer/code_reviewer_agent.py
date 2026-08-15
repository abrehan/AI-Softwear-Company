from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class CodeReviewerAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Code Reviewer",
            "Senior Software Architect"
        )

        self.model = "qwen2.5-coder:0.5b"

    async def run(self, task: str):
        return await self.review_code(task)

    async def review_code(self, task: str):

        print("🔍 Code Reviewer Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        backend_design = memory.get("backend") or ""
        frontend_design = memory.get("frontend") or ""
        database_design = memory.get("database") or ""
        ai_engineering = memory.get("ai") or ""
        ml_engineering = memory.get("ml") or ""
        prompt_engineering = memory.get("prompt") or ""
        technical_docs = memory.get("writer") or ""

        prompt = f"""
You are a Senior Code Reviewer.

==================================================
CEO SUMMARY
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
BACKEND
==================================================

{backend_design}

==================================================
FRONTEND
==================================================

{frontend_design}

==================================================
DATABASE
==================================================

{database_design}

==================================================
AI ENGINEERING
==================================================

{ai_engineering}

==================================================
ML ENGINEERING
==================================================

{ml_engineering}

==================================================
PROMPT ENGINEERING
==================================================

{prompt_engineering}

==================================================
TECHNICAL DOCUMENTATION
==================================================

{technical_docs}

==================================================
PROJECT
==================================================

{task}

Review the complete software project.

Return Markdown.

# Code Review Report

## Executive Summary

## Architecture Review

## Backend Review

## Frontend Review

## Database Review

## API Review

## AI Review

## ML Review

## Prompt Engineering Review

## Security Review

## Performance Review

## Scalability Review

## Maintainability Review

## Code Smells

## Bugs Found

## Risks

## Improvement Suggestions

## Best Practices

## Final Score
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("reviewer", result)

        workspace.save(
            "reviewer/code_review.md",
            result
        )

        print("💾 Code review saved")

        return result