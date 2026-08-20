from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class QAAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "QA Agent",
            "QA Engineer"
        )

        self.model = "llama3.2:3b"

    async def run(self, task: str):
        return await self.test_project(task)

    async def test_project(self, task: str):

        print("ðŸ§ª QA Agent Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        backend_design = memory.get("backend") or ""
        frontend_design = memory.get("frontend") or ""
        database_design = memory.get("database") or ""
        devops_plan = memory.get("devops") or ""

        prompt = f"""
You are a Senior QA Engineer.

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
DEVOPS DEPLOYMENT
==================================================

{devops_plan}

==================================================
ORIGINAL PROJECT
==================================================

{task}

Create a complete QA strategy.

Return the result in Markdown.

# QA Test Plan

## Testing Strategy

## Unit Testing

## Integration Testing

## API Testing

## UI Testing

## End-to-End Testing

## Performance Testing

## Load Testing

## Security Testing

## Regression Testing

## Smoke Testing

## Browser Compatibility

## Mobile Testing

## Automation Framework

## Test Data

## Bug Reporting Workflow

## Release Checklist

## Future Improvements
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("qa", result)

        workspace.save(
            "qa/test_plan.md",
            result
        )

        print("ðŸ’¾ QA test plan saved")

        return result

