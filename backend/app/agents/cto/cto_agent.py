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

    async def run(self, task: str):
        return await self.design_architecture(task)

    async def design_architecture(self, task: str):

        print("CTO Agent Started")

        context = self._load_authoritative_context()
        context = self._limit_context(context, 900)

        ceo = self._limit_context(
            memory.get("ceo") or "Not provided in current project context.",
            350,
        )

        pm = self._limit_context(
            memory.get("pm") or "Not provided in current project context.",
            450,
        )

        task = self._limit_context(task or "", 300)

        prompt = f"""
You are the CTO of an AI Software Company.

Create a SHORT architecture document for the TARGET hotel booking project.

IMPORTANT:
The AI Software Company is the INTERNAL platform.
Do not confuse it with the hotel booking product.

ONLY the AUTHORITATIVE PROJECT CONTEXT confirms existing technology.

CEO and PM are inputs, not proof of existing infrastructure.

RULES:
- Never invent existing technology.
- Unknown information = Not provided in current project context.
- Proposed technology must begin with "Recommended:"
- Finish EVERY section.
- Do not stop halfway through a section.
- Do not repeat sections.
- Do not use bold text.
- Keep each section to 1-3 concise bullets.
- Maximum approximately 500 words.

REQUIRED FORMAT:

# System Architecture

## Project Overview
Brief project description.

## Confirmed Current Architecture
Only confirmed existing technology.

## Architecture Gaps
Only confirmed gaps.

## Recommended Technology Architecture
Recommended technologies only.

## Orchestration Architecture
Recommended architecture only unless confirmed.

## Context Architecture
Explain how project/agent context should be handled.

## Agent Responsibility Boundaries
Define boundaries only from available project context.

## Testing Strategy
Recommended testing approach.

## Logging
Recommended logging approach.

## Risks
List 3-4 concise risks.

## Next Implementation Sequence
List 5-7 concrete recommended steps.

## Recommendations
List 3-5 concrete recommendations.

AUTHORITATIVE PROJECT CONTEXT:
{context}

CEO INPUT:
{ceo}

PM INPUT:
{pm}

TASK:
{task}
"""

        result = await self.think(prompt)

        result = self._normalize(result)

        if not result:
            raise RuntimeError("CTO returned an empty architecture document.")

        result = self._ensure_sections(result)

        validation = validate_cto_output(
            result,
            context,
        )

        if isinstance(validation, tuple):
            passed, errors = validation
        else:
            passed = bool(validation)
            errors = []

        if not passed:
            print("CTO validation failed:")
            for error in errors:
                print(f"[CTO] {error}")

            raise RuntimeError(
                "CTO output failed validation: "
                + "; ".join(str(e) for e in errors)
            )

        self.remember("cto", result)
        memory.save("cto", result)

        workspace.save(
            "architecture/system_architecture.md",
            result,
        )

        architecture_file = (
            self.workspace
            / "architecture"
            / "system_architecture.md"
        )

        architecture_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        architecture_file.write_text(
            result,
            encoding="utf-8",
        )

        print(f"Architecture saved: {architecture_file}")

        return result

    def _load_authoritative_context(self):

        file = self.workspace / "project_context.md"

        if not file.exists():
            return "Not provided in current project context."

        return file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    @staticmethod
    def _limit_context(value, maximum):

        value = value or ""

        if len(value) <= maximum:
            return value

        return value[:maximum] + "\n[Context truncated.]"

    @staticmethod
    def _normalize(result):

        result = (result or "").strip()

        result = result.replace("\\r\\n", "\n")
        result = result.replace("\\n", "\n")
        result = result.replace("`r`n", "\n")
        result = result.replace("`n", "\n")

        result = re.sub(
            r"```(?:markdown|md)?",
            "",
            result,
            flags=re.IGNORECASE,
        )

        result = result.replace("```", "")

        result = re.sub(
            r"\*\*(.*?)\*\*",
            r"\1",
            result,
        )

        return result.strip()

    @staticmethod
    def _ensure_sections(result):

        sections = [
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

        # Normalize headings.
        for section in sections:
            result = re.sub(
                rf"^\s*\*{{0,2}}{re.escape(section)}\*{{0,2}}\s*$",
                section,
                result,
                flags=re.IGNORECASE | re.MULTILINE,
            )

        # Remove duplicate headings while keeping first occurrence.
        lines = result.splitlines()
        output = []
        seen = set()

        for line in lines:

            normalized = line.strip().lower()

            matched = None

            for section in sections:
                if normalized == section.lower():
                    matched = section
                    break

            if matched:
                key = matched.lower()

                if key in seen:
                    continue

                seen.add(key)
                output.append(matched)
            else:
                output.append(line)

        result = "\n".join(output).strip()

        # Add missing sections at the END only.
        for section in sections:

            if section.lower() not in result.lower():

                result += (
                    "\n\n"
                    + section
                    + "\n"
                    + "Not provided in current project context."
                )

        return result.strip()
