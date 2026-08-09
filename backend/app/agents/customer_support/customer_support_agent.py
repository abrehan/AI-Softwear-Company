from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class CustomerSupportAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Customer Support",
            "Customer Success Manager"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.customer_support(task)

    async def customer_support(self, task: str):

        print("🎧 Customer Support Started")

        ceo_summary = memory.get("ceo") or ""
        business_analysis = memory.get("business") or ""
        sales_strategy = memory.get("sales") or ""
        technical_docs = memory.get("writer") or ""

        prompt = f"""
You are a Customer Success Manager.

==================================================
CEO SUMMARY
==================================================

{ceo_summary}

==================================================
BUSINESS ANALYSIS
==================================================

{business_analysis}

==================================================
SALES STRATEGY
==================================================

{sales_strategy}

==================================================
TECHNICAL DOCUMENTATION
==================================================

{technical_docs}

==================================================
PROJECT
==================================================

{task}

Create a complete Customer Support Plan.

Return Markdown.

# Customer Support Strategy

## Executive Summary

## Customer Journey

## Support Channels

- Email
- Live Chat
- WhatsApp
- Phone
- Ticket System
- Knowledge Base

## Ticket Workflow

## Priority Levels

## SLA Policy

## Escalation Process

## FAQ Strategy

## Self-Service Portal

## Customer Success Workflow

## Customer Feedback Collection

## Complaint Handling

## Customer Retention Strategy

## Support KPIs

## Support Team Structure

## Automation Opportunities

## Monthly Improvement Plan

## Recommendations
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("support", result)

        workspace.save(
            "support/customer_support.md",
            result
        )

        print("💾 Customer support plan saved")

        return result