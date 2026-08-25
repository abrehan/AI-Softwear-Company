from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace

class DocumentationAgent(BaseAgent):
    """Documentation Agent - Creates comprehensive technical documentation."""
    
    def __init__(self):
        super().__init__(
            "Documentation Agent",
            "Technical Documentation Specialist",
            agent_key="documentation",
        )
        self.model = "llama3.2:3b"
    
    async def run(self, task: str):
        return await self.create_documentation(task)
    
    async def create_documentation(self, task: str):
        print("📚 Documentation Agent: Creating documentation...")
        
        # Get context from memory
        ceo_summary = memory.get("ceo") or "Not provided"
        pm_plan = memory.get("pm") or "Not provided"
        cto_arch = memory.get("cto") or "Not provided"
        backend_design = memory.get("backend") or "Not provided"
        frontend_design = memory.get("frontend") or "Not provided"
        database_design = memory.get("database") or "Not provided"
        
        prompt = f"""
You are a Senior Technical Documentation Specialist.

Based on the following information, create comprehensive technical documentation.

CEO ANALYSIS:
{ceo_summary}

PM PLAN:
{pm_plan}

CTO ARCHITECTURE:
{cto_arch}

BACKEND DESIGN:
{backend_design}

FRONTEND DESIGN:
{frontend_design}

DATABASE DESIGN:
{database_design}

ORIGINAL TASK:
{task}

Create complete technical documentation with:

# Technical Documentation

## Executive Summary
## System Overview
## Architecture Documentation
## API Documentation
## Database Documentation
## Frontend Documentation
## Deployment Guide
## User Guide
## Developer Guide
## Security Documentation
## Monitoring Guide
## Troubleshooting Guide
## FAQs
## Glossary

Make it comprehensive and user-friendly.
If information is unknown, say "Not provided in current project context."
"""

        result = await self.think_with_context(prompt)
        
        self.remember("documentation", result)
        memory.save("documentation", result)
        workspace.save("documentation/technical_docs.md", result)
        
        print("💾 Documentation saved")
        return result
