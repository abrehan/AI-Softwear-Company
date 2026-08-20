from backend.app.agents.base_agent import BaseAgent
from backend.app.memory.project_memory import memory
from backend.app.workspace.workspace import workspace


class CTOAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            "CTO Agent",
            "Chief Technology Officer",
            agent_key="cto",
        )

        self.model = "llama3.2:3b"

    async def run(self, task: str):

        return await self.design_architecture(task)

    async def design_architecture(self, task: str):

        print("CTO Agent Started")

        authoritative_context = (
            self._load_authoritative_context()
        )

        ceo_summary = (
            memory.get("ceo") or ""
        )

        pm_plan = (
            memory.get("pm") or ""
        )

        controlled_context = f"""
===================================================
AUTHORITATIVE PROJECT CONTEXT
===================================================

{authoritative_context}

===================================================
CEO ANALYSIS
===================================================

{ceo_summary}

IMPORTANT:
CEO ANALYSIS is a decision input.
Its recommendations are NOT authoritative facts.

===================================================
PROJECT MANAGER PLAN
===================================================

{pm_plan}

IMPORTANT:
PROJECT MANAGER PLAN is a decision input.
Its recommendations are NOT authoritative facts.
"""

        prompt = f"""
You are the Chief Technology Officer of the AI Software Company.

ORIGINAL PROJECT REQUEST:

{task}

===================================================
STRICT FACTUALITY POLICY
===================================================

AUTHORITATIVE PROJECT CONTEXT is the only source of
confirmed project facts.

CEO and Project Manager outputs are decision inputs.

Do NOT automatically treat their recommendations as facts.

Never invent:

- budget
- deadlines
- dates
- KPIs
- customers
- employees
- revenue
- complexity
- completed work
- technical decisions
- required teams
- infrastructure
- deployment platforms

If information is not explicitly confirmed, write:

"Not provided in current project context."

Recommendations are allowed but MUST be clearly labeled
as recommendations.

Do not claim recommendations are completed work.

Do not use unrelated workspace files.

Do not modify source code.

The confirmed development direction MUST remain:

"The next development focus is to stabilize the Virtual AI
Office orchestration and context system before expanding
autonomous code generation."

Focus on stabilizing the existing orchestration and context
system before expanding autonomous code generation.

===================================================
CONTROLLED CONTEXT
===================================================

{controlled_context}

===================================================
OUTPUT FORMAT
===================================================

Return EXACTLY these sections:

# System Architecture

## Project Overview

## Confirmed Current Architecture

## Recommended Technology Architecture

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
- Context Management
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

## Orchestration Architecture

## Context Architecture

## Agent Responsibility Boundaries

## Testing Strategy

## Logging

## Risks

## Next Implementation Sequence

## Recommendations

Do not add extra sections.
"""

        result = await self.think_with_context(
            prompt,
            controlled_context=controlled_context,
        )

        self.remember(
            "cto",
            result,
        )

        memory.save(
            "cto",
            result,
        )

        workspace.save(
            "architecture/system_architecture.md",
            result,
        )

        print("Architecture saved")

        return result

    def _load_authoritative_context(self) -> str:

        context_file = (
            self.workspace
            / "project_context.md"
        )

        if not context_file.exists():

            return (
                "Not provided in current project context."
            )

        return context_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )
