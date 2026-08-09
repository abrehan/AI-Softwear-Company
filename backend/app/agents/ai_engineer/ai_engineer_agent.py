from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class AIEngineerAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "AI Engineer",
            "Senior Artificial Intelligence Engineer"
        )

        self.model = "llama3.2:3b"

    async def run(self, task: str):
        return await self.design_ai_system(task)

    async def design_ai_system(self, task: str):

        print("🤖 AI Engineer Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        backend_design = memory.get("backend") or ""
        frontend_design = memory.get("frontend") or ""
        database_design = memory.get("database") or ""
        security_report = memory.get("security") or ""
        devsecops_strategy = memory.get("devsecops") or ""

        prompt = f"""
You are a Senior AI Engineer.

CEO Analysis
{ceo_summary}

Project Plan
{pm_plan}

System Architecture
{cto_architecture}

Backend Design
{backend_design}

Frontend Design
{frontend_design}

Database Design
{database_design}

Security Report
{security_report}

DevSecOps Strategy
{devsecops_strategy}

Original Project
{task}

Design the complete AI architecture.

Return Markdown.

# AI Engineering

## AI Overview

## AI Features

## AI Agents

## Multi-Agent Architecture

## LLM Selection

## Local Models

## Cloud Models

## Tool Calling

## Memory Strategy

## Vector Database

## RAG Pipeline

## Embedding Strategy

## Agent Communication

## AI Workflow

## Error Handling

## Monitoring

## AI Security

## Future Improvements
"""

        result = await self.think(prompt)

        self.remember(task, result)

        memory.save("ai", result)

        workspace.save(
            "ai/ai_engineering.md",
            result
        )

        print("💾 AI engineering saved")

        return result