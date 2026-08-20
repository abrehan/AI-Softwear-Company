from backend.app.agents.base_agent import BaseAgent
from backend.app.memory.project_memory import memory
from backend.app.workspace.workspace import workspace
from backend.app.agents.cto.cto_output_validator import validate_cto_output


class CTOAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "CTO Agent",
            "Chief Technology Officer",
            agent_key="cto",
        )

        # Explicit CTO model.
        self.model = "qwen2.5-coder:7b"

    async def run(self, task: str):
        return await self.design_architecture(task)

    async def design_architecture(self, task: str):

        print("CTO Agent Started")

        # =====================================================
        # AUTHORITATIVE CONTEXT
        # =====================================================

        authoritative_context = self._load_authoritative_context()

        if not authoritative_context.strip():
            authoritative_context = (
                "Not provided in current project context."
            )

        # =====================================================
        # DECISION INPUTS
        # =====================================================

        ceo_summary = memory.get("ceo") or (
            "Not provided in current project context."
        )

        pm_plan = memory.get("pm") or (
            "Not provided in current project context."
        )

        # Prevent unnecessarily huge prompts.
        authoritative_context = self._limit_context(
            authoritative_context,
            3000,
        )

        ceo_summary = self._limit_context(
            ceo_summary,
            1500,
        )

        pm_plan = self._limit_context(
            pm_plan,
            2000,
        )

        task = self._limit_context(
            task or "",
            1000,
        )

        print(
            "[CTO] Context sizes:",
            f"authoritative={len(authoritative_context):,}",
            f"ceo={len(ceo_summary):,}",
            f"pm={len(pm_plan):,}",
            f"task={len(task):,}",
        )

        # =====================================================
        # CONTROLLED DECISION CONTEXT
        # =====================================================

        controlled_context = f"""
AUTHORITATIVE PROJECT CONTEXT
==============================
{authoritative_context}

CEO DECISION INPUT
==================
{ceo_summary}

PROJECT MANAGER DECISION INPUT
==============================
{pm_plan}
"""

        # =====================================================
        # CTO PROMPT
        # =====================================================

        prompt = f"""
You are the Chief Technology Officer of the AI Software Company.

Produce ONLY the requested system architecture document.

============================================================
SOURCE OF TRUTH
============================================================

AUTHORITATIVE PROJECT CONTEXT is the ONLY source of confirmed
project facts.

CEO input and PM input are decision inputs only.

Generated content and generated files are NOT authoritative facts.

Never invent project facts.

If information is unknown, write exactly:

"Not provided in current project context."

============================================================
FACT CLASSIFICATION
============================================================

Only information explicitly supported by authoritative context
may be described as confirmed, current, existing, implemented,
or working.

Recommendations must be labeled Recommended, Proposed, Suggested,
or Should be evaluated.

The confirmed development direction is:

"The next development focus is to stabilize the Virtual AI Office
orchestration and context system before expanding autonomous code
generation."

This is development direction only and does NOT mean completed work.

============================================================
ARCHITECTURE RULES
============================================================

CONFIRMED CURRENT ARCHITECTURE:
Only include technology explicitly confirmed by authoritative context.

RECOMMENDED TECHNOLOGY ARCHITECTURE:
Unconfirmed technology must be written as:
"Recommended: ..."

Never present unconfirmed technology as existing infrastructure.

Never invent:
- database technology
- cloud provider
- infrastructure
- deployment status
- security implementation
- scalability implementation
- communication architecture
- authentication implementation
- completed work

Do not present PostgreSQL, Redis, Docker, Docker Compose, Kubernetes,
Jenkins, Prometheus, Grafana, Celery, HAProxy, OAuth2, HashiCorp Vault,
AES-256, vector databases, message brokers, API gateways, or microservices
as confirmed unless explicitly supported by authoritative context.

============================================================
AGENT RULE
============================================================

Do not invent detailed agent responsibilities.

If responsibility boundaries are not explicitly confirmed, write:

"Specific responsibility boundaries are not provided in current
project context."

============================================================
RISK RULE
============================================================

Do not invent confirmed risks.

If risks are not explicitly confirmed, write:

"Not provided in current project context."

Possible risks may only be presented as recommendations to evaluate.

============================================================
OUTPUT REQUIREMENT
============================================================

Return EXACTLY these sections:

# System Architecture

## Project Overview

## Confirmed Current Architecture

## Architecture Gaps

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
- State Management
- API Integration

### Data
- Database
- Persistence
- Caching
- File Storage

## Orchestration Architecture

## Context Architecture

## Agent Responsibility Boundaries

## Testing Strategy

## Logging

## Risks

## Next Implementation Sequence

## Recommendations

Do not omit required sections.

The implementation sequence is a PLAN. Never describe planned work
as completed.

============================================================
PROJECT REQUEST
============================================================

{task}

============================================================
{controlled_context}
============================================================
FINAL INSTRUCTION
============================================================

Produce the complete architecture document now.

Be concise.

Clearly distinguish confirmed facts from recommendations.
"""

        # =====================================================
        # GENERATE
        # =====================================================

        result = await self.think_with_context(
            prompt,
            controlled_context="",
        )

        result = (result or "").strip()

        # =====================================================
        # OLLAMA GENERATION FAILURE CHECK
        # =====================================================

        ollama_failure_markers = (
            "Ollama generation exceeded",
            "Ollama connection timed out",
            "Ollama is unavailable",
            "Ollama HTTP Error",
            "Unexpected Ollama Error",
        )

        if any(
            marker.lower() in result.lower()
            for marker in ollama_failure_markers
        ):
            print("=" * 70)
            print("CTO OLLAMA GENERATION FAILED")
            print("=" * 70)
            print(result)
            print("=" * 70)

            raise RuntimeError(
                f"CTO generation failed before validation: {result}"
            )



        if not result:
            raise RuntimeError(
                "CTO returned an empty architecture document."
            )

        # =====================================================
        # =====================================================
        # VALIDATE BEFORE PERSISTING
        # =====================================================

        max_validation_attempts = 3
        validation_errors = []

        for validation_attempt in range(1, max_validation_attempts + 1):

            print(
                f"[CTO] Output validation attempt "
                f"{validation_attempt}/{max_validation_attempts}"
            )

            validation_result = validate_cto_output(
                result,
                authoritative_context,
            )

            if isinstance(validation_result, tuple):
                validation_passed, validation_errors = validation_result
            else:
                validation_passed = bool(validation_result)
                validation_errors = []

            if validation_passed:
                print("CTO output validation: PASS")
                break

            print("CTO OUTPUT VALIDATION FAILED")

            if validation_errors:
                for error in validation_errors:
                    print(f"[CTO VALIDATION] {error}")

            if validation_attempt >= max_validation_attempts:
                raise RuntimeError(
                    "CTO output failed factuality validation after "
                    f"{max_validation_attempts} attempts: "
                    + "; ".join(str(e) for e in validation_errors)
                )

            correction_errors = "\n".join(
                f"- {error}"
                for error in validation_errors
            )

            correction_prompt = f"""
The previous CTO architecture response failed validation.

You MUST produce a corrected architecture document.

VALIDATION ERRORS:
{correction_errors}

STRICT REQUIREMENTS:

1. Return ALL required sections.
2. Use exactly the required section names.
3. Do not place unconfirmed technologies inside
   "## Confirmed Current Architecture".
4. Put unknown information in the appropriate section using exactly:
   "Not provided in current project context."
5. Risks that are not explicitly confirmed must say:
   "Not provided in current project context."
6. Do not invent agent responsibility boundaries.
7. Do not describe planned work as completed.
8. Recommended technologies MUST be explicitly labeled:
   "Recommended: ..."
9. Do not add extra sections.
10. Preserve the confirmed development direction exactly.

Return ONLY the corrected architecture document.

PREVIOUS CTO RESPONSE:
{result}
"""

            print("[CTO] Requesting corrected architecture from Ollama...")

            result = await self.think_with_context(
                correction_prompt,
                controlled_context=controlled_context,
            )

        else:
            raise RuntimeError(
                "CTO output validation failed unexpectedly."
            )

        # =====================================================
        # PERSIST
        # =====================================================

        self.remember("cto", result)

        memory.save("cto", result)

        workspace.save(
            "architecture/system_architecture.md",
            result,
        )

        print("Architecture saved")

        return result

    def _load_authoritative_context(self) -> str:

        context_file = self.workspace / "project_context.md"

        if not context_file.exists():
            return "Not provided in current project context."

        return context_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    @staticmethod
    def _limit_context(value: str, maximum: int) -> str:

        value = value or ""

        if len(value) <= maximum:
            return value

        return (
            value[:maximum]
            + "\n\n[Context truncated for CTO processing.]"
        )

