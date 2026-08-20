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
    PHASE 11 â€” CONTROLLED AUTONOMOUS REPAIR ENGINE

    Safety pipeline:

        Phase 10.1 PASSED
            â†“
        Create checkpoint
            â†“
        Ask local Ollama for repair plan
            â†“
        Validate proposed patch
            â†“
        Apply patch
            â†“
        Run Phase 6 QA
            â†“
        Run Phase 9 verification
            â†“
        PASS  -> keep changes
        FAIL  -> rollback checkpoint

    IMPORTANT:
    - Never modifies source unless Phase 10.1 allows repair.
    - Never modifies files outside the generated backend.
    - Never applies a patch unless the original text matches.
    - Automatically rolls back failed repairs.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
        ollama_url: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5-coder:7b",
    ):
        self.project_root = Path(project_root).resolve()
        self.backend_root = self.project_root / "backend"

        self.ollama_url = ollama_url.rstrip("/")
        self.model = model

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

        self.phase101_root = (
            self.qa_root
            / "phase10.1"
            / "hardening"
        )

        self.phase11_root = (
            self.qa_root
            / "phase11"
        )

        self.phase11_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        self.checkpoint_root = (
            self.phase11_root
            / f"checkpoint_{self.timestamp}"
        )

        self.report_file = (
            self.phase11_root
            / f"phase11_{self.timestamp}.json"
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
    # Latest Phase 10.1 report
    # ---------------------------------------------------------

    def find_latest_safety_report(self) -> Path | None:
        if not self.phase101_root.exists():
            return None

        reports = list(
            self.phase101_root.rglob("*.json")
        )

        if not reports:
            return None

        return max(
            reports,
            key=lambda p: p.stat().st_mtime,
        )

    # ---------------------------------------------------------
    # Safety gate
    # ---------------------------------------------------------

    def verify_safety_gate(self) -> dict[str, Any]:
        self.log("Checking Phase 10.1 safety gate...")

        report = self.find_latest_safety_report()

        if report is None:
            return {
                "success": False,
                "allowed": False,
                "error": (
                    "No Phase 10.1 safety report was found."
                ),
            }

        try:
            data = json.loads(
                report.read_text(
                    encoding="utf-8"
                )
            )
        except Exception as exc:
            return {
                "success": False,
                "allowed": False,
                "error": (
                    f"Unable to read safety report: {exc}"
                ),
            }

        gate = str(
            data.get("gate", "")
        ).upper()

        ai_status = str(
            data.get("ai_status", "")
        ).upper()

        phase10_success = bool(
            data.get(
                "phase10_success",
                False,
            )
        )

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
            and ai_status == "HEALTHY"
            and phase10_success
            and phase9_success
            and repair_allowed
        )

        return {
            "success": True,
            "allowed": allowed,
            "report": str(report),
            "gate": gate,
            "ai_status": ai_status,
            "phase10_success": phase10_success,
            "phase9_success": phase9_success,
            "repair_allowed": repair_allowed,
        }

    # ---------------------------------------------------------
    # Project inspection
    # ---------------------------------------------------------

    def inspect_project(self) -> dict[str, Any]:
        if not self.backend_root.exists():
            return {
                "success": False,
                "error": (
                    f"Backend does not exist: "
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
                ".venv",
                "node_modules",
            }

            if any(
                part in ignored
                for part in relative.parts
            ):
                continue

            files.append(
                str(relative)
            )

        return {
            "success": True,
            "file_count": len(files),
            "files": sorted(files)[:500],
        }

    # ---------------------------------------------------------
    # Source collection
    # ---------------------------------------------------------

    def collect_source(self) -> str:
        sections: list[str] = []

        allowed_extensions = {
            ".py",
            ".json",
            ".txt",
            ".md",
        }

        for path in self.backend_root.rglob("*"):
            if not path.is_file():
                continue

            relative = path.relative_to(
                self.backend_root
            )

            if any(
                part in {
                    ".git",
                    "__pycache__",
                    ".venv",
                    "node_modules",
                }
                for part in relative.parts
            ):
                continue

            if path.suffix.lower() not in allowed_extensions:
                continue

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            except Exception:
                continue

            sections.append(
                f"\n===== {relative} =====\n"
                f"{content[:12000]}"
            )

            if len(sections) >= 20:
                break

        if not sections:
            return "No source files found."

        return "\n".join(sections)

    # ---------------------------------------------------------
    # Checkpoint
    # ---------------------------------------------------------

    def create_checkpoint(self) -> dict[str, Any]:
        self.log("Creating Phase 11 source checkpoint...")

        if not self.backend_root.exists():
            return {
                "success": False,
                "error": "Backend directory does not exist.",
            }

        if self.checkpoint_root.exists():
            shutil.rmtree(
                self.checkpoint_root
            )

        shutil.copytree(
            self.backend_root,
            self.checkpoint_root,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                ".venv",
                "node_modules",
            ),
        )

        return {
            "success": True,
            "checkpoint": str(
                self.checkpoint_root
            ),
        }

    # ---------------------------------------------------------
    # Rollback
    # ---------------------------------------------------------

    def rollback(self) -> dict[str, Any]:
        self.log(
            "Rolling back Phase 11 changes..."
        )

        if not self.checkpoint_root.exists():
            return {
                "success": False,
                "error": (
                    "Checkpoint does not exist."
                ),
            }

        if self.backend_root.exists():
            shutil.rmtree(
                self.backend_root
            )

        shutil.copytree(
            self.checkpoint_root,
            self.backend_root,
        )

        return {
            "success": True,
            "restored": str(
                self.backend_root
            ),
        }

    # ---------------------------------------------------------
    # Ollama
    # ---------------------------------------------------------

    def ask_ollama(
        self,
        prompt: str,
    ) -> dict[str, Any]:

        url = (
            f"{self.ollama_url}/api/generate"
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 3000,
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

            return {
                "success": True,
                "model": self.model,
                "response": data.get(
                    "response",
                    "",
                ).strip(),
            }

        except Exception as exc:
            return {
                "success": False,
                "model": self.model,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Repair prompt
    # ---------------------------------------------------------

    def build_repair_prompt(
        self,
        inspection: dict[str, Any],
    ) -> str:

        source = self.collect_source()

        return f"""
You are a senior autonomous software engineer.

You are operating inside a controlled repair system.

Your job is NOT to rewrite the whole project.

Only propose a repair if a real defect exists.

Return ONLY valid JSON.

Required JSON structure:

{{
  "repair_required": false,
  "reason": "No repair required.",
  "confidence": 1.0,
  "patches": []
}}

If a repair is genuinely required:

{{
  "repair_required": true,
  "reason": "Explain the defect.",
  "confidence": 0.95,
  "patches": [
    {{
      "file": "app/example.py",
      "search": "EXACT ORIGINAL TEXT",
      "replace": "EXACT REPLACEMENT TEXT"
    }}
  ]
}}

STRICT SAFETY RULES:

1. Never invent files.
2. Never delete an entire file.
3. Never replace an entire project.
4. Never modify .git directories.
5. Never modify .venv.
6. Never modify node_modules.
7. Never use shell commands.
8. Never use PowerShell commands.
9. Never include markdown.
10. The "search" text MUST be exact source text.
11. Keep patches as small as possible.
12. If there is no real defect, return repair_required=false.
13. Do not change working code merely for style.
14. Confidence below 0.85 means repair_required=false.

PROJECT FILES:

{json.dumps(inspection.get("files", []), indent=2)}

SOURCE:

{source}
"""

    # ---------------------------------------------------------
    # Parse AI response
    # ---------------------------------------------------------

    def parse_ai_response(
        self,
        response: str,
    ) -> dict[str, Any]:

        text = response.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        try:
            data = json.loads(text)

        except json.JSONDecodeError as exc:
            return {
                "success": False,
                "error": (
                    "AI returned invalid JSON: "
                    f"{exc}"
                ),
            }

        if not isinstance(data, dict):
            return {
                "success": False,
                "error": (
                    "AI response must be a JSON object."
                ),
            }

        repair_required = bool(
            data.get(
                "repair_required",
                False,
            )
        )

        confidence = float(
            data.get(
                "confidence",
                0,
            )
        )

        patches = data.get(
            "patches",
            [],
        )

        if not isinstance(
            patches,
            list,
        ):
            return {
                "success": False,
                "error": (
                    "AI patches must be a list."
                ),
            }

        if (
            repair_required
            and confidence < 0.85
        ):
            return {
                "success": True,
                "repair_required": False,
                "reason": (
                    "AI confidence below "
                    "safe repair threshold."
                ),
                "confidence": confidence,
                "patches": [],
            }

        return {
            "success": True,
            "repair_required": repair_required,
            "reason": str(
                data.get(
                    "reason",
                    "",
                )
            ),
            "confidence": confidence,
            "patches": patches,
        }

    # ---------------------------------------------------------
    # Validate patch
    # ---------------------------------------------------------

    def validate_patch(
        self,
        patch: dict[str, Any],
    ) -> dict[str, Any]:

        file_name = patch.get(
            "file"
        )

        search = patch.get(
            "search"
        )

        replace = patch.get(
            "replace"
        )

        if not isinstance(
            file_name,
            str,
        ):
            return {
                "success": False,
                "error": "Patch file is invalid.",
            }

        if not isinstance(
            search,
            str,
        ):
            return {
                "success": False,
                "error": (
                    "Patch search text is invalid."
                ),
            }

        if not isinstance(
            replace,
            str,
        ):
            return {
                "success": False,
                "error": (
                    "Patch replacement text is invalid."
                ),
            }

        target = (
            self.backend_root
            / file_name
        ).resolve()

        try:
            target.relative_to(
                self.backend_root
            )
        except ValueError:
            return {
                "success": False,
                "error": (
                    "Patch attempts to escape "
                    "backend directory."
                ),
            }

        if not target.exists():
            return {
                "success": False,
                "error": (
                    f"Target file does not exist: "
                    f"{file_name}"
                ),
            }

        if target.is_dir():
            return {
                "success": False,
                "error": (
                    "Patch target is a directory."
                ),
            }

        if (
            ".git" in target.parts
            or ".venv" in target.parts
            or "node_modules" in target.parts
        ):
            return {
                "success": False,
                "error": (
                    "Protected directory cannot "
                    "be modified."
                ),
            }

        content = target.read_text(
            encoding="utf-8",
            errors="replace",
        )

        occurrences = content.count(
            search
        )

        if occurrences != 1:
            return {
                "success": False,
                "error": (
                    f"Search text must occur exactly "
                    f"once. Found {occurrences}."
                ),
            }

        return {
            "success": True,
            "target": target,
            "content": content,
            "search": search,
            "replace": replace,
        }

    # ---------------------------------------------------------
    # Apply one patch
    # ---------------------------------------------------------

    def apply_patch(
        self,
        patch: dict[str, Any],
    ) -> dict[str, Any]:

        validation = self.validate_patch(
            patch
        )

        if not validation["success"]:
            return validation

        target: Path = validation["target"]
        content: str = validation["content"]

        new_content = content.replace(
            validation["search"],
            validation["replace"],
            1,
        )

        target.write_text(
            new_content,
            encoding="utf-8",
        )

        return {
            "success": True,
            "file": str(target),
        }

    # ---------------------------------------------------------
    # Run Phase 6 QA
    # ---------------------------------------------------------

    def run_phase6(self) -> dict[str, Any]:

        self.log(
            "Running Phase 6 QA..."
        )

        command = [
            sys.executable,
            "-m",
            "app.engineering.qa.qa_runner",
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

            passed = (
                result.returncode == 0
                and
                "ALL PHASE 6 QA TESTS PASSED"
                in output
            )

            return {
                "success": passed,
                "returncode": result.returncode,
                "output": output[-12000:],
            }

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Run Phase 9
    # ---------------------------------------------------------

    def run_phase9(self) -> dict[str, Any]:

        self.log(
            "Running Phase 9 verification..."
        )

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

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": (
                    result.stdout or ""
                )[-12000:],
                "stderr": (
                    result.stderr or ""
                )[-12000:],
            }

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Main execution
    # ---------------------------------------------------------

    def run(self) -> dict[str, Any]:

        self.log("=" * 60)
        self.log(
            "PHASE 11 - CONTROLLED AUTONOMOUS REPAIR"
        )
        self.log("=" * 60)

        report: dict[str, Any] = {
            "success": False,
            "stage": "phase11_started",
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "auto_modify": False,
        }

        # -----------------------------------------------------
        # Safety gate
        # -----------------------------------------------------

        safety = self.verify_safety_gate()

        report["safety_gate"] = safety

        if not safety.get(
            "allowed",
            False,
        ):
            self.log(
                "BLOCKED: Phase 10.1 did not authorize repair."
            )

            report["stage"] = (
                "phase11_blocked"
            )

            report["reason"] = (
                "Phase 10.1 safety gate "
                "did not authorize modification."
            )

            self.report_file.write_text(
                json.dumps(
                    report,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return report

        self.log(
            "Phase 10.1 safety gate PASSED."
        )

        # -----------------------------------------------------
        # Inspect
        # -----------------------------------------------------

        inspection = (
            self.inspect_project()
        )

        report["inspection"] = inspection

        if not inspection["success"]:
            report["stage"] = (
                "inspection_failed"
            )

            self.report_file.write_text(
                json.dumps(
                    report,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return report

        # -----------------------------------------------------
        # Checkpoint
        # -----------------------------------------------------

        checkpoint = (
            self.create_checkpoint()
        )

        report["checkpoint"] = checkpoint

        if not checkpoint["success"]:
            report["stage"] = (
                "checkpoint_failed"
            )

            self.report_file.write_text(
                json.dumps(
                    report,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return report

        # -----------------------------------------------------
        # AI repair plan
        # -----------------------------------------------------

        self.log(
            "Asking local Ollama for a controlled repair plan..."
        )

        prompt = self.build_repair_prompt(
            inspection
        )

        ai_raw = self.ask_ollama(
            prompt
        )

        report["ai_raw"] = ai_raw

        if not ai_raw["success"]:
            report["stage"] = (
                "ai_analysis_failed"
            )

            self.report_file.write_text(
                json.dumps(
                    report,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return report

        ai_plan = self.parse_ai_response(
            ai_raw["response"]
        )

        report["ai_plan"] = ai_plan

        if not ai_plan["success"]:
            report["stage"] = (
                "invalid_ai_plan"
            )

            self.report_file.write_text(
                json.dumps(
                    report,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return report

        # -----------------------------------------------------
        # No repair needed
        # -----------------------------------------------------

        if not ai_plan[
            "repair_required"
        ]:

            self.log(
                "AI reports that no repair is required."
            )

            report["success"] = True
            report["stage"] = (
                "phase11_no_repair_required"
            )
            report["auto_modify"] = False

            self.report_file.write_text(
                json.dumps(
                    report,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return report

        # -----------------------------------------------------
        # Validate patch count
        # -----------------------------------------------------

        patches = ai_plan.get(
            "patches",
            [],
        )

        if not patches:
            report["stage"] = (
                "repair_plan_empty"
            )

            report["error"] = (
                "AI requested repair but supplied "
                "no patches."
            )

            self.report_file.write_text(
                json.dumps(
                    report,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return report

        if len(patches) > 10:
            report["stage"] = (
                "repair_plan_rejected"
            )

            report["error"] = (
                "Maximum of 10 patches allowed "
                "per Phase 11 cycle."
            )

            self.report_file.write_text(
                json.dumps(
                    report,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return report

        # -----------------------------------------------------
        # Apply patches
        # -----------------------------------------------------

        self.log(
            f"Applying {len(patches)} controlled patch(es)..."
        )

        applied: list[dict[str, Any]] = []

        for index, patch in enumerate(
            patches,
            start=1,
        ):

            self.log(
                f"Patch {index}/{len(patches)}..."
            )

            result = self.apply_patch(
                patch
            )

            if not result["success"]:

                self.log(
                    "Patch validation failed."
                )

                rollback = (
                    self.rollback()
                )

                report["patch_failure"] = (
                    result
                )

                report["rollback"] = (
                    rollback
                )

                report["stage"] = (
                    "patch_validation_failed"
                )

                self.report_file.write_text(
                    json.dumps(
                        report,
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                return report

            applied.append(
                result
            )

        report["applied_patches"] = applied
        report["auto_modify"] = True

        # -----------------------------------------------------
        # QA after repair
        # -----------------------------------------------------

        phase6 = self.run_phase6()

        report["phase6"] = phase6

        if not phase6["success"]:

            self.log(
                "Phase 6 FAILED. Rolling back..."
            )

            rollback = (
                self.rollback()
            )

            report["rollback"] = (
                rollback
            )

            report["stage"] = (
                "phase6_failed_rolled_back"
            )

            report["auto_modify"] = False

            self.report_file.write_text(
                json.dumps(
                    report,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return report

        # -----------------------------------------------------
        # Phase 9 after repair
        # -----------------------------------------------------

        phase9 = self.run_phase9()

        report["phase9"] = phase9

        if not phase9["success"]:

            self.log(
                "Phase 9 FAILED. Rolling back..."
            )

            rollback = (
                self.rollback()
            )

            report["rollback"] = (
                rollback
            )

            report["stage"] = (
                "phase9_failed_rolled_back"
            )

            report["auto_modify"] = False

            self.report_file.write_text(
                json.dumps(
                    report,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return report

        # -----------------------------------------------------
        # Successful repair
        # -----------------------------------------------------

        self.log(
            "Phase 11 repair passed QA and Phase 9."
        )

        report["success"] = True
        report["stage"] = (
            "phase11_repair_successful"
        )

        self.report_file.write_text(
            json.dumps(
                report,
                indent=2,
            ),
            encoding="utf-8",
        )

        self.log(
            f"Phase 11 report: {self.report_file}"
        )

        return report


def main() -> None:
    result = Phase11ControlledRepair().run()

    print("")
    print("=" * 60)
    print("FINAL PHASE 11 RESULT")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
