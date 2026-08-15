from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class SEOAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "SEO Specialist",
            "Senior SEO Engineer"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.seo_analysis(task)

    async def seo_analysis(self, task: str):

        print("🔍 SEO Specialist Started")

        ceo_summary = memory.get("ceo") or ""
        business_analysis = memory.get("business") or ""
        marketing_plan = memory.get("marketing") or ""
        frontend_design = memory.get("frontend") or ""

        prompt = f"""
You are a Senior SEO Specialist.

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
FRONTEND DESIGN
==================================================

{frontend_design}

==================================================
PROJECT
==================================================

{task}

Create a complete SEO strategy.

Return Markdown.

# SEO Strategy

## Executive Summary

## Keyword Research

## Search Intent Analysis

## Competitor Analysis

## Technical SEO

## On-Page SEO

## Off-Page SEO

## Content Strategy

## Internal Linking

## Backlink Strategy

## Local SEO

## International SEO

## Schema Markup

## Core Web Vitals

## Site Speed Optimization

## SEO KPIs

## Monthly SEO Roadmap

## Recommendations
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("seo", result)

        workspace.save(
            "seo/seo_strategy.md",
            result
        )

        print("💾 SEO strategy saved")

        return result