import json
import re
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

    async def develop_backend(self, task: str):

        print("⚙️ Backend Agent Started")

        ceo_summary = self.project_memory.read(
            "requirements/project_summary.md"
        )

        pm_plan = self.project_memory.read(
            "planning/project_plan.md"
        )

        architecture = self.project_memory.read(
            "architecture/system_architecture.md"
        )

        blueprint = self.project_memory.read(
            "planning/file_list.md"
        )

        try:
            blueprint = json.loads(blueprint)
            backend_files = blueprint.get("backend", [])

        except Exception:

            print("❌ Invalid blueprint.")

            backend_files = [
                "backend/app/main.py",
                "backend/requirements.txt"
            ]

        print(f"\n📋 Backend Files : {len(backend_files)}")

        generated = []

        for index, filepath in enumerate(backend_files, start=1):

            print("=" * 60)
            print(f"📄 {index}/{len(backend_files)}")
            print(filepath)
            print("=" * 60)

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

Generate ONLY this file.

Project Summary:
{ceo_summary}

Project Plan:
{pm_plan}

Architecture:
{architecture}

Target File:
{filepath}

Rules:

Generate ONLY this file.

No markdown.

No explanations.

No ```.

Start directly with code.
"""

                code = await self.think(prompt)

                code = re.sub(r"^```[a-zA-Z]*", "", code)
                code = re.sub(r"```$", "", code)
                code = code.replace("===END===", "").strip()

            # Save in workspace (memory)
            self.project_memory.write(filepath, code)

            # Save actual generated project
            output_file = Path("generated_code") / filepath

            output_file.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            output_file.write_text(
                code,
                encoding="utf-8"
            )

            print(f"✅ Saved {output_file}")

            generated.append(filepath)

        print("\n" + "=" * 60)
        print("✅ Backend Generation Complete")
        print("=" * 60)

        return generated
