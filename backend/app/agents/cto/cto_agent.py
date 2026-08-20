from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace
from app.agents.cto.cto_output_validator import validate_cto_output
import re


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
        # LOAD AUTHORITATIVE CONTEXT (FIRST!)
        # =====================================================

        authoritative_context = self._load_authoritative_context()

        if not authoritative_context.strip():
            authoritative_context = "Not provided in current project context."

        # =====================================================
        # LOAD DECISION INPUTS
        # =====================================================

        ceo_summary = memory.get("ceo") or "Not provided in current project context."
        pm_plan = memory.get("pm") or "Not provided in current project context."

        # Limit context sizes to prevent token overflow
        authoritative_context = self._limit_context(authoritative_context, 700)
        ceo_summary = self._limit_context(ceo_summary, 400)
        pm_plan = self._limit_context(pm_plan, 500)
        task = self._limit_context(task or "", 400)

        print(
            "[CTO] Context sizes:",
            f"authoritative={len(authoritative_context):,}",
            f"ceo={len(ceo_summary):,}",
            f"pm={len(pm_plan):,}",
            f"task={len(task):,}",
        )

        # =====================================================
        # BUILD CONTROLLED CONTEXT
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
        # BUILD PROMPT (AFTER ALL VARIABLES ARE DEFINED)
        # =====================================================

        prompt = f"""
You are the CTO of an AI Software Company.

You MUST generate a complete architecture document with ALL required sections listed below.

DO NOT skip any section. If information is unknown, write:
"Not provided in current project context."

REQUIRED SECTIONS (You MUST include ALL of these):
=================================================

# System Architecture
## Project Overview
## Confirmed Current Architecture
## Architecture Gaps
## Recommended Technology Architecture
## Orchestration Architecture
## Context Architecture
## Agent Responsibility Boundaries
## Testing Strategy
## Logging
## Risks
## Next Implementation Sequence
## Recommendations

INSTRUCTIONS:
=============

1. Write plain text only (NO Markdown formatting except for headings)
2. Use real newlines (NOT escaped characters like \\n or `n)
3. Keep each section concise but complete
4. If something is unknown, say EXACTLY: "Not provided in current project context."
5. For recommended technologies, explicitly label as: "Recommended: ..."
6. For risks, label as: "Risk: ..."

SOURCE OF TRUTH:
===============

AUTHORITATIVE PROJECT CONTEXT is the only source for confirmed project facts.
CEO and PM information are decision inputs only.

Never invent existing infrastructure. If unknown, say "Not provided in current project context."

PROJECT CONTEXT:
===============

{authoritative_context}

CEO INPUT:
=========

{ceo_summary}

PM INPUT:
========

{pm_plan}

TASK:
====

{task}

REMEMBER: You MUST include ALL 13 sections listed above. Do not skip any.
"""

        # =====================================================
        # GENERATE
        # =====================================================

        result = await self.think_with_context(
            prompt,
            controlled_context="",
        )

        # =====================================================
        # NORMALIZE OLLAMA RESPONSE
        # =====================================================

        result = (result or "").strip()

        # Convert escaped newlines to real newlines
        result = result.replace("\\n", "\n")
        result = result.replace("\\r\\n", "\n")
        result = result.replace("`n", "\n")
        result = result.replace("`r`n", "\n")

        # Remove markdown code fences
        result = re.sub(r'```(?:markdown|md)?', '', result)
        result = result.replace('```', '')
        result = result.strip()

        print("\n" + "=" * 70)
        print("NORMALIZED OUTPUT CHECK:")
        print("-" * 70)
        if '\\n' in result:
            print("WARNING: Still contains \\n characters!")
        if '`n' in result:
            print("WARNING: Still contains `n characters!")
        else:
            print("✓ No escaped newlines found")
        print("=" * 70 + "\n")

        # =====================================================
        # ENSURE ALL REQUIRED SECTIONS EXIST
        # =====================================================

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

        # Add any missing sections
        for heading in required_headings:
            if heading.lower() not in result.lower():
                result += f"\n\n{heading}\n\nNot provided in current project context."

        # =====================================================
        # OLLAMA FAILURE CHECK
        # =====================================================

        failure_markers = [
            "Ollama generation exceeded",
            "Ollama connection timed out",
            "Ollama is unavailable",
            "Ollama HTTP Error",
        ]

        if any(marker.lower() in result.lower() for marker in failure_markers):
            print("=" * 70)
            print("CTO OLLAMA GENERATION FAILED")
            print("=" * 70)
            print(result)
            print("=" * 70)
            raise RuntimeError(f"CTO generation failed: {result}")

        if not result:
            raise RuntimeError("CTO returned an empty architecture document.")

        # =====================================================
        # VALIDATE
        # =====================================================

        max_attempts = 3
        validation_errors = []

        for attempt in range(1, max_attempts + 1):
            print(f"[CTO] Output validation attempt {attempt}/{max_attempts}")

            validation_result = validate_cto_output(result, authoritative_context)

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

            if attempt >= max_attempts:
                raise RuntimeError(
                    f"CTO output failed validation after {max_attempts} attempts: "
                    + "; ".join(str(e) for e in validation_errors)
                )

            # Correction prompt
            correction_prompt = f"""
The previous CTO response failed validation.

VALIDATION ERRORS:
{chr(10).join(f'- {e}' for e in validation_errors)}

REQUIRED SECTIONS:
# System Architecture
## Project Overview
## Confirmed Current Architecture
## Architecture Gaps
## Recommended Technology Architecture
## Orchestration Architecture
## Context Architecture
## Agent Responsibility Boundaries
## Testing Strategy
## Logging
## Risks
## Next Implementation Sequence
## Recommendations

PROJECT CONTEXT:
{authoritative_context}

Return a corrected architecture document with ALL required sections.
Use "Not provided in current project context." for unknown information.

PREVIOUS RESPONSE:
{result}
"""

            print("[CTO] Requesting corrected architecture...")
            result = await self.think_with_context(correction_prompt, controlled_context=controlled_context)

            # Re-normalize
            result = (result or "").strip()
            result = result.replace("\\n", "\n")
            result = result.replace("`n", "\n")
            result = re.sub(r'```(?:markdown|md)?', '', result)
            result = result.replace('```', '')
            result = result.strip()

            # Re-add missing sections
            for heading in required_headings:
                if heading.lower() not in result.lower():
                    result += f"\n\n{heading}\n\nNot provided in current project context."

        # =====================================================
        # PERSIST
        # =====================================================

        self.remember("cto", result)
        memory.save("cto", result)

        from pathlib import Path
        project_root = Path(__file__).resolve().parents[4]
        architecture_dir = project_root / "workspace" / "architecture"
        architecture_dir.mkdir(parents=True, exist_ok=True)

        architecture_file = architecture_dir / "system_architecture.md"
        architecture_file.write_text(result, encoding="utf-8")

        print(f"Architecture saved: {architecture_file}")
        return result

    def _load_authoritative_context(self) -> str:
        context_file = self.workspace / "project_context.md"
        if not context_file.exists():
            return "Not provided in current project context."
        return context_file.read_text(encoding="utf-8", errors="ignore")

    @staticmethod
    def _limit_context(value: str, maximum: int) -> str:
        value = value or ""
        if len(value) <= maximum:
            return value
        return value[:maximum] + "\n\n[Context truncated for CTO processing.]"