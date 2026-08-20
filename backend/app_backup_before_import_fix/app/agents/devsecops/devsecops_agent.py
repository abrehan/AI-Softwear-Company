from backend.app.agents.base_agent import BaseAgent
from backend.app.memory.project_memory import memory
from backend.app.workspace.workspace import workspace


class DevSecOpsAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "DevSecOps Agent",
            "Senior DevSecOps Engineer"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.devsecops_strategy(task)

    async def devsecops_strategy(self, task: str):

        print("ðŸ›¡ï¸ DevSecOps Agent Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        backend_design = memory.get("backend") or ""
        frontend_design = memory.get("frontend") or ""
        database_design = memory.get("database") or ""
        devops_plan = memory.get("devops") or ""
        security_report = memory.get("security") or ""

        prompt = f"""
You are a Senior DevSecOps Engineer.

==================================================
CEO PROJECT ANALYSIS
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
BACKEND DESIGN
==================================================

{backend_design}

==================================================
FRONTEND DESIGN
==================================================

{frontend_design}

==================================================
DATABASE DESIGN
==================================================

{database_design}

==================================================
DEVOPS PLAN
==================================================

{devops_plan}

==================================================
SECURITY REPORT
==================================================

{security_report}

==================================================
ORIGINAL PROJECT
==================================================

{task}

Create a complete DevSecOps strategy.

Return the result in Markdown.

# DevSecOps Strategy

## DevSecOps Overview

## Secure Development Lifecycle (SDLC)

## Secure Git Workflow

## Secret Management

## Dependency Scanning

## Static Code Analysis (SAST)

## Dynamic Security Testing (DAST)

## Container Security

## Docker Image Scanning

## Infrastructure as Code Security

## CI/CD Security

## Artifact Signing

## Vulnerability Management

## Compliance (OWASP, CIS, NIST)

## Monitoring & Incident Response

## Backup & Disaster Recovery

## Future Improvements"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("devsecops", result)

        workspace.save(
            "security/devsecops_strategy.md",
            result
        )

        print("ðŸ’¾ DevSecOps strategy saved")

        return result
