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
        # CTO PROMPT - EXPLICIT SECTION REQUIREMENTS
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
2. Use real newlines (\\n) NOT escaped characters
3. Keep each section concise but complete
4. If something is unknown, say EXACTLY: "Not provided in current project context."
5. For recommended technologies, explicitly label as: "Recommended: ..."
6. For risks, label as: "Risk: ..."

SOURCE OF TRUTH:
===============

AUTHORITATIVE PROJECT CONTEXT is the only source for confirmed project facts.
CEO and PM information are decision inputs only.

Never invent existing infrastructure. If unknown, say "Not provided in current project context."

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

REMEMBER: You MUST include ALL 13 sections listed above. Do not skip any.
"""
        # GENERATE
        # =====================================================

        result = await self.think_with_context(
            prompt,
            controlled_context="",
        )

        # =====================================================
        # NORMALIZE OLLAMA RESPONSE - COMPREHENSIVE FIX
        # =====================================================

        result = (result or "").strip()

        # CRITICAL: Ollama returns literal \n and `n sequences
        # These must be converted to real newlines BEFORE validation
        
        # First, handle escaped newline sequences
        # Using double backslash to match literal backslash-n
        result = result.replace("\\n", "\n")
        result = result.replace("\\r\\n", "\n")
        result = result.replace("\\r", "\n")
        
        # Handle PowerShell/backtick cases
        result = result.replace("`n", "\n")
        result = result.replace("`r`n", "\n")
        result = result.replace("`r", "\n")
        
        # Handle double escaped sequences
        result = result.replace("\\\\n", "\n")
        result = result.replace("\\\\r\\\\n", "\n")
        
        # Use regex to catch any remaining escaped newlines
        import re
        result = re.sub(r'\\n', '\n', result)
        result = re.sub(r'`n', '\n', result)
        
        # Remove Markdown code fences
        result = re.sub(r'```(?:markdown|md)?', '', result)
        result = result.replace('```', '')
        
        result = result.strip()

        # Debug: Show what we're working with
        print("\n" + "=" * 70)
        print("NORMALIZED OUTPUT CHECK:")
        print("-" * 70)
        if '\\n' in result:
            print("WARNING: Still contains \\n characters!")
        if '`n' in result:
            print("WARNING: Still contains `n characters!")
        else:
            print("No escaped newlines found - good!")
        print("=" * 70 + "\n")

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





















