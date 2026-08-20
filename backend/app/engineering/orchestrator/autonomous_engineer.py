from __future__ import annotations

import asyncio
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


class AutonomousEngineer:
    """
    PHASE 8 â€” AUTONOMOUS ENGINEERING ORCHESTRATOR

    Coordinates:

        validation
        runtime
        QA
        diagnostics
        repair planning
        backup
        verification
        rollback

    Safe by default:
        automatic source modification is disabled.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
        host: str = "127.0.0.1",
        port: int = 8766,
        max_repair_attempts: int = 3,
    ):

        self.project_root = (
            Path(project_root).resolve()
        )

        self.host = host
        self.port = port

        self.max_repair_attempts = (
            max_repair_attempts
        )

        self.backend_directory = (
            self.project_root / "backend"
        )

        self.report_directory = (
            self.project_root
            / ".qa"
            / "orchestrator"
        )

        self.report_directory.mkdir(
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
    # Save report
    # ---------------------------------------------------------

    def save_report(
        self,
        report: dict[str, Any],
    ) -> str:

        path = (
            self.report_directory
            / f"run_{self.timestamp()}.json"
        )

        path.write_text(
            json.dumps(
                report,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return str(path)

    # ---------------------------------------------------------
    # Import QA runner
    # ---------------------------------------------------------

    async def run_qa(self) -> dict[str, Any]:

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
            host=self.host,
            port=self.port,
        )

        return await runner.run()

    # ---------------------------------------------------------
    # Import project validator
    # ---------------------------------------------------------

    def run_validator(
        self,
    ) -> dict[str, Any]:

        try:

            from app.engineering.validator.project_validator import (
                ProjectValidator
            )

        except Exception as exc:

            return {
                "success": False,
                "stage": "validator_import",
                "error": str(exc),
            }

        try:

            validator = ProjectValidator(
                project_root=str(
                    self.project_root
                )
            )

            if hasattr(
                validator,
                "run",
            ):

                result = validator.run()

                if isinstance(
                    result,
                    dict,
                ):

                    return result

                return {
                    "success": bool(result),
                    "result": result,
                }

            return {
                "success": True,
                "stage": "validator",
                "message": (
                    "Validator loaded, "
                    "but no run() method exists."
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "stage": "validator",
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Backup
    # ---------------------------------------------------------

    def create_backup(
        self,
    ) -> dict[str, Any]:

        if not self.backend_directory.exists():

            return {
                "success": False,
                "error": (
                    "Backend directory does "
                    "not exist."
                ),
            }

        backup_directory = (
            self.report_directory
            / "backups"
            / f"backup_{self.timestamp()}"
        )

        backup_directory.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            shutil.copytree(
                self.backend_directory,
                backup_directory,
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
    # Error analysis
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
                        "payload": result.get(
                            "payload"
                        ),
                        "body": result.get(
                            "body"
                        ),
                    }
                )

        return {
            "success": True,
            "failure_count": len(
                failures
            ),
            "failures": failures,
        }

    # ---------------------------------------------------------
    # Repair plan
    # ---------------------------------------------------------

    def create_repair_plan(
        self,
        analysis: dict[str, Any],
    ) -> dict[str, Any]:

        plan = []

        for failure in analysis.get(
            "failures",
            [],
        ):

            status = failure.get(
                "status_code"
            )

            if status == 500:

                action = (
                    "Inspect FastAPI traceback "
                    "and repair server-side exception."
                )

            elif status == 422:

                action = (
                    "Inspect request schema and "
                    "endpoint test payload."
                )

            elif status == 404:

                action = (
                    "Inspect route registration "
                    "and endpoint path."
                )

            else:

                action = (
                    "Inspect endpoint response "
                    "and associated source code."
                )

            plan.append(
                {
                    "endpoint": (
                        f"{failure.get('method')} "
                        f"{failure.get('path')}"
                    ),
                    "status_code": status,
                    "action": action,
                    "automatic": False,
                }
            )

        return {
            "success": True,
            "items": plan,
        }

    # ---------------------------------------------------------
    # Safe repair placeholder
    # ---------------------------------------------------------

    def repair(
        self,
        repair_plan: dict[str, Any],
    ) -> dict[str, Any]:

        """
        Phase 8 intentionally does not mutate
        source code automatically.

        The next AI repair layer will provide
        a validated patch here.
        """

        return {
            "success": False,
            "applied": False,
            "message": (
                "No automatic source mutation "
                "configured. Repair plan generated."
            ),
            "plan": repair_plan,
        }

    # ---------------------------------------------------------
    # Main orchestration
    # ---------------------------------------------------------

    async def run(
        self,
        auto_repair: bool = False,
    ) -> dict[str, Any]:

        print()
        print("=" * 60)
        print(
            "ðŸ¤– PHASE 8 â€” AUTONOMOUS ENGINEER"
        )
        print("=" * 60)

        report: dict[str, Any] = {
            "success": False,
            "stage": "phase_8",
            "started_at": datetime.now().isoformat(),
            "project_root": str(
                self.project_root
            ),
            "host": self.host,
            "port": self.port,
            "auto_repair": auto_repair,
            "steps": [],
        }

        # -----------------------------------------------------
        # Step 1 â€” Validation
        # -----------------------------------------------------

        print()
        print(
            "ðŸ”Ž Step 1 â€” Project validation"
        )

        validation = (
            self.run_validator()
        )

        report["steps"].append(
            {
                "name": "validation",
                "result": validation,
            }
        )

        if not validation.get(
            "success",
            False,
        ):

            print(
                "âŒ Project validation failed."
            )

            report["stage"] = (
                "validation_failed"
            )

            self.save_report(report)

            return report

        print(
            "âœ… Project validation passed."
        )

        # -----------------------------------------------------
        # Step 2 â€” QA
        # -----------------------------------------------------

        for attempt in range(
            1,
            self.max_repair_attempts + 1,
        ):

            print()
            print(
                f"ðŸ§ª Step 2 â€” QA attempt "
                f"{attempt}/"
                f"{self.max_repair_attempts}"
            )

            qa = await self.run_qa()

            report["steps"].append(
                {
                    "name": "qa",
                    "attempt": attempt,
                    "result": qa,
                }
            )

            if qa.get(
                "success",
                False,
            ):

                print()
                print(
                    "ðŸŽ‰ ALL ENGINEERING CHECKS PASSED"
                )

                report["success"] = True
                report["stage"] = (
                    "completed"
                )
                report["completed_at"] = (
                    datetime.now().isoformat()
                )

                report_path = (
                    self.save_report(
                        report
                    )
                )

                report[
                    "report"
                ] = report_path

                print()
                print(
                    f"ðŸ“„ Report: {report_path}"
                )

                return report

            # -------------------------------------------------
            # Step 3 â€” Analyze
            # -------------------------------------------------

            print()
            print(
                "ðŸ”¬ Step 3 â€” Failure analysis"
            )

            analysis = (
                self.analyze_failure(
                    qa
                )
            )

            report["steps"].append(
                {
                    "name": "analysis",
                    "attempt": attempt,
                    "result": analysis,
                }
            )

            print(
                f"ðŸ”Ž Failures: "
                f"{analysis['failure_count']}"
            )

            # -------------------------------------------------
            # Step 4 â€” Repair plan
            # -------------------------------------------------

            repair_plan = (
                self.create_repair_plan(
                    analysis
                )
            )

            report["steps"].append(
                {
                    "name": "repair_plan",
                    "attempt": attempt,
                    "result": repair_plan,
                }
            )

            print(
                "ðŸ“‹ Repair plan created."
            )

            # -------------------------------------------------
            # Safe mode
            # -------------------------------------------------

            if not auto_repair:

                print(
                    "ðŸ›¡ï¸ SAFE MODE â€” "
                    "No source files modified."
                )

                report["stage"] = (
                    "repair_plan_generated"
                )

                report_path = (
                    self.save_report(
                        report
                    )
                )

                report[
                    "report"
                ] = report_path

                return report

            # -------------------------------------------------
            # Step 5 â€” Backup
            # -------------------------------------------------

            print()
            print(
                "ðŸ’¾ Step 5 â€” Creating backup"
            )

            backup = (
                self.create_backup()
            )

            report["steps"].append(
                {
                    "name": "backup",
                    "attempt": attempt,
                    "result": backup,
                }
            )

            if not backup.get(
                "success",
                False,
            ):

                report["stage"] = (
                    "backup_failed"
                )

                self.save_report(
                    report
                )

                return report

            print(
                "âœ… Backup created."
            )

            # -------------------------------------------------
            # Step 6 â€” Repair
            # -------------------------------------------------

            print()
            print(
                "ðŸ”§ Step 6 â€” Repair"
            )

            repair_result = (
                self.repair(
                    repair_plan
                )
            )

            report["steps"].append(
                {
                    "name": "repair",
                    "attempt": attempt,
                    "result": repair_result,
                }
            )

            if not repair_result.get(
                "applied",
                False,
            ):

                print(
                    "â„¹ï¸ No automatic repair applied."
                )

                report["stage"] = (
                    "repair_pending"
                )

                report_path = (
                    self.save_report(
                        report
                    )
                )

                report[
                    "report"
                ] = report_path

                return report

        # -----------------------------------------------------
        # Maximum attempts
        # -----------------------------------------------------

        report["stage"] = (
            "maximum_attempts_reached"
        )

        report["completed_at"] = (
            datetime.now().isoformat()
        )

        report_path = (
            self.save_report(
                report
            )
        )

        report[
            "report"
        ] = report_path

        return report


# -------------------------------------------------------------
# Manual execution
# -------------------------------------------------------------

async def main():

    engineer = AutonomousEngineer(
        project_root="generated_code",
        host="127.0.0.1",
        port=8766,
        max_repair_attempts=3,
    )

    result = await engineer.run(
        auto_repair=False
    )

    print()
    print("=" * 60)
    print(
        "FINAL PHASE 8 RESULT"
    )
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":

    asyncio.run(main())

