from backend.app.agents.base_agent import BaseAgent
from backend.app.memory.project_memory import memory
from backend.app.workspace.workspace import workspace


class CEOAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "CEO Agent",
            "Chief Executive Officer",
            agent_key="ceo",
        )

    async def run(self, task: str):
        return await self.analyze_project(task)

    async def analyze_project(self, task: str):

        prompt = f"""
You are the CEO Agent for the AI Software Company.

Analyze ONLY the project request below.

ORIGINAL PROJECT REQUEST:
{task}

STRICT FACTUALITY POLICY:

1. Use ONLY information explicitly contained in the ORIGINAL PROJECT REQUEST
   and verified project context.

2. NEVER invent or assume:
   - dates
   - deadlines
   - KPIs
   - percentages
   - revenue
   - customers
   - employees
   - achievements
   - completed work
   - launches
   - budgets
   - priority levels
   - complexity levels
   - timelines
   - technical decisions

3. If information is unavailable, write exactly:
   "Not provided in current project context."

4. Recommendations are allowed, but they MUST appear under
   "Recommendations" and MUST NOT be presented as completed work or facts.

5. Do not describe the company as fictional.

6. Do not use information from unrelated previous tasks.

7. Do not treat your own recommendations as facts.

8. Keep the response concise and useful to the Project Manager.

RETURN EXACTLY THIS STRUCTURE:

PROJECT SUMMARY
- List only confirmed facts from the request.

CURRENT STATUS
- State confirmed current status if explicitly provided.
- Otherwise:
  Not provided in current project context.

PRIORITY
- State the priority only if explicitly provided.
- Otherwise:
  Not provided in current project context.

COMPLEXITY
- State complexity only if explicitly provided.
- Otherwise:
  Not provided in current project context.

REQUIRED TEAMS
- List teams explicitly required by the request.
- If the request does not specify teams:
  Not provided in current project context.

UNKNOWN / NOT PROVIDED
- List important missing information.
- Do not invent values.

RECOMMENDATIONS
- Provide practical recommendations.
- Clearly label them as recommendations.
- Do not claim that recommendations have already been completed.

Do not add extra sections.
"""

        result = await self.think_with_context(prompt)

        self.remember(task, result)

        memory.save("ceo", result)

        workspace.save(
            "requirements/project_summary.md",
            result,
        )

        return result
