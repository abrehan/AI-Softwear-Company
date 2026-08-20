from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class DevOpsAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "DevOps Agent",
            "DevOps Engineer"
        )

        self.model = "llama3.2:3b"

    async def run(self, task: str):
        return await self.deploy_project(task)

    async def deploy_project(self, task: str):

        print("ðŸš€ DevOps Agent Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        backend_design = memory.get("backend") or ""
        frontend_design = memory.get("frontend") or ""
        database_design = memory.get("database") or ""

        prompt = f"""
You are a Senior DevOps Engineer.

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
ORIGINAL PROJECT
==================================================

{task}

Create a complete DevOps deployment strategy.

Return the result in Markdown.

# DevOps Deployment

## Deployment Overview

## Development Environment

## Production Environment

## Docker

## Docker Compose

## Reverse Proxy

## CI/CD Pipeline

## GitHub Actions

## Environment Variables

## Secrets Management

## Logging

## Monitoring

## Alerting

## Backups

## Scaling

## High Availability

## Disaster Recovery

## Performance Optimization

## Security Best Practices

## Future Improvements
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("devops", result)

        workspace.save(
            "devops/devops_deployment.md",
            result
        )

        print("ðŸ’¾ DevOps deployment saved")

        return result

