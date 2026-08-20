from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class SalesAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Sales Manager",
            "Senior Sales Director"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.sales_strategy(task)

    async def sales_strategy(self, task: str):

        print("ðŸ’¼ Sales Manager Started")

        ceo_summary = memory.get("ceo") or ""
        business_analysis = memory.get("business") or ""
        marketing_plan = memory.get("marketing") or ""
        seo_strategy = memory.get("seo") or ""
        social_strategy = memory.get("social") or ""

        prompt = f"""
You are a Senior Sales Director.

==================================================
CEO SUMMARY
==================================================

{ceo_summary}

==================================================
BUSINESS ANALYSIS
==================================================

{business_analysis}

==================================================
MARKETING PLAN
==================================================

{marketing_plan}

==================================================
SEO STRATEGY
==================================================

{seo_strategy}

==================================================
SOCIAL MEDIA STRATEGY
==================================================

{social_strategy}

==================================================
PROJECT
==================================================

{task}

Create a complete Sales Strategy.

Return Markdown.

# Sales Strategy

## Executive Summary

## Ideal Customer Profile (ICP)

## Target Market

## Product Positioning

## Pricing Strategy

## Revenue Model

## Sales Funnel

## Lead Generation

## Lead Qualification

## CRM Workflow

## Sales Pipeline

## Sales Outreach

## Objection Handling

## Customer Retention

## Upselling Strategy

## Cross-selling Strategy

## Partnerships

## Sales KPIs

## Revenue Forecast

## 12-Month Sales Roadmap

## Recommendations
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("sales", result)

        workspace.save(
            "sales/sales_strategy.md",
            result
        )

        print("ðŸ’¾ Sales strategy saved")

        return result

