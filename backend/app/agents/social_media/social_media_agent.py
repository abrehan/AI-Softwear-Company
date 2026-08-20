from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class SocialMediaAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Social Media Manager",
            "Senior Social Media Strategist"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.social_campaign(task)

    async def social_campaign(self, task: str):

        print("ðŸ“± Social Media Manager Started")

        ceo_summary = memory.get("ceo") or ""
        business_analysis = memory.get("business") or ""
        marketing_plan = memory.get("marketing") or ""
        seo_strategy = memory.get("seo") or ""

        prompt = f"""
You are a Senior Social Media Manager.

CEO Summary

{ceo_summary}

Business Analysis

{business_analysis}

Marketing Plan

{marketing_plan}

SEO Strategy

{seo_strategy}

Original Project

{task}

Create a complete Social Media Strategy.

Return Markdown.

# Social Media Strategy

## Executive Summary

## Brand Voice

## Target Audience

## Platform Strategy

### LinkedIn

### Facebook

### Instagram

### X (Twitter)

### YouTube

### TikTok

### Reddit

## Content Pillars

## 30-Day Content Calendar

## Posting Schedule

## Reels / Shorts Strategy

## Hashtag Strategy

## Community Engagement

## Influencer Strategy

## Paid Social Campaigns

## KPIs

## Monthly Growth Plan

## Recommendations
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("social", result)

        workspace.save(
            "social/social_media_plan.md",
            result
        )

        print("ðŸ’¾ Social media strategy saved")

        return result

