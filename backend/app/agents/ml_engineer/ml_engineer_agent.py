from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class MLEngineerAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "ML Engineer",
            "Senior Machine Learning Engineer"
        )

        self.model = "llama3.2:3b"

    async def run(self, task: str):
        return await self.design_ml_system(task)

    async def design_ml_system(self, task: str):

        print("ðŸ§  ML Engineer Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        ai_engineering = memory.get("ai") or ""

        prompt = f"""
You are a Senior Machine Learning Engineer.

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
PROJECT
==================================================

{task}

Design the Machine Learning architecture.

Return Markdown.

# Machine Learning Engineering

## ML Overview

## ML Objectives

## Datasets

## Data Collection

## Data Cleaning

## Feature Engineering

## Training Pipeline

## Model Selection

## Deep Learning

## Recommendation Engine

## Classification

## Regression

## Clustering

## Forecasting

## Evaluation Metrics

## Model Deployment

## Monitoring

## Retraining Strategy

## Future Improvements
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("ml", result)

        workspace.save(
            "ml/ml_engineering.md",
            result
        )

        print("ðŸ’¾ ML engineering saved")

        return result

