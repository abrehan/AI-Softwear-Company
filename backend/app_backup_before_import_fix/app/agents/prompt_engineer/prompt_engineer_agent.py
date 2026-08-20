from backend.app.agents.base_agent import BaseAgent
from backend.app.memory.project_memory import memory
from backend.app.workspace.workspace import workspace


class PromptEngineerAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Prompt Engineer",
            "Senior Prompt Engineer"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.design_prompts(task)

    async def design_prompts(self, task: str):

        print("ðŸ“ Prompt Engineer Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        ai_engineering = memory.get("ai") or ""
        ml_engineering = memory.get("ml") or ""

        prompt = f"""
You are a Senior Prompt Engineer.

==================================================
CEO ANALYSIS
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
AI ENGINEERING
==================================================

{ai_engineering}

==================================================
ML ENGINEERING
==================================================

{ml_engineering}

==================================================
PROJECT
==================================================

{task}

Design the complete Prompt Engineering strategy.

Return Markdown.

# Prompt Engineering

## Prompt Strategy

## System Prompts

## Agent Prompts

## CEO Prompt

## PM Prompt

## CTO Prompt

## Developer Prompts

## AI Prompts

## RAG Prompts

## Memory Prompts

## Reflection Prompts

## Planning Prompts

## Tool Calling Prompts

## Error Recovery Prompts

## Prompt Optimization

## Prompt Security

## Prompt Versioning

## Future Improvements
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("prompt", result)

        workspace.save(
            "prompt/prompt_engineering.md",
            result
        )

        print("ðŸ’¾ Prompt engineering saved")

        return result
