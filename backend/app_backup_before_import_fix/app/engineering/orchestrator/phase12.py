from __future__ import annotations

import difflib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


class Phase12ControlledRepairExecutor:
    """
    PHASE 12 â€” CONTROLLED AUTONOMOUS REPAIR EXECUTOR

    Safety-first repair execution layer.

    Pipeline:

        Phase 10.1 Safety Gate
                |
                v
        Phase 11 Repair Plan
                |
                v
        Source Checkpoint
                |
                v
        AI Repair Proposal
                |
                v
        File/Path Validation
                |
                v
        Dry Run / Controlled Apply
                |
                v
        Python Syntax Validation
                |
                v
        Phase 6 / Phase 9 QA
                |
          +-----+-----+
          |           |
        PASS         FAIL
          |           |
          v           v
       Keep       Rollback
          |
          v
       Audit Report

    IMPORTANT SAFETY RULES:

    1. Phase 10.1 must be PASSED.
    2. Phase 11 must explicitly require a repair.
    3. Only files explicitly listed by the repair plan may be modified.
    4. Absolute paths are rejected.
    5. Paths escaping backend_root are rejected.
    6. .git, virtual environments and generated caches are protected.
    7. Dry-run mode is enabled by default.
    8. No arbitrary shell commands from Ollama are executed.
    9. A checkpoint is created before modification.
    10. Syntax validation occurs after modification.
    11. Phase 9 QA occurs after modification.
    12. Failed repairs are automatically rolled back.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
        ollama_url: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5-coder:7b",
        dry_run: bool = True,
    ):
        self.project_root = Path(
            project_root
        ).resolve()

        self.backend_root = (
            self.project_root / "backend"
        )

        self.qa_root = (
            self.project_root.parent
            / "generated"
            / "_code.qa"
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

        self.phase12_root = (
            self.qa_root
            / "phase12"
            / "run"
        )

        self.checkpoint_root = (
            self.qa_root
            / "phase12"
            / "checkpoints"
        )

        self.phase12_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.checkpoint_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.ollama_url = (
            ollama_url.rstrip("/")
        )

        self.model = model

        self.dry_run = dry_run

        self.timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        self.report_file = (
            self.phase12_root
            / f"phase12_{self.timestamp}.json"
        )

        self.current_checkpoint = (
            self.checkpoint_root
            / self.timestamp
        )

    # =========================================================
    # LOGGING
    # =========================================================

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

    # =========================================================
    # REPORT
    # =========================================================

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

    # =========================================================
    # FIND LATEST JSON
    # =========================================================

    @staticmethod
    def latest_json(
        root: Path,
    ) -> Path | None:

        if not root.exists():
            return None

        files = list(
            root.rglob("*.json")
        )

        if not files:
            return None

        files.sort(
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        return files[0]

    # =========================================================
    # PHASE 10.1 SAFETY GATE
    # =========================================================

    def check_phase10_1(
        self,
    ) -> dict[str, Any]:

        report = self.latest_json(
            self.phase10_1_root
        )

        if report is None:
            return {
                "success": False,
                "gate": "BLOCKED",
                "error": (
                    "No Phase 10.1 report found."
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
                "gate": "BLOCKED",
                "source_report": str(report),
                "error": str(exc),
            }

        gate = str(
            data.get(
                "gate",
                "BLOCKED",
            )
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
            and repair_allowed
        )

        return {
            "success": allowed,
            "gate": gate,
            "ai_status": ai_status,
            "phase9_success": phase9_success,
            "repair_allowed": repair_allowed,
            "source_report": str(report),
        }

    # =========================================================
    # PHASE 11 REPAIR PLAN
    # =========================================================

    def check_phase11(
        self,
    ) -> dict[str, Any]:

        report = self.latest_json(
            self.phase11_root
        )

        if report is None:
            return {
                "success": False,
                "error": (
                    "No Phase 11 report found."
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
                "source_report": str(report),
                "error": str(exc),
            }

        decision = data.get(
            "repair_decision",
            {},
        )

        repair_plan = data.get(
            "repair_plan",
            {},
        )

        repair_required = bool(
            decision.get(
                "repair_required",
                repair_plan.get(
                    "required",
                    False,
                ),
            )
        )

        return {
            "success": bool(
                data.get(
                    "success",
                    False,
                )
            ),
            "repair_required": repair_required,
            "repair_decision": decision,
            "repair_plan": repair_plan,
            "source_report": str(report),
            "raw_report": data,
        }

    # =========================================================
    # PROJECT INSPECTION
    # =========================================================

    def inspect_project(
        self,
    ) -> dict[str, Any]:

        if not self.backend_root.exists():
            return {
                "success": False,
                "error": (
                    f"Backend directory does not "
                    f"exist: {self.backend_root}"
                ),
            }

        files: list[str] = []

        ignored = {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
        }

        for path in self.backend_root.rglob("*"):

            if not path.is_file():
                continue

            relative = path.relative_to(
                self.backend_root
            )

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
            "files": sorted(files)[:2000],
        }

    # =========================================================
    # CHECKPOINT
    # =========================================================

    def create_checkpoint(
        self,
    ) -> dict[str, Any]:

        if not self.backend_root.exists():
            return {
                "success": False,
                "error": (
                    "Backend directory does not exist."
                ),
            }

        try:

            if self.current_checkpoint.exists():
                shutil.rmtree(
                    self.current_checkpoint
                )

            self.current_checkpoint.mkdir(
                parents=True,
                exist_ok=True,
            )

            destination = (
                self.current_checkpoint
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

    # =========================================================
    # PROTECTED PATH VALIDATION
    # =========================================================

    def validate_relative_path(
        self,
        relative_path: str,
    ) -> tuple[bool, str, Path | None]:

        if not relative_path:
            return (
                False,
                "Empty file path.",
                None,
            )

        path_text = str(
            relative_path
        ).strip()

        path_text = path_text.replace(
            "\\",
            "/",
        )

        candidate = Path(
            path_text
        )

        if candidate.is_absolute():
            return (
                False,
                "Absolute paths are not allowed.",
                None,
            )

        if ":" in path_text:
            return (
                False,
                "Drive-qualified paths are not allowed.",
                None,
            )

        if path_text.startswith(
            "../"
        ) or "/../" in path_text:

            return (
                False,
                "Path traversal is not allowed.",
                None,
            )

        try:

            resolved = (
                self.backend_root
                / candidate
            ).resolve()

            resolved.relative_to(
                self.backend_root
            )

        except ValueError:

            return (
                False,
                "Path escapes backend root.",
                None,
            )

        protected_parts = {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
        }

        relative_parts = set(
            candidate.parts
        )

        if protected_parts.intersection(
            relative_parts
        ):
            return (
                False,
                "Protected directory.",
                None,
            )

        return (
            True,
            "Path accepted.",
            resolved,
        )

    # =========================================================
    # EXTRACT FILES FROM PHASE 11 PLAN
    # =========================================================

    def extract_files_to_modify(
        self,
        phase11: dict[str, Any],
    ) -> list[str]:

        decision = phase11.get(
            "repair_decision",
            {},
        )

        plan = phase11.get(
            "repair_plan",
            {},
        )

        candidates: list[Any] = []

        for source in (
            decision,
            plan,
        ):

            value = source.get(
                "files_to_modify"
            )

            if isinstance(
                value,
                list,
            ):
                candidates.extend(
                    value
                )

        response = ""

        ai_analysis = phase11.get(
            "ai_analysis",
            {},
        )

        if isinstance(
            ai_analysis,
            dict,
        ):
            response = ai_analysis.get(
                "response",
                "",
            )

        # Parse simple bullet paths from AI
        # response when structured field is absent.
        if response:

            collecting = False

            for line in response.splitlines():

                stripped = line.strip()

                if stripped.upper().startswith(
                    "FILES_TO_MODIFY:"
                ):
                    collecting = True
                    continue

                if collecting:

                    if not stripped:
                        continue

                    if stripped.upper().startswith(
                        "REASON:"
                    ):
                        collecting = False
                        continue

                    if stripped.startswith("-"):
                        value = stripped[1:].strip()

                        if (
                            value
                            and value.upper()
                            != "NONE"
                        ):
                            candidates.append(
                                value
                            )

        cleaned: list[str] = []

        for item in candidates:

            if not isinstance(
                item,
                str,
            ):
                continue

            value = item.strip()

            if (
                value
                and value.upper()
                not in {
                    "NONE",
                    "N/A",
                }
                and value not in cleaned
            ):
                cleaned.append(
                    value
                )

        return cleaned

    # =========================================================
    # READ FILE
    # =========================================================

    @staticmethod
    def read_text(
        path: Path,
    ) -> str:

        try:
            return path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            return path.read_text(
                encoding="utf-8",
                errors="replace",
            )

    # =========================================================
    # FILE SNAPSHOT
    # =========================================================

    def snapshot_files(
        self,
        files: list[Path],
    ) -> dict[str, str]:

        snapshot: dict[str, str] = {}

        for path in files:

            if path.exists() and path.is_file():

                relative = str(
                    path.relative_to(
                        self.backend_root
                    )
                )

                snapshot[
                    relative
                ] = self.read_text(path)

        return snapshot

    # =========================================================
    # DIFF
    # =========================================================

    def create_diff(
        self,
        before: str,
        after: str,
        relative_path: str,
    ) -> str:

        return "".join(
            difflib.unified_diff(
                before.splitlines(
                    keepends=True
                ),
                after.splitlines(
                    keepends=True
                ),
                fromfile=(
                    f"a/{relative_path}"
                ),
                tofile=(
                    f"b/{relative_path}"
                ),
            )
        )

    # =========================================================
    # SYNTAX VALIDATION
    # =========================================================

    def run_python_syntax_check(
        self,
    ) -> dict[str, Any]:

        if not self.backend_root.exists():
            return {
                "success": False,
                "error": (
                    "Backend directory missing."
                ),
            }

        python_files = list(
            self.backend_root.rglob(
                "*.py"
            )
        )

        python_files = [
            p
            for p in python_files
            if not any(
                part in {
                    ".venv",
                    "venv",
                    "__pycache__",
                    "node_modules",
                }
                for part in p.parts
            )
        ]

        failures: list[dict[str, Any]] = []

        for path in python_files:

            try:

                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "py_compile",
                        str(path),
                    ],
                    cwd=str(
                        self.backend_root
                    ),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=30,
                )

                if result.returncode != 0:

                    failures.append(
                        {
                            "file": str(
                                path.relative_to(
                                    self.backend_root
                                )
                            ),
                            "returncode": (
                                result.returncode
                            ),
                            "stderr": (
                                result.stderr[-4000:]
                            ),
                        }
                    )

            except Exception as exc:

                failures.append(
                    {
                        "file": str(
                            path.relative_to(
                                self.backend_root
                            )
                        ),
                        "error": str(exc),
                    }
                )

        return {
            "success": not failures,
            "checked_files": len(
                python_files
            ),
            "failures": failures,
        }

    # =========================================================
    # PHASE 9
    # =========================================================

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

            return {
                "success": (
                    result.returncode == 0
                    and (
                        "Project is working correctly"
                        in output
                        or
                        "ALL PHASE 6 QA TESTS PASSED"
                        in output
                    )
                ),
                "returncode": result.returncode,
                "output": output[-12000:],
            }

        except Exception as exc:

            return {
                "success": False,
                "returncode": None,
                "error": str(exc),
            }

    # =========================================================
    # ROLLBACK
    # =========================================================

    def rollback(
        self,
    ) -> dict[str, Any]:

        source = (
            self.current_checkpoint
            / "backend"
        )

        if not source.exists():
            return {
                "success": False,
                "error": (
                    "Checkpoint backend does not exist."
                ),
            }

        try:

            if self.backend_root.exists():
                shutil.rmtree(
                    self.backend_root
                )

            shutil.copytree(
                source,
                self.backend_root,
            )

            return {
                "success": True,
                "restored_from": str(
                    source
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "error": str(exc),
            }

    # =========================================================
    # MAIN
    # =========================================================

    def run(self) -> dict[str, Any]:

        self.log("")
        self.log("=" * 60)
        self.log(
            "PHASE 12 - CONTROLLED AUTONOMOUS REPAIR EXECUTOR"
        )
        self.log("=" * 60)

        report: dict[str, Any] = {
            "phase": "12",
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "dry_run": self.dry_run,
            "source_modified": False,
            "repair_executed": False,
            "rollback_performed": False,
        }

        # -----------------------------------------------------
        # Phase 10.1
        # -----------------------------------------------------

        self.log(
            "Checking Phase 10.1 safety gate..."
        )

        safety = self.check_phase10_1()

        report[
            "phase10_1_safety"
        ] = safety

        if not safety["success"]:

            self.log(
                "Phase 10.1 safety gate BLOCKED."
            )

            report["stage"] = (
                "phase10_1_gate"
            )

            report["error"] = (
                "Phase 10.1 did not authorize "
                "repair execution."
            )

            self.save_report(report)

            return report

        self.log(
            "Phase 10.1 safety gate PASSED."
        )

        # -----------------------------------------------------
        # Phase 11
        # -----------------------------------------------------

        self.log(
            "Checking Phase 11 repair plan..."
        )

        phase11 = self.check_phase11()

        report[
            "phase11_plan"
        ] = {
            key: value
            for key, value
            in phase11.items()
            if key != "raw_report"
        }

        if not phase11["success"]:

            report["stage"] = (
                "phase11_plan"
            )

            report["error"] = (
                phase11.get(
                    "error",
                    "Phase 11 unavailable.",
                )
            )

            self.save_report(report)

            return report

        if not phase11[
            "repair_required"
        ]:

            self.log(
                "Phase 11 reports that no repair is required."
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
                    "Phase 11 did not authorize "
                    "a repair."
                ),
            }

            self.save_report(report)

            self.log("")
            self.log("=" * 60)
            self.log(
                "FINAL PHASE 12 RESULT"
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
        # Inspect project
        # -----------------------------------------------------

        inspection = (
            self.inspect_project()
        )

        report[
            "inspection"
        ] = inspection

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
        # Extract approved files
        # -----------------------------------------------------

        raw_phase11 = phase11[
            "raw_report"
        ]

        files_to_modify = (
            self.extract_files_to_modify(
                raw_phase11
            )
        )

        report[
            "requested_files"
        ] = files_to_modify

        if not files_to_modify:

            report["stage"] = (
                "file_validation"
            )

            report["error"] = (
                "Repair was requested, but "
                "Phase 11 did not provide "
                "any explicit files to modify."
            )

            self.save_report(report)

            return report

        # -----------------------------------------------------
        # Validate paths
        # -----------------------------------------------------

        validated_paths: list[Path] = []
        validation_results: list[
            dict[str, Any]
        ] = []

        for relative_path in files_to_modify:

            valid, reason, resolved = (
                self.validate_relative_path(
                    relative_path
                )
            )

            validation_results.append(
                {
                    "file": relative_path,
                    "valid": valid,
                    "reason": reason,
                }
            )

            if not valid:
                continue

            if resolved is None:
                continue

            validated_paths.append(
                resolved
            )

        report[
            "file_validation"
        ] = validation_results

        if (
            len(validated_paths)
            != len(files_to_modify)
        ):

            report["stage"] = (
                "file_validation"
            )

            report["error"] = (
                "One or more requested files "
                "failed safety validation."
            )

            self.save_report(report)

            return report

        # -----------------------------------------------------
        # Ensure files exist
        # -----------------------------------------------------

        missing_files = [
            str(
                path.relative_to(
                    self.backend_root
                )
            )
            for path in validated_paths
            if not path.exists()
        ]

        report[
            "missing_files"
        ] = missing_files

        if missing_files:

            report["stage"] = (
                "file_validation"
            )

            report["error"] = (
                "Requested repair file does "
                "not exist."
            )

            self.save_report(report)

            return report

        # -----------------------------------------------------
        # Checkpoint
        # -----------------------------------------------------

        self.log(
            "Creating Phase 12 source checkpoint..."
        )

        checkpoint = (
            self.create_checkpoint()
        )

        report[
            "checkpoint"
        ] = checkpoint

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
        # Snapshot
        # -----------------------------------------------------

        before_snapshot = (
            self.snapshot_files(
                validated_paths
            )
        )

        report[
            "before_snapshot_files"
        ] = sorted(
            before_snapshot.keys()
        )

        # -----------------------------------------------------
        # Dry-run safety boundary
        # -----------------------------------------------------

        if self.dry_run:

            self.log(
                "DRY-RUN MODE ENABLED."
            )

            self.log(
                "No source files will be modified."
            )

            report["stage"] = (
                "dry_run"
            )

            report["success"] = True

            report[
                "repair_plan"
            ] = {
                "required": True,
                "executed": False,
                "dry_run": True,
                "authorized_files": (
                    files_to_modify
                ),
                "reason": (
                    "Repair execution was "
                    "intentionally prevented "
                    "because Phase 12 is running "
                    "in dry-run mode."
                ),
            }

            self.save_report(report)

            self.log("")
            self.log("=" * 60)
            self.log(
                "FINAL PHASE 12 RESULT"
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
        # Controlled apply mode
        # -----------------------------------------------------

        #
        # IMPORTANT:
        #
        # This version deliberately refuses to let
        # Ollama directly write source code.
        #
        # A future patch provider can populate
        # "proposed_changes".
        #

        proposed_changes = (
            phase11[
                "raw_report"
            ].get(
                "proposed_changes",
                {},
            )
        )

        if not isinstance(
            proposed_changes,
            dict,
        ):
            proposed_changes = {}

        if not proposed_changes:

            report["stage"] = (
                "patch_required"
            )

            report["error"] = (
                "Controlled apply mode requires "
                "explicit proposed_changes. "
                "No source modification was performed."
            )

            self.save_report(report)

            return report

        # -----------------------------------------------------
        # Apply only approved changes
        # -----------------------------------------------------

        changed_files: list[str] = []
        diffs: dict[str, str] = {}

        try:

            for relative_path in files_to_modify:

                if relative_path not in proposed_changes:

                    raise RuntimeError(
                        "No proposed patch supplied "
                        f"for approved file: "
                        f"{relative_path}"
                    )

                new_content = proposed_changes[
                    relative_path
                ]

                if not isinstance(
                    new_content,
                    str,
                ):
                    raise RuntimeError(
                        "Proposed content must "
                        "be a string."
                    )

                valid, reason, resolved = (
                    self.validate_relative_path(
                        relative_path
                    )
                )

                if not valid or resolved is None:
                    raise RuntimeError(
                        f"Unsafe file path: "
                        f"{relative_path} "
                        f"({reason})"
                    )

                before = before_snapshot.get(
                    relative_path,
                    "",
                )

                diff = self.create_diff(
                    before,
                    new_content,
                    relative_path,
                )

                diffs[
                    relative_path
                ] = diff

                if before != new_content:

                    resolved.write_text(
                        new_content,
                        encoding="utf-8",
                    )

                    changed_files.append(
                        relative_path
                    )

        except Exception as exc:

            self.log(
                "Patch application failed."
            )

            rollback = self.rollback()

            report[
                "rollback"
            ] = rollback

            report[
                "rollback_performed"
            ] = rollback.get(
                "success",
                False,
            )

            report["stage"] = (
                "patch_application"
            )

            report["error"] = str(
                exc
            )

            self.save_report(report)

            return report

        report[
            "changed_files"
        ] = changed_files

        report[
            "diffs"
        ] = diffs

        if not changed_files:

            report["stage"] = (
                "no_changes"
            )

            report["success"] = True

            self.save_report(report)

            return report

        report[
            "source_modified"
        ] = True

        report[
            "repair_executed"
        ] = True

        # -----------------------------------------------------
        # Syntax
        # -----------------------------------------------------

        self.log(
            "Running Python syntax validation..."
        )

        syntax_result = (
            self.run_python_syntax_check()
        )

        report[
            "syntax_validation"
        ] = syntax_result

        if not syntax_result["success"]:

            self.log(
                "Syntax validation FAILED."
            )

            rollback = self.rollback()

            report[
                "rollback"
            ] = rollback

            report[
                "rollback_performed"
            ] = rollback.get(
                "success",
                False,
            )

            report["success"] = False
            report["stage"] = (
                "syntax_validation"
            )

            self.save_report(report)

            return report

        # -----------------------------------------------------
        # Phase 9
        # -----------------------------------------------------

        self.log(
            "Running Phase 9 post-repair QA..."
        )

        qa_result = (
            self.run_phase9()
        )

        report[
            "post_repair_phase9"
        ] = qa_result

        if not qa_result["success"]:

            self.log(
                "Post-repair QA FAILED."
            )

            rollback = self.rollback()

            report[
                "rollback"
            ] = rollback

            report[
                "rollback_performed"
            ] = rollback.get(
                "success",
                False,
            )

            report["success"] = False
            report["stage"] = (
                "post_repair_qa"
            )

            self.save_report(report)

            return report

        # -----------------------------------------------------
        # Final snapshot
        # -----------------------------------------------------

        after_snapshot = (
            self.snapshot_files(
                validated_paths
            )
        )

        report[
            "after_snapshot_files"
        ] = sorted(
            after_snapshot.keys()
        )

        report["success"] = True

        report["stage"] = (
            "repair_completed"
        )

        report[
            "rollback_available"
        ] = self.current_checkpoint.exists()

        self.save_report(report)

        self.log("")
        self.log("=" * 60)
        self.log(
            "PHASE 12 REPAIR COMPLETED SUCCESSFULLY"
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

    # SAFETY DEFAULT:
    #
    # Phase 12 starts in dry-run mode.
    #
    # Set the environment variable:
    #
    # PHASE12_APPLY=1
    #
    # only after you have reviewed the dry-run
    # audit report.
    #
    apply_enabled = (
        os.environ.get(
            "PHASE12_APPLY",
            "0",
        ).strip()
        == "1"
    )

    executor = (
        Phase12ControlledRepairExecutor(
            dry_run=not apply_enabled
        )
    )

    executor.run()


if __name__ == "__main__":
    main()
