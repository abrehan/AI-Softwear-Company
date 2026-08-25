from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace
from pathlib import Path

class FileGeneratorAgent(BaseAgent):
    """File Generator Agent - Generates project files and directory structures."""
    
    def __init__(self):
        super().__init__(
            "File Generator Agent",
            "File Generator",
            agent_key="file_generator",
        )
        self.model = "llama3.2:3b"
    
    async def run(self, task: str):
        return await self.generate_files(task)
    
    async def generate_files(self, task: str):
        print("📄 File Generator Agent: Generating files...")
        
        # Get context from memory
        ceo_summary = memory.get("ceo") or "Not provided"
        pm_plan = memory.get("pm") or "Not provided"
        file_plan = memory.get("file_planner") or "Not provided"
        
        prompt = f"""
You are a File Generation Specialist.

Based on the following information, generate a complete file structure and file contents.

CEO ANALYSIS:
{ceo_summary}

PM PLAN:
{pm_plan}

FILE PLAN:
{file_plan}

ORIGINAL TASK:
{task}

Generate:

# Project File Structure

## Directory Structure
[Show complete directory tree]

## Configuration Files
[Content of config files]

## Source Code Files
[Main source files]

## Test Files
[Test file structure]

## Documentation Files
[Doc file structure]

## Deployment Files
[Deployment files]

## README Files
[Readme content]

Create a realistic and complete file structure for the project.
If information is unknown, use standard best practices.
"""

        result = await self.think_with_context(prompt)
        
        self.remember("file_generator", result)
        memory.save("file_generator", result)
        workspace.save("files/generated_file_structure.md", result)
        
        print("💾 File structure saved")
        return result
