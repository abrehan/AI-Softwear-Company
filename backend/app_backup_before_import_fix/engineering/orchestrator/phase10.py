from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


class Phase10Orchestrator:
    """
    PHASE 10 — LOCAL AI ENGINEERING ORCHESTRATOR

    Pipeline:
        1. Verify Ollama
        2. Inspect generated project
        3. Run Phase 9 verification
        4. Ask local Ollama model for engineering analysis
        5. Write a structured Phase 10 JSON report

    Phase 10 is ANALYSIS ONLY.
    It does not modify project source code.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
        ollama_url: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5-coder:7b",
    ) -> None:
        self.project_root = Path(project_root).resolve()
        self.backend_root = self.project_root / "backend"

        self.ollama_url = ollama_url.rstrip("/")
        self.model = model

        # Canonical Phase 10 report location.
        #
        # D:\AI Softwear Company\backend
        #   generated\
        #       _code.qa\
        #           phase10\
        #               run\
        self.report_directory = (
            self.project_root.parent
            / "generated"
            / "_code.qa"
            / "phase10"
            / "run"
        )

        self.report_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.max_source_chars = 12000

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message: str) -> None:
        """Safe console logging for Windows."""
        text = str(message)

        try:
            print(text)
        except UnicodeEncodeError:
            print(
                text.encode(
                    "ascii",
                    errors="replace",
                ).decode("ascii")
            )

    # ---------------------------------------------------------
    # Ollama
    # ---------------------------------------------------------

    def check_ollama(self) -> dict[str, Any]:
        """Verify that Ollama is online and return available models."""

        url = f"{self.ollama_url}/api/tags"

        try:
            response = httpx.get(
                url,
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            models = [
                item.get("name")
                for item in data.get("models", [])
                if item.get("name")
            ]

            return {
                "success": True,
                "url": self.ollama_url,
                "models": models,
                "model_available": self.model in models,
            }

        except Exception as exc:
            return {
                "success": False,
                "url": self.ollama_url,
                "models": [],
                "model_available": False,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Project inspection
    # ---------------------------------------------------------

    def inspect_project(self) -> dict[str, Any]:
        """Inspect the generated backend without modifying it."""

        if not self.backend_root.exists():
            return {
                "success": False,
                "file_count": 0,
                "files": [],
                "error": (
                    f"Backend directory not found: "
                    f"{self.backend_root}"
                ),
            }

        files: list[str] = []

        excluded_directories = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
        }

        for path in self.backend_root.rglob("*"):
            if not path.is_file():
                continue

            relative = path.relative_to(
                self.backend_root
            )

            if any(
                part in excluded_directories
                for part in relative.parts
            ):
                continue

            files.append(str(relative))

        files.sort()

        return {
            "success": True,
            "file_count": len(files),
            "files": files[:500],
        }

    # ---------------------------------------------------------
    # Source collection
    # ---------------------------------------------------------

    def collect_source(self) -> str:
        """
        Collect a limited amount of source context
        for the local AI model.
        """

        candidates = [
            self.backend_root / "app" / "main.py",
            self.backend_root / "app" / "models" / "user.py",
        ]

        sections: list[str] = []

        for path in candidates:
            if not path.exists():
                continue

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            except Exception as exc:
                content = f"Unable to read file: {exc}"

            content = content[: self.max_source_chars]

            relative = path.relative_to(
                self.backend_root
            )

            sections.append(
                f"\n===== {relative} =====\n"
                f"{content}"
            )

        if not sections:
            return "No primary source files were found."

        return "\n".join(sections)

    # ---------------------------------------------------------
    # Phase 9
    # ---------------------------------------------------------

    def run_phase9(self) -> dict[str, Any]:
        """Run Phase 9 using the current Python interpreter."""

        self.log("Running Phase 9 verification...")

        command = [
            sys.executable,
            "-m",
            "app.engineering.orchestrator.phase9",
        ]

        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            result = subprocess.run(
                command,
                cwd=str(self.project_root.parent),
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
            )

            stdout = result.stdout or ""
            stderr = result.stderr or ""

            success_marker = (
                "Project is working correctly."
            )

            marker_found = success_marker in stdout

            success = (
                result.returncode == 0
                and marker_found
            )

            return {
                "success": success,
                "returncode": result.returncode,
                "marker_found": marker_found,
                "stdout": stdout[-12000:],
                "stderr": stderr[-12000:],
            }

        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""

            if isinstance(stdout, bytes):
                stdout = stdout.decode(
                    "utf-8",
                    errors="replace",
                )

            if isinstance(stderr, bytes):
                stderr = stderr.decode(
                    "utf-8",
                    errors="replace",
                )

            return {
                "success": False,
                "returncode": None,
                "marker_found": False,
                "stdout": stdout[-12000:],
                "stderr": stderr[-12000:],
                "error": "Phase 9 timed out after 180 seconds.",
            }

        except Exception as exc:
            return {
                "success": False,
                "returncode": None,
                "marker_found": False,
                "stdout": "",
                "stderr": "",
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # AI prompt
    # ---------------------------------------------------------

    def build_prompt(
        self,
        inspection: dict[str, Any],
        phase9: dict[str, Any],
    ) -> str:
        """Build a strict engineering-analysis prompt."""

        source = self.collect_source()

        phase9_success = phase9.get(
            "success",
            False,
        )

        phase9_errors = (
            phase9.get("stderr", "")
            or phase9.get("error", "")
        )

        return f"""
You are the local engineering safety analyst for an AI software company.

Your job is ANALYSIS ONLY.

Do NOT modify files.
Do NOT invent failures.
Use the supplied Phase 9 evidence.

Return EXACTLY these fields:

STATUS: HEALTHY
RISK: LOW
REPAIR_ALLOWED: YES

FINDINGS:

- None

RECOMMENDED_ACTIONS:

- NO REPAIR REQUIRED

REASON:

- The project is working correctly according to the available QA evidence.

Rules:

1. If Phase 9 succeeded and there are no demonstrated failures:
   STATUS should be HEALTHY.
   RISK should be LOW.
   REPAIR_ALLOWED should be YES.

2. If Phase 9 failed:
   Do not claim the project is healthy without evidence.

3. Never claim a source file was modified.

4. Do not invent test results.

PROJECT INSPECTION:
File count: {inspection.get("file_count", 0)}
Files:
{json.dumps(inspection.get("files", []), indent=2)}

PHASE 9 SUCCESS:
{phase9_success}

PHASE 9 ERRORS:
{phase9_errors[-4000:]}

SOURCE HIGHLIGHTS:
{source}
""".strip()

    # ---------------------------------------------------------
    # Ollama analysis
    # ---------------------------------------------------------

    def ask_ollama(
        self,
        prompt: str,
    ) -> dict[str, Any]:
        """Ask the local Ollama model for analysis."""

        url = f"{self.ollama_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 1200,
            },
        }

        try:
            response = httpx.post(
                url,
                json=payload,
                timeout=180,
            )

            response.raise_for_status()

            data = response.json()

            response_text = str(
                data.get("response", "")
            ).strip()

            return {
                "success": True,
                "model": self.model,
                "response": response_text,
            }

        except Exception as exc:
            return {
                "success": False,
                "model": self.model,
                "response": "",
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Report
    # ---------------------------------------------------------

    def create_report(
        self,
        ollama_status: dict[str, Any],
        inspection: dict[str, Any],
        phase9: dict[str, Any],
        ai_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Create the Phase 10 report."""

        phase9_success = bool(
            phase9.get("success", False)
        )

        ai_success = bool(
            ai_analysis.get("success", False)
        )

        report_success = (
            phase9_success
            and ai_success
        )

        return {
            "success": report_success,
            "stage": "phase10_completed",
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "ollama": ollama_status,
            "inspection": inspection,
            "phase9": phase9,
            "ai_analysis": ai_analysis,
            "auto_modify": False,
        }

    # ---------------------------------------------------------
    # Main pipeline
    # ---------------------------------------------------------

    def run(self) -> dict[str, Any]:
        """Execute the complete Phase 10 pipeline."""

        self.log("=" * 60)
        self.log(
            "PHASE 10 - LOCAL AI ENGINEERING ORCHESTRATOR"
        )
        self.log("=" * 60)

        self.log("Checking Ollama...")
        ollama_status = self.check_ollama()

        if ollama_status.get("success"):
            self.log(
                "Ollama online."
            )

            self.log(
                f"Models detected: "
                f"{len(ollama_status.get('models', []))}"
            )

            if not ollama_status.get(
                "model_available",
                False,
            ):
                self.log(
                    f"WARNING: Model {self.model} "
                    "was not found."
                )
        else:
            self.log(
                "Ollama is not available."
            )

        self.log(
            "Inspecting generated project..."
        )

        inspection = self.inspect_project()

        if not inspection.get("success"):
            self.log(
                f"Project inspection failed: "
                f"{inspection.get('error')}"
            )

        self.log(
            f"Files discovered: "
            f"{inspection.get('file_count', 0)}"
        )

        self.log(
            "Running Phase 9 verification..."
        )

        phase9 = self.run_phase9()

        if phase9.get("success"):
            self.log(
                "Phase 9 completed successfully."
            )
        else:
            self.log(
                "Phase 9 verification failed."
            )

        ai_analysis: dict[str, Any]

        if (
            ollama_status.get("success")
            and ollama_status.get(
                "model_available",
                False,
            )
        ):
            self.log(
                "Asking local AI engineer for analysis..."
            )

            prompt = self.build_prompt(
                inspection,
                phase9,
            )

            ai_analysis = self.ask_ollama(
                prompt
            )

        else:
            ai_analysis = {
                "success": False,
                "model": self.model,
                "response": "",
                "error": (
                    "Ollama unavailable or "
                    "requested model unavailable."
                ),
            }

        if ai_analysis.get("success"):
            self.log(
                "AI engineering analysis completed."
            )
        else:
            self.log(
                "AI engineering analysis failed."
            )

        report = self.create_report(
            ollama_status,
            inspection,
            phase9,
            ai_analysis,
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        report_path = (
            self.report_directory
            / f"phase10_{timestamp}.json"
        )

        report_path.write_text(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        self.log(
            f"Phase 10 report written to: "
            f"{report_path}"
        )

        self.log("=" * 60)
        self.log("FINAL PHASE 10 RESULT")
        self.log("=" * 60)

        self.log(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
            )
        )

        return report


def main() -> None:
    orchestrator = Phase10Orchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()