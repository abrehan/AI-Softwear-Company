from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class Phase112ControlledExecutor:
    """
    PHASE 11.2 — CONTROLLED PATCH EXECUTOR

    Responsibilities:

    1. Verify validated repair plan.
    2. Create checkpoint.
    3. Apply exact text replacements.
    4. Run Phase 6 QA.
    5. Run Phase 9 verification.
    6. Keep successful changes.
    7. Roll back failed changes.

    This phase never asks the AI for arbitrary commands.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
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

        self.phase11_root = (
            self.qa_root / "phase11"
        )

        self.executor_root = (
            self.phase11_root
            / "executor"
        )

        self.executor_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        self.timestamp = timestamp

        self.checkpoint_root = (
            self.executor_root
            / f"checkpoint_{timestamp}"
        )

        self.report_file = (
            self.executor_root
            / f"executor_{timestamp}.json"
        )

    def log(self, message: str) -> None:
        try:
            print(message)
        except UnicodeEncodeError:
            print(
                str(message)
                .encode(
                    "ascii",
                    errors="replace",
                )
                .decode("ascii")
            )

    def load_validation(
        self,
        validation_path: str,
    ) -> dict[str, Any]:

        path = Path(
            validation_path
        ).resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"Validation report not found: {path}"
            )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "Validation report must be a JSON object."
            )

        return data

    def create_checkpoint(
        self,
    ) -> dict[str, Any]:

        self.log(
            "Creating Phase 11.2 checkpoint..."
        )

        if not self.backend_root.exists():
            return {
                "success": False,
                "error": (
                    "Backend directory does not exist."
                ),
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
            "path": str(
                self.checkpoint_root
            ),
        }

    def rollback(
        self,
    ) -> dict[str, Any]:

        self.log(
            "ROLLBACK: Restoring checkpoint..."
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

    def apply_patch(
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

        if not all(
            isinstance(value, str)
            for value in (
                file_name,
                search,
                replace,
            )
        ):
            return {
                "success": False,
                "error": (
                    "Invalid patch structure."
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
                    "Patch attempted to "
                    "escape backend."
                ),
            }

        if not target.exists():
            return {
                "success": False,
                "error": (
                    f"Target does not exist: "
                    f"{file_name}"
                ),
            }

        content = target.read_text(
            encoding="utf-8",
            errors="replace",
        )

        count = content.count(
            search
        )

        if count != 1:
            return {
                "success": False,
                "error": (
                    f"Expected exactly one "
                    f"search match in "
                    f"{file_name}; found {count}."
                ),
            }

        new_content = content.replace(
            search,
            replace,
            1,
        )

        target.write_text(
            new_content,
            encoding="utf-8",
        )

        return {
            "success": True,
            "file": file_name,
        }

    def run_phase6(
        self,
    ) -> dict[str, Any]:

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

    def run_phase9(
        self,
    ) -> dict[str, Any]:

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

    def save(
        self,
        report: dict[str, Any],
    ) -> None:

        self.report_file.write_text(
            json.dumps(
                report,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

    def run(
        self,
        validation_path: str,
    ) -> dict[str, Any]:

        self.log("=" * 60)
        self.log(
            "PHASE 11.2 - CONTROLLED PATCH EXECUTOR"
        )
        self.log("=" * 60)

        try:
            validation = (
                self.load_validation(
                    validation_path
                )
            )
        except Exception as exc:

            result = {
                "success": False,
                "stage": "validation_load_failed",
                "error": str(exc),
            }

            self.save(result)
            return result

        if not validation.get(
            "success",
            False,
        ):
            result = {
                "success": False,
                "stage": "validation_rejected",
                "error": (
                    "Phase 11.1 validation did "
                    "not pass."
                ),
                "validation": validation,
            }

            self.save(result)
            return result

        evaluation = validation.get(
            "evaluation",
            {},
        )

        if not evaluation.get(
            "valid",
            False,
        ):
            result = {
                "success": False,
                "stage": "validation_rejected",
                "error": (
                    "Repair plan is not valid."
                ),
                "validation": validation,
            }

            self.save(result)
            return result

        if not evaluation.get(
            "repair_required",
            False,
        ):
            result = {
                "success": True,
                "stage": (
                    "no_repair_required"
                ),
                "auto_modify": False,
                "message": (
                    "Validated plan contains "
                    "no repair request."
                ),
            }

            self.save(result)
            return result

        patches = (
            validation
            .get("plan", {})
            .get("patches", [])
        )

        if not patches:
            result = {
                "success": False,
                "stage": "empty_patch_set",
                "error": (
                    "No patches available "
                    "for execution."
                ),
            }

            self.save(result)
            return result

        checkpoint = (
            self.create_checkpoint()
        )

        if not checkpoint["success"]:
            result = {
                "success": False,
                "stage": "checkpoint_failed",
                "checkpoint": checkpoint,
            }

            self.save(result)
            return result

        applied: list[dict[str, Any]] = []

        for index, patch in enumerate(
            patches,
            start=1,
        ):

            self.log(
                f"Applying patch "
                f"{index}/{len(patches)}..."
            )

            result = self.apply_patch(
                patch
            )

            if not result["success"]:

                rollback = (
                    self.rollback()
                )

                final = {
                    "success": False,
                    "stage": (
                        "patch_failed_rolled_back"
                    ),
                    "applied_patches": applied,
                    "failed_patch": result,
                    "rollback": rollback,
                    "auto_modify": False,
                }

                self.save(final)
                return final

            applied.append(
                result
            )

        phase6 = (
            self.run_phase6()
        )

        if not phase6["success"]:

            rollback = (
                self.rollback()
            )

            final = {
                "success": False,
                "stage": (
                    "phase6_failed_rolled_back"
                ),
                "applied_patches": applied,
                "phase6": phase6,
                "rollback": rollback,
                "auto_modify": False,
            }

            self.save(final)
            return final

        phase9 = (
            self.run_phase9()
        )

        if not phase9["success"]:

            rollback = (
                self.rollback()
            )

            final = {
                "success": False,
                "stage": (
                    "phase9_failed_rolled_back"
                ),
                "applied_patches": applied,
                "phase9": phase9,
                "rollback": rollback,
                "auto_modify": False,
            }

            self.save(final)
            return final

        final = {
            "success": True,
            "stage": (
                "phase11.2_repair_committed"
            ),
            "timestamp": datetime.now().isoformat(),
            "applied_patches": applied,
            "phase6": phase6,
            "phase9": phase9,
            "checkpoint": checkpoint,
            "auto_modify": True,
            "message": (
                "Repair passed Phase 6 and "
                "Phase 9 verification."
            ),
        }

        self.save(final)

        self.log(
            "REPAIR SUCCESSFUL."
        )

        self.log(
            f"Report: {self.report_file}"
        )

        return final


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Phase 11.2 Controlled Executor"
        )
    )

    parser.add_argument(
        "validation",
        help=(
            "Path to Phase 11.1 "
            "validation JSON"
        ),
    )

    args = parser.parse_args()

    result = (
        Phase112ControlledExecutor()
        .run(args.validation)
    )

    print("")
    print("=" * 60)
    print("FINAL PHASE 11.2 RESULT")
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