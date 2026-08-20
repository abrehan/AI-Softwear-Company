from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class ProjectManagerAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Project Manager",
            "Project Planning",
            agent_key="project_manager",
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.plan_project(task)

    async def plan_project(self, task: str):

        # Read CEO analysis from shared memory
        ceo_summary = memory.get("ceo") or "No CEO analysis is available yet."

        prompt = f"""
You are the Project Manager of an AI Software Company.

Your job is to create a practical project management plan.

CEO ANALYSIS:
{ceo_summary}

ORIGINAL PROJECT REQUEST:
{task}

Create the project plan using exactly these sections:

# PROJECT SUMMARY
Summarize the requested project.

# CURRENT STATUS
Only state information supported by the provided context.
Do not invent completed work.

# PRIORITY
State the priority only when supported by the request/context.

# COMPLEXITY
Give a qualitative assessment based on the actual task.

# PROJECT ROADMAP
Provide clear development phases in logical order.

# MILESTONES
List concrete milestones.

# SPRINT PLAN
Create practical development sprints.

# TEAM ASSIGNMENTS
Assign appropriate agents/teams and explain their responsibilities.

# DEPENDENCIES
List technical and organizational dependencies.

# RISKS
List realistic project risks and mitigations.

# DELIVERABLES
List expected deliverables.

# SUCCESS CRITERIA
Define measurable or clearly verifiable success criteria.

# RECOMMENDED NEXT STEPS
Recommendations only. Do not claim they are already completed.

IMPORTANT RULES:
- Use the original project request as the primary source.
- Use CEO analysis as supporting context.
- Do not invent dates, budgets, customers, revenue, employees, KPIs, achievements,
  completed work, or technical decisions unless provided.
- Do not repeatedly say "assemble a cross-functional team" unless it is actually
  relevant.
- Do not turn recommendations into completed work.
- Produce an actionable project-management plan.
"""

        # IMPORTANT:
        # Send the constructed PM prompt, not the original task alone.
        result = await self.think_with_context(prompt)

        # Save local memory
        self.remember("project_manager", result)

        # Save for other agents
        memory.save("pm", result)

        # Save project plan to shared workspace
        workspace.save(
            "planning/project_plan.md",
            result,
        )

        return result


