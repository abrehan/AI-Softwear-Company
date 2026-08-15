from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class CTOAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "CTO Agent",
            "Chief Technology Officer"
        )

        self.model = "llama3.2:3b"

    async def run(self, task: str):
        return await self.design_architecture(task)

    async def design_architecture(self, task: str):

        print("🏗️ CTO Agent Started")

        # Read previous agents' work
        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""

        prompt = f"""
You are the Chief Technology Officer (CTO) of an AI Software Company.

Your responsibility is to design the complete software architecture.

===================================================
CEO PROJECT ANALYSIS
===================================================

{ceo_summary}

===================================================
PROJECT MANAGER PLAN
===================================================

{pm_plan}

===================================================
ORIGINAL PROJECT
===================================================

{task}

Create a complete technical architecture.

Return the result in Markdown.

# System Architecture

## Project Overview

## Recommended Technology Stack

### Backend
- Framework
- Language
- API Structure
- Authentication
- Business Logic
- AI Integration

### Frontend
- Framework
- UI Architecture
- Components
- State Management
- Routing

### Database
- Database Engine
- Tables
- Relationships
- Indexes

### Infrastructure
- Docker
- Docker Compose
- CI/CD
- Deployment
- Monitoring

### AI Layer
- LLM
- AI Agents
- Memory
- Vector Database

### Security
- Authentication
- Authorization
- Encryption
- Secrets Management

### Scalability
- Load Balancing
- Caching
- Background Jobs

### Testing Strategy

### Logging

### Folder Structure

### Development Workflow
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        # Save for other agents
        memory.save("cto", result)

        # Save Markdown document
        workspace.save(
            "architecture/system_architecture.md",
            result
        )

        print("💾 Architecture saved")

        return result