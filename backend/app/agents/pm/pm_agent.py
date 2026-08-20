from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace

class PMAgent(BaseAgent):
    """Project Manager Agent - Breaks down projects into tasks."""
    
    def __init__(self):
        super().__init__(
            "PM Agent",
            "Project Manager",
            agent_key="pm",
        )
        self.model = "llama3.2:3b"
    
    async def run(self, task: str):
        return await self.plan_project(task)
    
    async def plan_project(self, project_analysis: str):
        """Create a detailed project plan from CEO analysis."""
        
        print("PM Agent: Creating project plan...")
        
        prompt = f"""
You are the Project Manager for an AI Software Company.

Based on the CEO's project analysis below, create a detailed project plan with tasks, timeline estimates, and team assignments.

CEO PROJECT ANALYSIS:
{project_analysis}

Create a project plan with the following structure:

PROJECT PLAN
============

PROJECT NAME
[Extract from analysis]

OBJECTIVES
[List 3-5 key objectives]

DELIVERABLES
[What will be delivered]

TASKS
[Break down into phases with specific tasks]
Phase 1: Setup & Foundation
- Task 1: Description [2 days] [Team: Backend]
- Task 2: Description [3 days] [Team: Frontend]

Phase 2: Core Features
[Tasks...]

Phase 3: Integration
[Tasks...]

Phase 4: Testing & Deployment
[Tasks...]

TEAM STRUCTURE
- Backend: [Skills needed]
- Frontend: [Skills needed]
- DevOps: [Skills needed]
- QA: [Skills needed]

TIMELINE
Total estimated: [X] weeks

RISKS
- Risk 1: Description [Impact: High/Medium/Low]
- Risk 2: Description [Impact: High/Medium/Low]

DEPENDENCIES
- [List any task dependencies]

SUCCESS METRICS
- [How to measure success]

Important rules:
1. Use only information from the CEO analysis
2. Make realistic estimates
3. Break down large tasks into smaller ones
4. Consider dependencies between tasks
5. If something is unknown, say: "Not specified in project context"
"""

        result = await self.think_with_context(prompt)
        
        # Save to memory
        self.remember("pm_plan", result)
        memory.save("pm", result)
        workspace.save("project/pm_plan.md", result)
        
        return result
