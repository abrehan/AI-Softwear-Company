from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class DevOpsAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "DevOps Agent",
            "DevOps Engineer",
            agent_key="devops",
        )

    async def run(self, task: str):
        return await self.deploy_project(task)

    async def deploy_project(self, task: str):

        print("DevOps Agent Started")

        ceo_summary = self._get("ceo")
        pm_plan = self._get("pm")
        cto_architecture = self._get("cto")
        backend_design = self._get("backend")
        frontend_design = self._get("frontend")
        database_design = self._get("database")
        qa_plan = self._get("qa")
        security_plan = self._get("security")

        ceo_summary = self._limit(ceo_summary, 250)
        pm_plan = self._limit(pm_plan, 350)
        cto_architecture = self._limit(cto_architecture, 650)
        backend_design = self._limit(backend_design, 500)
        frontend_design = self._limit(frontend_design, 350)
        database_design = self._limit(database_design, 400)
        qa_plan = self._limit(qa_plan, 350)
        security_plan = self._limit(security_plan, 400)
        task = self._limit(task or "", 300)

        prompt = f"""
You are the DevOps Engineer for an AI Software Company.

Create a concise deployment and operations plan for the target project.

IMPORTANT SYSTEM SEPARATION:

The AI Software Company is the internal orchestration platform.
The target project is the product managed by that platform.

RULES:

1. Use only the supplied project information.
2. Do not claim infrastructure already exists unless confirmed.
3. Do not invent cloud providers, servers, domains, production
   deployments, Kubernetes clusters, Docker environments, or CI/CD
   systems.
4. Every proposal must begin with:
   Recommended:
5. Unknown information must say:
   Not provided in current project context.
6. Do not claim deployment has occurred.
7. Keep the output concise.
8. Complete every section.

RETURN EXACTLY:

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

QA:
{qa_plan}

SECURITY:
{security_plan}

TASK:
{task}

Unknown items must use:
Not provided in current project context.

Recommendations must begin with:
Recommended:
"""

        result = await self.think(prompt)

        result = self._normalize(result)

        if not result:
            raise RuntimeError(
                "DevOps Agent returned an empty deployment plan."
            )

        self.remember("devops", result)
        memory.save("devops", result)

        workspace.save(
            "devops/devops_deployment.md",
            result,
        )

        print("DevOps deployment saved")

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
