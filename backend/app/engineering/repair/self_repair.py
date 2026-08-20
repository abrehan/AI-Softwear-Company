from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class SelfRepairEngine:
    """
    PHASE 7 â€” SELF-REPAIR ENGINE

    Workflow:

        QA
         â†“
        Detect failure
         â†“
        Collect diagnostics
         â†“
        Create backup
         â†“
        Generate repair plan
         â†“
        Apply only approved/local repair
         â†“
        Run QA again
         â†“
        Keep fix OR rollback

    The engine is intentionally conservative.
    It never modifies source code unless apply_repair()
    is explicitly called.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
        max_attempts: int = 3,
    ):
        self.project_root = (
            Path(project_root).resolve()
        )

        self.max_attempts = max_attempts

        self.backend_directory = (
            self.project_root / "backend"
        )

        self.app_directory = (
            self.backend_directory / "app"
        )

        self.repair_directory = (
            self.project_root
            / ".qa"
            / "repairs"
        )

        self.repair_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ---------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------

    def timestamp(self) -> str:

        return datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

    # ---------------------------------------------------------
    # Create backup
    # ---------------------------------------------------------

    def create_backup(self) -> dict[str, Any]:

        stamp = self.timestamp()

        backup_directory = (
            self.repair_directory
            / f"backup_{stamp}"
        )

        try:

            shutil.copytree(
                self.backend_directory,
                backup_directory,
                dirs_exist_ok=False,
            )

            return {
                "success": True,
                "path": str(
                    backup_directory
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Restore backup
    # ---------------------------------------------------------

    def restore_backup(
        self,
        backup_path: str,
    ) -> dict[str, Any]:

        source = Path(backup_path)

        if not source.exists():

            return {
                "success": False,
                "error": (
                    "Backup does not exist: "
                    f"{source}"
                ),
            }

        try:

            shutil.rmtree(
                self.backend_directory
            )

            shutil.copytree(
                source,
                self.backend_directory,
            )

            return {
                "success": True,
                "restored_from": str(source),
            }

        except Exception as exc:

            return {
                "success": False,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Python compile check
    # ---------------------------------------------------------

    def compile_check(self) -> dict[str, Any]:

        if not self.app_directory.exists():

            return {
                "success": False,
                "error": (
                    "Application directory not found."
                ),
            }

        errors = []

        for file in self.app_directory.rglob(
            "*.py"
        ):

            try:

                source = file.read_text(
                    encoding="utf-8"
                )

                compile(
                    source,
                    str(file),
                    "exec",
                )

            except Exception as exc:

                errors.append(
                    {
                        "file": str(file),
                        "error": str(exc),
                    }
                )

        return {
            "success": len(errors) == 0,
            "errors": errors,
        }

    # ---------------------------------------------------------
    # Collect Python files
    # ---------------------------------------------------------

    def list_source_files(self) -> list[str]:

        if not self.app_directory.exists():
            return []

        return [
            str(path)
            for path in self.app_directory.rglob(
                "*.py"
            )
        ]

    # ---------------------------------------------------------
    # Analyze QA result
    # ---------------------------------------------------------

    def analyze_failure(
        self,
        qa_result: dict[str, Any],
    ) -> dict[str, Any]:

        failures = []

        endpoint_tests = (
            qa_result.get(
                "endpoint_tests",
                {},
            )
        )

        for result in endpoint_tests.get(
            "results",
            [],
        ):

            if not result.get(
                "passed",
                False,
            ):

                failures.append(
                    {
                        "type": "http_endpoint",
                        "method": result.get(
                            "method"
                        ),
                        "path": result.get(
                            "path"
                        ),
                        "status_code": result.get(
                            "status_code"
                        ),
                        "error": result.get(
                            "error"
                        ),
                        "body": result.get(
                            "body"
                        ),
                        "payload": result.get(
                            "payload"
                        ),
                    }
                )

        if qa_result.get(
            "stage"
        ) == "openapi":

            failures.append(
                {
                    "type": "openapi",
                    "error": str(
                        qa_result.get(
                            "openapi",
                            {}
                        )
                    ),
                }
            )

        return {
            "failure_count": len(
                failures
            ),
            "failures": failures,
        }

    # ---------------------------------------------------------
    # Generate repair plan
    # ---------------------------------------------------------

    def generate_repair_plan(
        self,
        qa_result: dict[str, Any],
    ) -> dict[str, Any]:

        analysis = self.analyze_failure(
            qa_result
        )

        failures = analysis[
            "failures"
        ]

        plan = []

        for failure in failures:

            item = {
                "problem": failure,
                "action": (
                    "Inspect the generated "
                    "FastAPI source and "
                    "associated request model."
                ),
                "automatic_change": False,
            }

            status = failure.get(
                "status_code"
            )

            if status == 500:

                item["action"] = (
                    "Inspect server traceback "
                    "for the failing endpoint."
                )

            elif status == 422:

                item["action"] = (
                    "Inspect request schema and "
                    "test payload compatibility."
                )

            elif status == 404:

                item["action"] = (
                    "Inspect route registration "
                    "and endpoint path."
                )

            plan.append(item)

        return {
            "success": True,
            "failure_count": len(
                failures
            ),
            "plan": plan,
        }

    # ---------------------------------------------------------
    # Save diagnostic report
    # ---------------------------------------------------------

    def save_report(
        self,
        data: dict[str, Any],
        filename: str = "latest_report.json",
    ) -> str:

        report_path = (
            self.repair_directory
            / filename
        )

        report_path.write_text(
            json.dumps(
                data,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return str(report_path)

    # ---------------------------------------------------------
    # Apply repair
    # ---------------------------------------------------------

    def apply_repair(
        self,
        repair_function,
    ) -> dict[str, Any]:

        """
        Apply a caller-supplied repair function.

        The repair function receives the project root.

        This keeps the engine safe: it does not invent
        source-code modifications by itself.
        """

        try:

            result = repair_function(
                self.project_root
            )

            return {
                "success": True,
                "result": result,
            }

        except Exception as exc:

            return {
                "success": False,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Run Phase 6 QA
    # ---------------------------------------------------------

    async def run_qa(
        self,
    ) -> dict[str, Any]:

        try:

            from app.engineering.qa.qa_runner import (
                QARunner
            )

        except Exception as exc:

            return {
                "success": False,
                "stage": "qa_import",
                "error": str(exc),
            }

        runner = QARunner(
            project_root=str(
                self.project_root
            ),
            host="127.0.0.1",
            port=8766,
        )

        return await runner.run()

    # ---------------------------------------------------------
    # Main diagnostic cycle
    # ---------------------------------------------------------

    async def run(
        self,
        apply_repairs: bool = False,
    ) -> dict[str, Any]:

        print()
        print("=" * 60)
        print(
            "ðŸ› ï¸ PHASE 7 â€” SELF-REPAIR ENGINE"
        )
        print("=" * 60)

        history = []

        for attempt in range(
            1,
            self.max_attempts + 1,
        ):

            print()
            print(
                f"ðŸ”„ QA ATTEMPT "
                f"{attempt}/{self.max_attempts}"
            )

            qa_result = (
                await self.run_qa()
            )

            history.append(
                {
                    "attempt": attempt,
                    "qa": qa_result,
                }
            )

            if qa_result.get(
                "success",
                False,
            ):

                print()
                print(
                    "ðŸŽ‰ QA PASSED â€” "
                    "NO REPAIR REQUIRED"
                )

                final = {
                    "success": True,
                    "stage": "self_repair",
                    "attempts": attempt,
                    "message": (
                        "System passed QA."
                    ),
                    "history": history,
                }

                self.save_report(
                    final
                )

                return final

            print()
            print(
                "âŒ QA FAILURE DETECTED"
            )

            analysis = (
                self.analyze_failure(
                    qa_result
                )
            )

            print(
                f"ðŸ”Ž Failures found: "
                f"{analysis['failure_count']}"
            )

            plan = (
                self.generate_repair_plan(
                    qa_result
                )
            )

            self.save_report(
                {
                    "qa": qa_result,
                    "analysis": analysis,
                    "repair_plan": plan,
                },
                filename=(
                    f"attempt_{attempt}.json"
                ),
            )

            print(
                "ðŸ“‹ Repair plan generated."
            )

            if not apply_repairs:

                print(
                    "ðŸ›¡ï¸ Safe mode: "
                    "no source changes applied."
                )

                return {
                    "success": False,
                    "stage": "repair_plan",
                    "attempts": attempt,
                    "analysis": analysis,
                    "repair_plan": plan,
                    "history": history,
                }

            backup = (
                self.create_backup()
            )

            if not backup.get(
                "success",
                False,
            ):

                return {
                    "success": False,
                    "stage": "backup",
                    "error": backup.get(
                        "error"
                    ),
                    "history": history,
                }

            print(
                "ðŸ’¾ Backup created:"
            )

            print(
                f"   {backup['path']}"
            )

            print(
                "âš ï¸ No automatic code mutation "
                "is configured yet."
            )

            print(
                "â„¹ï¸ Add a repair function to "
                "apply_repairs=True mode."
            )

            return {
                "success": False,
                "stage": "repair_not_implemented",
                "attempts": attempt,
                "backup": backup,
                "analysis": analysis,
                "repair_plan": plan,
                "history": history,
            }

        return {
            "success": False,
            "stage": "max_attempts",
            "attempts": self.max_attempts,
            "history": history,
        }


# -------------------------------------------------------------
# Manual execution
# -------------------------------------------------------------

async def main():

    engine = SelfRepairEngine(
        project_root="generated_code",
        max_attempts=3,
    )

    result = await engine.run(
        apply_repairs=False
    )

    print()
    print("=" * 60)
    print(
        "FINAL PHASE 7 RESULT"
    )
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    if not result.get(
        "success",
        False,
    ):

        raise SystemExit(1)


if __name__ == "__main__":

    asyncio.run(main())

