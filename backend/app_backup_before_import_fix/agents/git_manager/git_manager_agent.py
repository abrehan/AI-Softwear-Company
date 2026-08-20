from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class GitManagerAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Git Manager",
            "Senior Git & DevOps Engineer"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.manage_git(task)

    async def manage_git(self, task: str):

        print("🌿 Git Manager Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        backend_design = memory.get("backend") or ""
        frontend_design = memory.get("frontend") or ""
        database_design = memory.get("database") or ""
        devops_plan = memory.get("devops") or ""
        reviewer_report = memory.get("reviewer") or ""

        prompt = f"""
You are a Senior Git Engineer.

CEO Summary
{ceo_summary}

Project Plan
{pm_plan}

Architecture
{cto_architecture}

Backend
{backend_design}

Frontend
{frontend_design}

Database
{database_design}

DevOps
{devops_plan}

Code Review
{reviewer_report}

Original Project
{task}

Design the complete Git strategy.

Return Markdown.

# Git Strategy

## Repository Structure

## Branch Strategy

## Git Flow

## Branch Naming

## Commit Convention

## Pull Request Workflow

## Code Review Rules

## Merge Strategy

## Release Strategy

## Semantic Versioning

## GitHub Actions

## CI/CD Integration

## Tags

## Rollback Strategy

## Best Practices
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("git", result)

        workspace.save(
            "git/git_strategy.md",
            result
        )

        print("💾 Git strategy saved")

        return result