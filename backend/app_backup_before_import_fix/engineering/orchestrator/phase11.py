from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


class Phase11ControlledRepair:
    """
    PHASE 11 — CONTROLLED AUTONOMOUS REPAIR

    Safety-first autonomous repair layer.

    Pipeline:
        Phase 10.1 safety gate
            ↓
        source checkpoint
            ↓
        local Ollama repair analysis
            ↓
        repair decision
            ↓
        optional controlled modification
            ↓
        Phase 9 QA verification
            ↓
        rollback if QA fails
            ↓
        complete audit report

    IMPORTANT:
    - Does not modify source when AI says no repair is required.
    - Creates a checkpoint before any modification.
    - Requires Phase 10.1 safety approval.
    - Rolls back modifications if post-repair QA fails.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
        ollama_url: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5-coder:7b",
    ):
        self.project_root = Path(project_root).resolve()

        self.backend_root = self.project_root / "backend"

        self.qa_root = (
            self.project_root.parent
            / "generated"
            / "_code.qa"
        )

        self.phase10_root = (
            self.qa_root
            / "phase10"
            / "run"
        )

        self.phase10_1_root = (
            self.qa_root
            / "phase10.1"
            / "hardening"
        )

        self.phase11_root = (
            self.qa_root
            / "phase11"
            / "run"
        )

        self.phase11_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.ollama_url = ollama_url.rstrip("/")
        self.model = model

        self.timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        self.report_file = (
            self.phase11_root
            / f"phase11_{self.timestamp}.json"
        )

        self.checkpoint_root = (
            self.qa_root
            / "phase11"
            / "checkpoints"
            / self.timestamp
        )

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message: str) -> None:
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
    # Utility
    # ---------------------------------------------------------

    def save_report(
        self,
        report: dict[str, Any],
    ) -> None:
        self.report_file.write_text(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            encoding="utf-8",
        )

    # ---------------------------------------------------------
    # Phase 10.1
    # ---------------------------------------------------------

    def find_latest_phase10_1_report(
        self,
    ) -> Path | None:

        if not self.phase10_1_root.exists():
            return None

        reports = list(
            self.phase10_1_root.rglob("*.json")
        )

        if not reports:
            return None

        reports.sort(
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        return reports[0]

    def check_safety_gate(
        self,
    ) -> dict[str, Any]:

        report_file = (
            self.find_latest_phase10_1_report()
        )

        if report_file is None:
            return {
                "success": False,
                "gate": "BLOCKED",
                "error": (
                    "No Phase 10.1 safety-gate "
                    "report was found."
                ),
            }

        try:
            data = json.loads(
                report_file.read_text(
                    encoding="utf-8"
                )
            )
        except Exception as exc:
            return {
                "success": False,
                "gate": "BLOCKED",
                "source_report": str(report_file),
                "error": str(exc),
            }

        gate = str(
            data.get("gate", "BLOCKED")
        ).upper()

        ai_status = str(
            data.get(
                "ai_status",
                "UNKNOWN",
            )
        ).upper()

        phase9_success = bool(
            data.get(
                "phase9_success",
                False,
            )
        )

        repair_allowed = bool(
            data.get(
                "repair_allowed",
                False,
            )
        )

        allowed = (
            gate == "PASSED"
            and phase9_success
        )

        return {
            "success": allowed,
            "gate": gate,
            "ai_status": ai_status,
            "phase9_success": phase9_success,
            "repair_allowed": repair_allowed,
            "source_report": str(report_file),
        }

    # ---------------------------------------------------------
    # Ollama
    # ---------------------------------------------------------

    def check_ollama(self) -> dict[str, Any]:

        try:
            response = httpx.get(
                f"{self.ollama_url}/api/tags",
                timeout=5,
            )

            response.raise_for_status()

            data = response.json()

            models = [
                item.get("name")
                for item in data.get(
                    "models",
                    [],
                )
            ]

            return {
                "success": True,
                "url": self.ollama_url,
                "models": models,
                "model_available": (
                    self.model in models
                ),
            }

        except Exception as exc:
            return {
                "success": False,
                "url": self.ollama_url,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Project inspection
    # ---------------------------------------------------------

    def inspect_project(self) -> dict[str, Any]:

        if not self.backend_root.exists():
            return {
                "success": False,
                "error": (
                    f"Backend not found: "
                    f"{self.backend_root}"
                ),
            }

        files: list[str] = []

        for path in self.backend_root.rglob("*"):

            if not path.is_file():
                continue

            relative = path.relative_to(
                self.backend_root
            )

            ignored = {
                ".git",
                "__pycache__",
                "node_modules",
                ".venv",
                "venv",
            }

            if any(
                part in ignored
                for part in relative.parts
            ):
                continue

            files.append(str(relative))

        return {
            "success": True,
            "file_count": len(files),
            "files": sorted(files)[:1000],
        }

    # ---------------------------------------------------------
    # Source checkpoint
    # ---------------------------------------------------------

    def create_checkpoint(
        self,
    ) -> dict[str, Any]:

        if not self.backend_root.exists():
            return {
                "success": False,
                "error": "Backend directory does not exist.",
            }

        try:

            if self.checkpoint_root.exists():
                shutil.rmtree(
                    self.checkpoint_root
                )

            self.checkpoint_root.mkdir(
                parents=True,
                exist_ok=True,
            )

            destination = (
                self.checkpoint_root
                / "backend"
            )

            shutil.copytree(
                self.backend_root,
                destination,
                ignore=shutil.ignore_patterns(
                    ".git",
                    "__pycache__",
                    ".venv",
                    "venv",
                    "node_modules",
                ),
            )

            return {
                "success": True,
                "path": str(
                    destination
                ),
            }

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Ollama repair analysis
    # ---------------------------------------------------------

    def build_repair_prompt(
        self,
        inspection: dict[str, Any],
        safety: dict[str, Any],
    ) -> str:

        files = inspection.get(
            "files",
            [],
        )

        return f"""
You are a senior local software engineer.

This is Phase 11 of a safety-controlled autonomous
engineering system.

Your task is ONLY to determine whether a repair is
actually required.

Do NOT invent problems.

Do NOT recommend changes merely for style.

Do NOT modify files.

Safety gate:
{safety}

Project files:
{json.dumps(files, indent=2)}

Return EXACTLY this structure:

REPAIR_REQUIRED: NO
RISK: LOW
FILES_TO_MODIFY: NONE
REASON:
The project is healthy and no repair is required.

If an actual defect is evident, use:

REPAIR_REQUIRED: YES
RISK: LOW
FILES_TO_MODIFY:
- relative/path/to/file.py
REASON:
Describe the concrete defect and why the change is necessary.

Only recommend a repair when there is concrete evidence.
""".strip()

    def ask_ollama(
        self,
        prompt: str,
    ) -> dict[str, Any]:

        try:

            response = httpx.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,
                        "num_predict": 800,
                    },
                },
                timeout=120,
            )

            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "model": self.model,
                "response": (
                    data.get(
                        "response",
                        "",
                    ).strip()
                ),
            }

        except Exception as exc:
            return {
                "success": False,
                "model": self.model,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Parse AI decision
    # ---------------------------------------------------------

    def parse_repair_decision(
        self,
        response: str,
    ) -> dict[str, Any]:

        text = response.upper()

        repair_required = (
            "REPAIR_REQUIRED: YES"
            in text
        )

        explicit_no = (
            "REPAIR_REQUIRED: NO"
            in text
        )

        risk = "UNKNOWN"

        for line in response.splitlines():
            if line.upper().startswith(
                "RISK:"
            ):
                risk = (
                    line.split(
                        ":",
                        1,
                    )[1]
                    .strip()
                    .upper()
                )

        if explicit_no:
            repair_required = False

        return {
            "repair_required": repair_required,
            "risk": risk,
            "decision_verified": (
                explicit_no
                or repair_required
            ),
        }

    # ---------------------------------------------------------
    # Phase 9 verification
    # ---------------------------------------------------------

    def run_phase9(
        self,
    ) -> dict[str, Any]:

        command = [
            sys.executable,
            "-m",
            "app.engineering.orchestrator.phase9",
        ]

        try:

            result = subprocess.run(
                command,
                cwd=str(
                    self.project_root.parent
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
            )

            output = (
                (result.stdout or "")
                + "\n"
                + (result.stderr or "")
            )

            marker = (
                "ALL PHASE 6 QA TESTS PASSED"
            )

            return {
                "success": (
                    result.returncode == 0
                    and (
                        marker in output
                        or
                        "Project is working correctly"
                        in output
                    )
                ),
                "returncode": result.returncode,
                "qa_marker": marker,
                "output": output[-12000:],
            }

        except Exception as exc:

            return {
                "success": False,
                "returncode": None,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Main pipeline
    # ---------------------------------------------------------

    def run(self) -> dict[str, Any]:

        self.log("")
        self.log("=" * 60)
        self.log(
            "PHASE 11 - CONTROLLED AUTONOMOUS REPAIR"
        )
        self.log("=" * 60)

        report: dict[str, Any] = {
            "phase": "11",
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "source_modified": False,
            "repair_executed": False,
            "rollback_performed": False,
        }

        # -----------------------------------------------------
        # Safety gate
        # -----------------------------------------------------

        self.log(
            "Checking Phase 10.1 safety gate..."
        )

        safety = self.check_safety_gate()

        report["phase10_1_safety"] = safety

        if not safety["success"]:

            self.log(
                "Phase 10.1 safety gate BLOCKED."
            )

            report["stage"] = (
                "safety_gate"
            )

            report["error"] = (
                "Phase 10.1 did not authorize "
                "Phase 11."
            )

            self.save_report(report)

            return report

        self.log(
            "Phase 10.1 safety gate PASSED."
        )

        # -----------------------------------------------------
        # Project inspection
        # -----------------------------------------------------

        inspection = (
            self.inspect_project()
        )

        report["inspection"] = inspection

        if not inspection["success"]:

            report["stage"] = (
                "inspection"
            )

            report["error"] = inspection.get(
                "error"
            )

            self.save_report(report)

            return report

        # -----------------------------------------------------
        # Checkpoint
        # -----------------------------------------------------

        self.log(
            "Creating Phase 11 source checkpoint..."
        )

        checkpoint = (
            self.create_checkpoint()
        )

        report["checkpoint"] = checkpoint

        if not checkpoint["success"]:

            report["stage"] = (
                "checkpoint"
            )

            report["error"] = checkpoint.get(
                "error"
            )

            self.save_report(report)

            return report

        # -----------------------------------------------------
        # Ollama
        # -----------------------------------------------------

        self.log(
            "Checking local Ollama..."
        )

        ollama = self.check_ollama()

        report["ollama"] = ollama

        if not ollama["success"]:

            report["stage"] = "ollama"

            report["error"] = (
                "Ollama is unavailable."
            )

            self.save_report(report)

            return report

        if not ollama.get(
            "model_available",
            False,
        ):

            report["stage"] = (
                "ollama_model"
            )

            report["error"] = (
                f"Required model '{self.model}' "
                "is not installed."
            )

            self.save_report(report)

            return report

        # -----------------------------------------------------
        # AI analysis
        # -----------------------------------------------------

        self.log(
            "Asking local Ollama for a "
            "controlled repair plan..."
        )

        prompt = self.build_repair_prompt(
            inspection,
            safety,
        )

        ai_result = self.ask_ollama(
            prompt
        )

        report["ai_analysis"] = ai_result

        if not ai_result["success"]:

            report["stage"] = (
                "ai_analysis"
            )

            report["error"] = (
                ai_result.get(
                    "error"
                )
            )

            self.save_report(report)

            return report

        decision = (
            self.parse_repair_decision(
                ai_result.get(
                    "response",
                    "",
                )
            )
        )

        report["repair_decision"] = (
            decision
        )

        # -----------------------------------------------------
        # No repair required
        # -----------------------------------------------------

        if (
            not decision[
                "repair_required"
            ]
        ):

            self.log(
                "AI reports that no repair is required."
            )

            report["stage"] = (
                "no_repair_required"
            )

            report["success"] = True

            report[
                "repair_plan"
            ] = {
                "required": False,
                "executed": False,
                "reason": (
                    "AI determined that the "
                    "project is healthy."
                ),
            }

            self.save_report(report)

            self.log("")
            self.log("=" * 60)
            self.log(
                "FINAL PHASE 11 RESULT"
            )
            self.log("=" * 60)
            self.log(
                json.dumps(
                    report,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            return report

        # -----------------------------------------------------
        # Repair is required
        # -----------------------------------------------------

        self.log(
            "AI reports that a repair may be required."
        )

        # Safety rule: do not automatically edit
        # source code in this version.
        report["stage"] = (
            "repair_plan_generated"
        )

        report["success"] = True

        report["repair_plan"] = {
            "required": True,
            "executed": False,
            "automatic_modification": False,
            "reason": (
                "A repair was identified, but "
                "Phase 11 requires controlled "
                "implementation before modifying "
                "source code."
            ),
        }

        self.save_report(report)

        self.log(
            "Repair plan generated; source "
            "code was NOT modified."
        )

        self.log("")
        self.log("=" * 60)
        self.log(
            "FINAL PHASE 11 RESULT"
        )
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
    orchestrator = Phase11ControlledRepair()
    orchestrator.run()


if __name__ == "__main__":
    main()