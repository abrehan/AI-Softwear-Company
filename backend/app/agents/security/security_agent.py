from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class SecurityAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Security Agent",
            "Senior Cyber Security Engineer",
            agent_key="security",
        )

    async def run(self, task: str):
        return await self.security_review(task)

    async def security_review(self, task: str):

        print("Security Agent Started")

        ceo_summary = self._get("ceo")
        pm_plan = self._get("pm")
        cto_architecture = self._get("cto")
        backend_design = self._get("backend")
        frontend_design = self._get("frontend")
        database_design = self._get("database")
        devops_plan = self._get("devops")
        qa_plan = self._get("qa")

        ceo_summary = self._limit(ceo_summary, 300)
        pm_plan = self._limit(pm_plan, 400)
        cto_architecture = self._limit(cto_architecture, 700)
        backend_design = self._limit(backend_design, 700)
        frontend_design = self._limit(frontend_design, 400)
        database_design = self._limit(database_design, 500)
        devops_plan = self._limit(devops_plan, 250)
        qa_plan = self._limit(qa_plan, 500)
        task = self._limit(task or "", 300)

        prompt = f"""
You are the Senior Cyber Security Engineer for an AI Software Company.

Review the current project outputs and produce a concise security
assessment.

IMPORTANT:
The AI Software Company is the internal orchestration platform.
The target project is the managed product.
Do not confuse the two.

RULES:

1. Review only the information supplied below.
2. Do not claim a security control already exists unless confirmed.
3. Do not claim a vulnerability was fixed unless evidence says it was fixed.
4. Do not invent incidents, credentials, breaches, compliance certifications,
   or completed security work.
5. Unknown information must say:
   Not provided in current project context.
6. Recommendations must begin with:
   Recommended:
7. Findings should be clearly distinguished from recommendations.
8. Keep the report concise.
9. Complete every section.

RETURN EXACTLY:

# Security Report

## Security Overview

## Authentication

## Authorization

## JWT Strategy

## OAuth

## API Security

## SQL Injection Protection

## XSS Protection

## CSRF Protection

## CORS Policy

## Password Policy

## Secrets Management

## Encryption

## Database Security

## Server Security

## Docker Security

## Cloud Security

## Vulnerability Assessment

## Security Checklist

## Critical Findings

## Recommendations

## Security Gate

CEO:
{ceo_summary}

PM:
{pm_plan}

CTO:
{cto_architecture}

BACKEND:
{backend_design}

FRONTEND:
{frontend_design}

DATABASE:
{database_design}

DEVOPS:
{devops_plan}

QA:
{qa_plan}

TASK:
{task}

For controls not confirmed by the supplied information, use:
Not provided in current project context.

Finish every section.
"""

        result = await self.think(prompt)

        result = self._normalize(result)

        if not result:
            raise RuntimeError(
                "Security Agent returned an empty security report."
            )

        self.remember("security", result)
        memory.save("security", result)

        workspace.save(
            "security/security_report.md",
            result,
        )

        print("Security report saved")

        return result

    def _get(self, key: str) -> str:
        value = memory.get(key)

        if value:
            return value

        return "Not provided in current project context."

    @staticmethod
    def _limit(value: str, maximum: int) -> str:
        value = str(value or "")

        if len(value) <= maximum:
            return value

        return value[:maximum] + "\n[Context truncated.]"

    @staticmethod
    def _normalize(result: str) -> str:
        result = (result or "").strip()

        result = result.replace("\\r\\n", "\n")
        result = result.replace("\\n", "\n")
        result = result.replace("`r`n", "\n")
        result = result.replace("`n", "\n")

        return result.strip()
