from backend.app.agents.base_agent import BaseAgent
from backend.app.memory.project_memory import memory
from backend.app.workspace.workspace import workspace


class TechnicalWriterAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Technical Writer",
            "Senior Technical Documentation Engineer"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.write_documentation(task)

    async def write_documentation(self, task: str):

        print("ðŸ“š Technical Writer Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        backend_design = memory.get("backend") or ""
        frontend_design = memory.get("frontend") or ""
        database_design = memory.get("database") or ""
        ai_engineering = memory.get("ai") or ""
        ml_engineering = memory.get("ml") or ""
        prompt_engineering = memory.get("prompt") or ""

        prompt = f"""
You are a Senior Technical Writer.

CEO Summary
{ceo_summary}

Project Plan
{pm_plan}

Architecture
{cto_architecture}

Backend
{backend_design}

Frontend
{frontend_design}

Database
{database_design}

AI Engineering
{ai_engineering}

ML Engineering
{ml_engineering}

Prompt Engineering
{prompt_engineering}

Original Project
{task}

Create complete technical documentation.

Return Markdown.

# Technical Documentation

## Project Overview

## Business Goals

## Architecture Overview

## Backend Documentation

## Frontend Documentation

## Database Documentation

## API Documentation

## AI Architecture

## ML Pipeline

## Prompt Engineering

## Installation Guide

## Configuration

## Deployment

## Folder Structure

## Troubleshooting

## Future Roadmap
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("writer", result)

        workspace.save(
            "writer/technical_documentation.md",
            result
        )

        print("ðŸ’¾ Technical documentation saved")

        return result
