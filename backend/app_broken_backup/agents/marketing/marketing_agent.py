from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class MarketingAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Marketing Manager",
            "Chief Marketing Officer"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.marketing_plan(task)

    async def marketing_plan(self, task: str):

        print("📣 Marketing Manager Started")

        ceo_summary = memory.get("ceo") or ""
        business_analysis = memory.get("business") or ""
        technical_docs = memory.get("writer") or ""

        prompt = f"""
You are a Chief Marketing Officer.

CEO Summary

{ceo_summary}

Business Analysis

{business_analysis}

Technical Documentation

{technical_docs}

Original Project

{task}

Create a complete software marketing strategy.

Return Markdown.

# Marketing Strategy

## Executive Summary

## Brand Positioning

## Target Audience

## Customer Personas

## Value Proposition

## Marketing Channels

## Content Marketing

## Email Marketing

## Paid Advertising

## Organic Marketing

## Community Building

## Partnerships

## Launch Strategy

## Marketing Budget

## KPIs

## Growth Strategy

## 12 Month Marketing Roadmap
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("marketing", result)

        workspace.save(
            "marketing/marketing_plan.md",
            result
        )

        print("💾 Marketing plan saved")

        return result