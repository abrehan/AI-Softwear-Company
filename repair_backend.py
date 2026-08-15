import asyncio
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, "backend")

from app.agents.backend.backend_agent import BackendAgent


async def main():

    agent = BackendAgent()

    root = Path("generated_code/backend")

    files = [
        root / "app/main.py",
        root / "app/models/project.py",
        root / "app/models/user.py",
        root / "app/schemas/project.py",
        root / "app/services/project_service.py",
        root / "app/services/user_service.py",
        root / "app/utils/helpers.py",
    ]

    for file in files:

        print("=" * 70)
        print("CHECKING:", file)
        print("=" * 70)

        code = file.read_text(encoding="utf-8")

        repaired_successfully = False

        for attempt in range(1, 4):

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "py_compile",
                    str(file)
                ],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                print("VALID:", file)
                repaired_successfully = True
                break

            error = result.stderr.strip()

            print("INVALID")
            print(error)
            print("REPAIR ATTEMPT:", attempt)

            repaired = await agent.repair_python(
                filepath=str(file),
                code=code,
                error=error,
                ceo_summary=agent.project_memory.read(
                    "requirements/project_summary.md"
                ),
                pm_plan=agent.project_memory.read(
                    "planning/project_plan.md"
                ),
                architecture=agent.project_memory.read(
                    "architecture/system_architecture.md"
                )
            )

            code = agent.clean_code(repaired)

            file.write_text(
                code,
                encoding="utf-8"
            )

        if not repaired_successfully:

            print("FAILED:", file)


asyncio.run(main())
