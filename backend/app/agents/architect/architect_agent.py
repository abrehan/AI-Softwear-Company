from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace

class ArchitectAgent(BaseAgent):
    """Architect Agent - Designs system architecture and technical solutions."""
    
    def __init__(self):
        super().__init__(
            "Architect Agent",
            "System Architect",
            agent_key="architect",
        )
        self.model = "llama3.2:3b"
    
    async def run(self, task: str):
        return await self.design_architecture(task)
    
    async def design_architecture(self, task: str):
        print("🏗️ Architect Agent: Designing architecture...")
        
        # Get context from memory
        ceo_summary = memory.get("ceo") or "Not provided"
        pm_plan = memory.get("pm") or "Not provided"
        cto_arch = memory.get("cto") or "Not provided"
        
        prompt = f"""
You are a Senior System Architect.

Based on the following information, design a comprehensive system architecture.

CEO ANALYSIS:
{ceo_summary}

PM PLAN:
{pm_plan}

CTO ARCHITECTURE:
{cto_arch}

ORIGINAL TASK:
{task}

Create a detailed architecture design with:

# System Architecture Design

## Overview
## Architecture Principles
## High-Level Architecture
## Component Breakdown
## Technology Stack
## Data Flow
## Security Architecture
## Scalability Strategy
## Performance Considerations
## Deployment Strategy
## Monitoring & Observability
## Disaster Recovery
## Future Considerations

Be specific and practical. Use real technologies where appropriate.
If information is unknown, say "Not provided in current project context."
"""

        result = await self.think_with_context(prompt)
        
        self.remember("architect", result)
        memory.save("architect", result)
        workspace.save("architecture/architect_design.md", result)
        
        print("💾 Architecture design saved")
        return result
