from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace
from app.agents.cto.cto_output_validator import validate_cto_output


class CTOAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "CTO Agent",
            "Chief Technology Officer",
            agent_key="cto",
        )

        # Explicit CTO model.
        self.model = "phi3.5:3.8b"

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
    700,
)

        ceo_summary = self._limit_context(
    ceo_summary,
    400,
)

        pm_plan = self._limit_context(
    pm_plan,
    500,
)

        task = self._limit_context(
    task or "",
    400,
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
AUTHORITATIVE PROJECT CONTEXT:
{authoritative_context}

CEO INPUT:
{ceo_summary}

PM INPUT:
{pm_plan}

TASK:
{task}
"""

        # =====================================================
        # CTO PROMPT
        # =====================================================

        prompt = f"""
You are the CTO of an AI Software Company.

Return ONLY concise architecture facts and recommendations.

Do NOT generate Markdown headings.

Do NOT generate a complete architecture document.

Do NOT use:
- literal `n
- literal \n
- escaped newline characters
- Markdown code fences

Use short plain-text statements only.

SOURCE OF TRUTH
===============

AUTHORITATIVE PROJECT CONTEXT is the only source for confirmed
project facts.

CEO and PM information are decision inputs only.

Never invent existing infrastructure.

If something is unknown, say exactly:

Not provided in current project context.

FACTUALITY
==========

Only explicitly confirmed technologies may be described as
existing, current, implemented, or working.

Everything else is a recommendation.

Never treat these as confirmed unless explicitly present in
AUTHORITATIVE PROJECT CONTEXT:

PostgreSQL
Redis
Docker
Docker Compose
Kubernetes
Jenkins
Prometheus
Grafana
Celery
OAuth
OAuth2
AWS
Azure
GCP
message broker
API gateway
microservices
HAProxy
Vault
AES-256

ARCHITECTURE GAPS
=================

Do not list technologies as gaps.

If information is unknown, simply say:

Not provided in current project context.

ORCHESTRATION
=============

Do not invent Kubernetes, Docker, message brokers, API gateways,
microservices, Celery, or other orchestration infrastructure.

If not confirmed, say:

Not provided in current project context.

RESPONSIBILITIES
================

Do not invent detailed agent responsibilities.

If not confirmed, say:

Specific responsibility boundaries are not provided in current project context.

RISKS
=====

Do not invent confirmed risks.

If risks are unknown, say:

Not provided in current project context.

PLANNING
========

The implementation sequence is a PLAN.

Never say that planned work is completed.

Return concise information only.

AUTHORITATIVE PROJECT CONTEXT
=============================

{authoritative_context}

CEO INPUT
=========

{ceo_summary}

PM INPUT
========

{pm_plan}

TASK
====

{task}
"""
        # GENERATE
        # =====================================================

        result = await self.think_with_context(
            prompt,
            controlled_context="",
        )

        
        # =====================================================
        # NORMALIZE OLLAMA OUTPUT
        # =====================================================

        result = (result or "").strip()

        # =====================================================
        # NORMALIZE OLLAMA RESPONSE
        # =====================================================

        # Convert escaped newline representations into real
        # newline characters before validation.
        result = result.replace("\\r\\n", "`n")
        result = result.replace("\\n", "`n")
        result = result.replace("\r\n", "`n")
        result = result.replace("`r`n", "`n")
        result = result.replace("`n", "`n")

        # Remove accidental Markdown code fences.
        result = result.replace("```markdown", "")
        result = result.replace("```md", "")
        result = result.replace("```", "")

        result = result.strip()

        # =====================================================
        # NORMALIZE OLLAMA RESPONSE
        # =====================================================

        # Convert escaped newline representations into real
        # newline characters before validation.
        result = result.replace("\\r\\n", "`n")
        result = result.replace("\\n", "`n")
        result = result.replace("\r\n", "`n")
        result = result.replace("`r`n", "`n")
        result = result.replace("`n", "`n")

        # Remove accidental Markdown code fences.
        result = result.replace("```markdown", "")
        result = result.replace("```md", "")
        result = result.replace("```", "")

        result = result.strip()

        # Ollama may return escaped newline sequences.
        # Convert them to real newline characters before validation.
        result = result.replace("\r\n", "`n")
        result = result.replace("\n", "`n")
        result = result.replace("`r`n", "`n")
        result = result.replace("`r", "`n")
        result = result.replace("`n", "`n")

        # Remove accidental Markdown fences.
        result = result.replace("```markdown", "")
        result = result.replace("```md", "")
        result = result.replace("```", "")

        result = result.strip()

        # =====================================================
        # DETERMINISTIC CTO OUTPUT NORMALIZATION
        # =====================================================

        required_defaults = {
            "## Architecture Gaps":
                "Not provided in current project context.",

            "## Testing Strategy":
                "Not provided in current project context.",

            "## Logging":
                "Not provided in current project context.",

            "## Risks":
                "Not provided in current project context.",

            "## Next Implementation Sequence":
                "1. Review the confirmed architecture and identified gaps.`n"
                "2. Stabilize orchestration and context handling.`n"
                "3. Validate the system before expanding autonomous capabilities.",

            "## Recommendations":
                "Not provided in current project context.",
        }

        required_headings = [
            "# System Architecture",
            "## Project Overview",
            "## Confirmed Current Architecture",
            "## Architecture Gaps",
            "## Recommended Technology Architecture",
            "## Orchestration Architecture",
            "## Context Architecture",
            "## Agent Responsibility Boundaries",
            "## Testing Strategy",
            "## Logging",
            "## Risks",
            "## Next Implementation Sequence",
            "## Recommendations",
        ]

        # Add missing mandatory sections.
        for heading in required_headings:

            if heading.lower() not in result.lower():

                default_text = required_defaults.get(
                    heading,
                    "Not provided in current project context.",
                )

                result += (
                    f"\n\n{heading}\n\n"
                    f"{default_text}"
                )

        # Architecture Gaps must explicitly identify unknowns.
        gaps_start = result.lower().find(
            "## architecture gaps".lower()
        )

        if gaps_start >= 0:

            next_section = result.lower().find(
                "## recommended technology architecture".lower(),
                gaps_start + len("## architecture gaps"),
            )

            if next_section < 0:
                next_section = len(result)

            gaps_section = result[
                gaps_start:next_section
            ]

            if (
                "not provided in current project context."
                not in gaps_section.lower()
            ):

                result = (
                    result[:next_section]
                    + "\nNot provided in current project context.\n"
                    + result[next_section:]
                )

        # Agent responsibility boundaries must be explicitly proposed
        # when they are not confirmed.
        responsibility_start = result.lower().find(
            "## agent responsibility boundaries".lower()
        )

        if responsibility_start >= 0:

            next_section = result.lower().find(
                "## testing strategy".lower(),
                responsibility_start + len(
                    "## agent responsibility boundaries"
                ),
            )

            if next_section < 0:
                next_section = len(result)

            responsibility_section = result[
                responsibility_start:next_section
            ]

            responsibility_lower = (
                responsibility_section.lower()
            )

            if (
                "recommended responsibility:" not in responsibility_lower
                and "proposed responsibility:" not in responsibility_lower
                and "confirmed" not in responsibility_lower
            ):

                result = (
                    result[:next_section]
                    + "\nProposed responsibility: "
                      "Not provided in current project context.\n"
                    + result[next_section:]
                )

        # Risks must either be unknown or explicitly recommended.
        risks_start = result.lower().find(
            "## risks".lower()
        )

        if risks_start >= 0:

            next_section = result.lower().find(
                "## next implementation sequence".lower(),
                risks_start + len("## risks"),
            )

            if next_section < 0:
                next_section = len(result)

            risks_section = result[
                risks_start:next_section
            ]

            risks_lower = risks_section.lower()

            if (
                "not provided in current project context."
                not in risks_lower
                and "recommended risk to evaluate:" not in risks_lower
            ):

                result = (
                    result[:next_section]
                    + "\nNot provided in current project context.\n"
                    + result[next_section:]
                )

        result = result.strip()

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

        # =====================================================
        # PERSIST ARCHITECTURE
        # =====================================================

        from pathlib import Path

        project_root = Path(__file__).resolve().parents[4]

        architecture_dir = (
            project_root
            / "workspace"
            / "architecture"
        )

        architecture_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        architecture_file = (
            architecture_dir
            / "system_architecture.md"
        )

        architecture_file.write_text(
            result,
            encoding="utf-8",
        )

        print(
            f"Architecture saved: {architecture_file}"
        )
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



















