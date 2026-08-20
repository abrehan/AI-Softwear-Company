from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace

class DevAgent(BaseAgent):
    """Developer Agent - Generates code from project plans."""
    
    def __init__(self):
        super().__init__(
            "Dev Agent",
            "Developer",
            agent_key="dev",
        )
        self.model = "codellama:7b"
    
    async def run(self, task: str):
        return await self.generate_code(task)
    
    async def generate_code(self, project_plan: str):
        print("Dev Agent: Generating code...")
        
        prompt = f"""
You are a Senior Developer.

Based on the project plan below, generate production-ready code.

PROJECT PLAN:
{project_plan[:2000]}

Generate the most critical components first.
Use best practices and include proper error handling.
"""

        result = await self.think_with_context(prompt)
        
        self.remember("dev", result)
        memory.save("dev", result)
        workspace.save("code/generated_code.md", result)
        
        return result
