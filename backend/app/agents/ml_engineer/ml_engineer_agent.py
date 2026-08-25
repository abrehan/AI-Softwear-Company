from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class MLEngineerAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "ML Engineer",
            "Senior Machine Learning Engineer",
        )

        self.model = "llama3.2:3b"

    async def run(self, task: str):
        return await self.design_ml_system(task)

    async def design_ml_system(self, task: str):

        print("ML Engineer Started")

        ceo_summary = self._limit(
            memory.get("ceo") or "",
            700,
        )

        cto_architecture = self._limit(
            memory.get("cto") or "",
            1200,
        )

        ai_engineering = self._limit(
            memory.get("ai") or "",
            1000,
        )

        project = self._limit(
            task,
            600,
        )

        prompt = f"""
You are a Senior Machine Learning Engineer.

Design the ML architecture for this project.

CEO SUMMARY:
{ceo_summary}

SYSTEM ARCHITECTURE:
{cto_architecture}

AI ENGINEERING:
{ai_engineering}

PROJECT:
{project}

Keep the response concise and practical.

Return Markdown with exactly these sections:

# Machine Learning Engineering
## ML Overview
## ML Objectives
## Data Strategy
## Feature Engineering
## Model Selection
## Training Pipeline
## Evaluation
## Deployment
## Monitoring
## Retraining
## Future Improvements
"""

        result = await self.think(prompt)

        self.remember(task, result)

        memory.save(
            "ml",
            result,
        )

        workspace.save(
            "ml/ml_engineering.md",
            result,
        )

        print("ML engineering saved")

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
