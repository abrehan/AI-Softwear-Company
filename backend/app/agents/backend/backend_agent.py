import json
import re
import subprocess
import sys
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.generators.backend_generator import BackendGenerator
from app.generators.main_generator import MainGenerator


class BackendAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "backend",
            "Senior FastAPI Backend Engineer"
        )

    async def run(self, task: str):
        return await self.develop_backend(task)

    def clean_code(self, code: str) -> str:
        """
        Remove common Markdown/prose wrappers from AI-generated code.
        """
        code = str(code).strip()

        # Remove fenced Markdown blocks.
        code = re.sub(r"^```(?:python|py)?\s*", "", code, flags=re.IGNORECASE)
        code = re.sub(r"\s*```$", "", code)

        # Remove accidental END markers.
        code = code.replace("===END===", "").strip()

        return code

    def validate_python(self, filepath: Path):
        """
        Compile one generated Python file.
        Returns (True, "") when valid.
        """
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(filepath)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return True, ""

        error = result.stderr.strip()

        if not error:
            error = result.stdout.strip()

        return False, error

    async def repair_python(
        self,
        filepath: str,
        code: str,
        error: str,
        ceo_summary: str,
        pm_plan: str,
        architecture: str
    ):

        print(f"Repairing: {filepath}")

        prompt = f"""
You are a senior Python/FastAPI code repair engineer.

A previous AI generated this Python file:

FILE:
{filepath}

The file failed Python compilation.

COMPILER ERROR:
{error}

CURRENT CODE:
{code}

PROJECT CONTEXT:

CEO:
{ceo_summary}

PROJECT PLAN:
{pm_plan}

ARCHITECTURE:
{architecture}

TASK:

Repair the Python file.

STRICT RULES:

1. Return ONLY valid Python source code.
2. Do NOT return Markdown.
3. Do NOT use ``` fences.
4. Do NOT explain anything.
5. Preserve the intended functionality.
6. Fix the syntax/compiler error.
7. Make imports and FastAPI syntax valid.
8. Do not add unrelated functionality.

Return the complete corrected file.
"""

        repaired = await self.think(prompt)

        return self.clean_code(repaired)

    async def generate_file(
        self,
        filepath,
        task,
        ceo_summary,
        pm_plan,
        architecture
    ):

        if filepath.endswith("main.py"):

            generator = MainGenerator()

            code = await generator.generate(
                filepath=filepath,
                ceo_summary=ceo_summary,
                project_plan=pm_plan,
                architecture=architecture,
                task=task
            )

        else:

            prompt = f"""
You are a Senior FastAPI Backend Engineer.

Generate ONLY this Python file:

{filepath}

CEO PROJECT SUMMARY:
{ceo_summary}

PROJECT PLAN:
{pm_plan}

SYSTEM ARCHITECTURE:
{architecture}

TASK:
{task}

STRICT OUTPUT RULES:

Return ONLY the complete Python source code.

DO NOT:
- use Markdown
- use ``` fences
- explain the code
- describe the code
- add commentary
- output headings
- output "Here is the code"

Start immediately with valid Python source code.
"""

            code = await self.think(prompt)

        return self.clean_code(code)

    async def develop_backend(self, task: str):

        print("Backend Agent Started")

        ceo_summary = self.project_memory.read(
            "requirements/project_summary.md"
        )

        pm_plan = self.project_memory.read(
            "planning/project_plan.md"
        )

        architecture = self.project_memory.read(
            "architecture/system_architecture.md"
        )

        blueprint_text = self.project_memory.read(
            "planning/file_list.md"
        )

        try:

            blueprint = json.loads(blueprint_text)

            backend_files = blueprint.get(
                "backend",
                []
            )

        except Exception as exc:

            print(f"Invalid blueprint: {exc}")

            backend_files = [
                "backend/app/main.py",
                "backend/requirements.txt"
            ]

        print(
            f"Backend files approved: {len(backend_files)}"
        )

        generated = []

        output_root = Path("generated_code")

        output_root.mkdir(
            parents=True,
            exist_ok=True
        )

        for index, filepath in enumerate(
            backend_files,
            start=1
        ):

            print("=" * 60)
            print(
                f"Generating {index}/{len(backend_files)}"
            )
            print(filepath)
            print("=" * 60)

            code = await self.generate_file(
                filepath,
                task,
                ceo_summary,
                pm_plan,
                architecture
            )

            output_file = output_root / filepath

            output_file.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            output_file.write_text(
                code,
                encoding="utf-8"
            )

            # -------------------------------------------------
            # AUTOMATIC PYTHON VALIDATION + REPAIR
            # -------------------------------------------------

            max_repairs = 3

            for attempt in range(
                max_repairs + 1
            ):

                valid, error = self.validate_python(
                    output_file
                )

                if valid:

                    print(
                        f"VALID: {filepath}"
                    )

                    break

                print(
                    f"INVALID: {filepath}"
                )

                print(error)

                if attempt >= max_repairs:

                    raise RuntimeError(
                        f"Could not repair {filepath} "
                        f"after {max_repairs} attempts."
                    )

                code = await self.repair_python(
                    filepath=filepath,
                    code=code,
                    error=error,
                    ceo_summary=ceo_summary,
                    pm_plan=pm_plan,
                    architecture=architecture
                )

                output_file.write_text(
                    code,
                    encoding="utf-8"
                )

            # Save only validated code to project memory.
            self.project_memory.write(
                filepath,
                code
            )

            print(
                f"Saved: {output_file}"
            )

            generated.append(filepath)

        print()
        print("=" * 60)
        print("Backend Generation Complete")
        print("=" * 60)

        return generated


