from backend.app.agents.base_agent import BaseAgent
from backend.app.memory.project_memory import memory
from backend.app.workspace.workspace import workspace


class BusinessAnalystAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Business Analyst",
            "Senior Business Analyst"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.analyze_business(task)

    async def analyze_business(self, task: str):

        print("ðŸ“Š Business Analyst Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        technical_docs = memory.get("writer") or ""

        prompt = f"""
You are a Senior Business Analyst.

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
TECHNICAL DOCUMENTATION
==================================================

{technical_docs}

==================================================
PROJECT
==================================================

{task}

Create a complete Business Analysis document.

Return Markdown.

# Business Analysis

## Executive Summary

## Business Objectives

## Problem Statement

## Target Users

## Stakeholders

## Functional Requirements

## Non-Functional Requirements

## User Stories

## Acceptance Criteria

## Business Rules

## Risk Analysis

## KPIs

## Success Metrics

## Cost Considerations

## Future Opportunities

## Recommendations
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("business", result)

        workspace.save(
            "business/business_analysis.md",
            result
        )

        print("ðŸ’¾ Business analysis saved")

        return result
