from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional


class ProjectRunner:
    """
    Phase 4 - Step 1
    Generated FastAPI project runner and smoke tester.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
        timeout: int = 15,
    ):
        self.project_root = Path(project_root)
        self.timeout = timeout

    # ---------------------------------------------------------
    # Locate generated backend
    # ---------------------------------------------------------

    def find_backend(self) -> Optional[Path]:
        possible_paths = [
            self.project_root / "backend",
            self.project_root,
        ]

        for path in possible_paths:
            if not path.exists():
                continue

            main_file = path / "app" / "main.py"

            if main_file.exists():
                return path.resolve()

        return None

    # ---------------------------------------------------------
    # Find shared .venv
    # ---------------------------------------------------------

    def get_python_command(self, project_dir: Path) -> str:
        """
        Use the main AI Software Company .venv.

        Expected structure:

        backend/
        ├── .venv/
        ├── app/
        └── generated_code/
            └── backend/
        """

        backend_root = Path(__file__).resolve().parents[3]

        if os.name == "nt":
            venv_python = (
                backend_root
                / ".venv"
                / "Scripts"
                / "python.exe"
            )
        else:
            venv_python = (
                backend_root
                / ".venv"
                / "bin"
                / "python"
            )

        if venv_python.exists():
            return str(venv_python)

        return sys.executable

    # ---------------------------------------------------------
    # Validate requirements
    # ---------------------------------------------------------

    async def validate_requirements(
        self,
        project_dir: Path,
    ) -> dict:

        requirements = project_dir / "requirements.txt"

        if not requirements.exists():
            return {
                "success": False,
                "stage": "requirements",
                "error": "requirements.txt not found",
            }

        content = requirements.read_text(
            encoding="utf-8",
            errors="replace",
        )

        if not content.strip():
            return {
                "success": False,
                "stage": "requirements",
                "error": "requirements.txt is empty",
            }

        return {
            "success": True,
            "stage": "requirements",
            "file": str(requirements),
        }

    # ---------------------------------------------------------
    # Python syntax check
    # ---------------------------------------------------------

    async def validate_python(
        self,
        project_dir: Path,
    ) -> dict:

        python = self.get_python_command(project_dir)

        process = await asyncio.create_subprocess_exec(
            python,
            "-m",
            "compileall",
            "-q",
            "app",
            cwd=str(project_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        return {
            "success": process.returncode == 0,
            "stage": "syntax",
            "return_code": process.returncode,
            "stdout": stdout.decode(
                "utf-8",
                errors="replace",
            ),
            "stderr": stderr.decode(
                "utf-8",
                errors="replace",
            ),
        }

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    async def validate(self) -> dict:

        backend = self.find_backend()

        if backend is None:
            return {
                "success": False,
                "stage": "discovery",
                "error": (
                    "Generated backend not found. "
                    "Expected generated_code/backend/app/main.py"
                ),
            }

        print(f"📁 Backend: {backend}")

        requirements = await self.validate_requirements(
            backend
        )

        if not requirements["success"]:
            return requirements

        print("✅ requirements.txt found")

        syntax = await self.validate_python(
            backend
        )

        if not syntax["success"]:
            print("❌ Python syntax error")

            return syntax

        print("✅ Python syntax valid")

        return {
            "success": True,
            "stage": "validation",
            "project": str(backend),
        }

    # ---------------------------------------------------------
    # FastAPI smoke test
    # ---------------------------------------------------------

    async def run_backend(self) -> dict:

        backend = self.find_backend()

        if backend is None:
            return {
                "success": False,
                "stage": "discovery",
                "error": "Backend not found",
            }

        validation = await self.validate()

        if not validation["success"]:
            return validation

        python = self.get_python_command(backend)

        print(f"🐍 Python: {python}")
        print("🚀 Starting generated FastAPI backend...")

        process = await asyncio.create_subprocess_exec(
            python,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8765",
            cwd=str(backend),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout,
            )

            stdout_text = stdout.decode(
                "utf-8",
                errors="replace",
            )

            stderr_text = stderr.decode(
                "utf-8",
                errors="replace",
            )

            return {
                "success": process.returncode == 0,
                "stage": "runtime",
                "return_code": process.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
            }

        except asyncio.TimeoutError:

            print(
                f"⏱️ Backend stayed alive for "
                f"{self.timeout} seconds."
            )

            try:
                process.terminate()
                await asyncio.wait_for(
                    process.wait(),
                    timeout=5,
                )

            except Exception:

                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass

            return {
                "success": True,
                "stage": "runtime",
                "port": 8765,
                "message": (
                    "FastAPI application started and "
                    "remained running during smoke test."
                ),
            }

    # ---------------------------------------------------------
    # Public runner
    # ---------------------------------------------------------

    async def run(self) -> dict:

        print("=" * 60)
        print("🚀 PHASE 4 — PROJECT RUNNER")
        print("=" * 60)

        result = await self.run_backend()

        print()

        if result.get("success"):
            print("✅ Project Runner PASSED")
        else:
            print("❌ Project Runner FAILED")

        print("=" * 60)

        return result


# -------------------------------------------------------------
# Manual execution
# -------------------------------------------------------------

async def main():

    runner = ProjectRunner()

    result = await runner.run()

    print()
    print("RESULT:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())