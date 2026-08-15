from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class Phase15_1DeploymentAuthorization:
    """
    PHASE 15.1 - DEPLOYMENT AUTHORIZATION GATE

    Final safety boundary between:

        RELEASE_READY
              |
              v
        DEPLOYMENT DRY RUN
              |
              v
        DEPLOYMENT AUTHORIZATION
              |
              v
        ACTUAL DEPLOYMENT

    IMPORTANT:
        This phase does NOT deploy the application.

        Default behavior:
            authorization_mode = "MANUAL"

        The result must be explicitly authorized before a
        future deployment executor is allowed to run.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
        authorization_mode: str = "MANUAL",
    ) -> None:

        self.project_root = Path(
            project_root
        ).resolve()

        self.qa_root = (
            self.project_root.parent
            / "generated"
            / "_code.qa"
        )

        self.phase15_dir = (
            self.qa_root
            / "phase15"
        )

        self.phase15_1_dir = (
            self.qa_root
            / "phase15.1"
        )

        self.phase15_1_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.authorization_mode = (
            authorization_mode
            .strip()
            .upper()
        )

        allowed_modes = {
            "MANUAL",
            "BLOCKED",
        }

        if (
            self.authorization_mode
            not in allowed_modes
        ):
            raise ValueError(
                "Invalid authorization mode. "
                "Allowed modes: MANUAL, BLOCKED"
            )

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(
        self,
        message: str,
    ) -> None:

        print(
            f"[{datetime.now().isoformat()}] "
            f"[PHASE 15.1] {message}"
        )

    # ---------------------------------------------------------
    # JSON helpers
    # ---------------------------------------------------------

    def latest_json(
        self,
        directory: Path,
    ) -> Path | None:

        if not directory.exists():
            return None

        files = list(
            directory.rglob("*.json")
        )

        if not files:
            return None

        return max(
            files,
            key=lambda p: p.stat().st_mtime,
        )

    def load_json(
        self,
        path: Path,
    ) -> dict[str, Any]:

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
                "Expected JSON object."
            )

        return data

    # ---------------------------------------------------------
    # Phase 15 validation
    # ---------------------------------------------------------

    def check_phase15(
        self,
    ) -> tuple[
        bool,
        dict[str, Any],
    ]:

        self.log(
            "Checking Phase 15 deployment gate..."
        )

        report_file = self.latest_json(
            self.phase15_dir
        )

        if report_file is None:

            return False, {
                "success": False,
                "error":
                    "No Phase 15 deployment report found.",
                "searched_path":
                    str(self.phase15_dir),
            }

        try:

            report = self.load_json(
                report_file
            )

        except Exception as exc:

            return False, {
                "success": False,
                "error":
                    f"Invalid Phase 15 JSON: {exc}",
                "source_report":
                    str(report_file),
            }

        phase = str(
            report.get(
                "phase",
                "",
            )
        )

        success = bool(
            report.get(
                "success",
                False,
            )
        )

        gate = str(
            report.get(
                "gate",
                "",
            )
        ).upper()

        deployment_status = str(
            report.get(
                "deployment_status",
                "",
            )
        ).upper()

        deployment_executed = bool(
            report.get(
                "deployment_executed",
                False,
            )
        )

        source_modified = bool(
            report.get(
                "source_modified",
                False,
            )
        )

        checks = {
            "phase15_identity":
                phase == "15",

            "phase15_success":
                success,

            "phase15_gate":
                gate == "PASSED",

            "dry_run_passed":
                deployment_status
                == "DRY_RUN_PASSED",

            "deployment_not_executed":
                deployment_executed is False,

            "source_not_modified":
                source_modified is False,
        }

        passed = all(
            checks.values()
        )

        result = {
            "success": passed,
            "source_report":
                str(report_file),
            "checks": checks,
            "phase15": {
                "phase":
                    phase,
                "success":
                    success,
                "gate":
                    gate,
                "deployment_status":
                    deployment_status,
                "deployment_executed":
                    deployment_executed,
                "source_modified":
                    source_modified,
                },
        }

        if passed:

            self.log(
                "Phase 15 deployment gate PASSED."
            )

        else:

            self.log(
                "Phase 15 deployment gate FAILED."
            )

        return passed, result

    # ---------------------------------------------------------
    # Project validation
    # ---------------------------------------------------------

    def check_project(
        self,
    ) -> dict[str, Any]:

        self.log(
            "Checking deployment source..."
        )

        exists = (
            self.project_root.exists()
        )

        is_directory = (
            self.project_root.is_dir()
            if exists
            else False
        )

        file_count = 0

        if is_directory:

            for path in self.project_root.rglob("*"):

                if not path.is_file():
                    continue

                if any(
                    part in {
                        ".git",
                        ".venv",
                        "__pycache__",
                        "node_modules",
                    }
                    for part in path.parts
                ):
                    continue

                file_count += 1

        return {
            "success":
                exists
                and is_directory
                and file_count > 0,

            "exists":
                exists,

            "is_directory":
                is_directory,

            "file_count":
                file_count,
        }

    # ---------------------------------------------------------
    # Authorization decision
    # ---------------------------------------------------------

    def evaluate_authorization(
        self,
        phase15_valid: bool,
        project_valid: bool,
    ) -> dict[str, Any]:

        self.log(
            "Evaluating deployment authorization..."
        )

        if not phase15_valid:

            return {
                "authorized":
                    False,
                "decision":
                    "BLOCKED",
                "reason":
                    "Phase 15 validation failed.",
            }

        if not project_valid:

            return {
                "authorized":
                    False,
                "decision":
                    "BLOCKED",
                "reason":
                    "Deployment source validation failed.",
            }

        if (
            self.authorization_mode
            == "BLOCKED"
        ):

            return {
                "authorized":
                    False,
                "decision":
                    "BLOCKED",
                "reason":
                    "Authorization mode explicitly blocks deployment.",
            }

        # MANUAL is intentionally not an automatic approval.
        return {
            "authorized":
                False,

            "decision":
                "MANUAL_APPROVAL_REQUIRED",

            "reason":
                (
                    "All automated safety checks passed, "
                    "but explicit human authorization is required."
                ),
        }

    # ---------------------------------------------------------
    # Write audit
    # ---------------------------------------------------------

    def write_report(
        self,
        result: dict[str, Any],
    ) -> Path:

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        report_file = (
            self.phase15_1_dir
            / (
                "authorization_"
                f"{timestamp}.json"
            )
        )

        report_file.write_text(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return report_file

    # ---------------------------------------------------------
    # Main
    # ---------------------------------------------------------

    def run(
        self,
    ) -> dict[str, Any]:

        print("=" * 60)
        print(
            "PHASE 15.1 - DEPLOYMENT AUTHORIZATION GATE"
        )
        print("=" * 60)

        self.log(
            "Starting deployment authorization gate..."
        )

        self.log(
            "Actual deployment is DISABLED."
        )

        # -----------------------------------------------------
        # 1. Validate Phase 15
        # -----------------------------------------------------

        phase15_valid, phase15 = (
            self.check_phase15()
        )

        if not phase15_valid:

            result = {
                "phase":
                    "15.1",

                "success":
                    False,

                "stage":
                    "phase15_validation",

                "gate":
                    "BLOCKED",

                "authorization_status":
                    "BLOCKED",

                "timestamp":
                    datetime.now().isoformat(),

                "authorization_mode":
                    self.authorization_mode,

                "phase15":
                    phase15,

                "deployment_authorized":
                    False,

                "deployment_executed":
                    False,

                "source_modified":
                    False,

                "rollback_performed":
                    False,
            }

            report = self.write_report(
                result
            )

            self.log(
                f"Authorization audit: {report}"
            )

            print("")
            print("=" * 60)
            print(
                "FINAL PHASE 15.1 RESULT"
            )
            print("=" * 60)
            print(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            return result

        # -----------------------------------------------------
        # 2. Validate project
        # -----------------------------------------------------

        project = (
            self.check_project()
        )

        # -----------------------------------------------------
        # 3. Evaluate authorization
        # -----------------------------------------------------

        decision = (
            self.evaluate_authorization(
                phase15_valid,
                project["success"],
            )
        )

        authorized = bool(
            decision["authorized"]
        )

        # -----------------------------------------------------
        # 4. Final status
        # -----------------------------------------------------

        if (
            decision["decision"]
            == "MANUAL_APPROVAL_REQUIRED"
        ):

            gate = "PASSED"

            authorization_status = (
                "MANUAL_APPROVAL_REQUIRED"
            )

            stage = (
                "manual_authorization_pending"
            )

            success = True

        elif (
            decision["decision"]
            == "BLOCKED"
        ):

            gate = "BLOCKED"

            authorization_status = (
                "BLOCKED"
            )

            stage = (
                "authorization_blocked"
            )

            success = False

        else:

            gate = "BLOCKED"

            authorization_status = (
                "BLOCKED"
            )

            stage = (
                "unknown_authorization_state"
            )

            success = False

        # -----------------------------------------------------
        # 5. Safety guarantees
        # -----------------------------------------------------

        result = {
            "phase":
                "15.1",

            "success":
                success,

            "stage":
                stage,

            "gate":
                gate,

            "authorization_status":
                authorization_status,

            "timestamp":
                datetime.now().isoformat(),

            "authorization_mode":
                self.authorization_mode,

            "phase15":
                phase15,

            "project":
                project,

            "decision":
                decision,

            "deployment_authorized":
                authorized,

            "deployment_executed":
                False,

            "source_modified":
                False,

            "rollback_performed":
                False,

            "safety_policy": {
                "actual_deployment":
                    False,

                "source_modification":
                    False,

                "automatic_authorization":
                    False,

                "manual_approval_required":
                    True,

                "rollback":
                    False,

                "default_mode":
                    "MANUAL",
                },

            "conclusion":
                (
                    "Phase 15.1 validated the deployment "
                    "pipeline and requires explicit manual "
                    "authorization before any future deployment."
                    ),
        }

        # -----------------------------------------------------
        # 6. Save audit
        # -----------------------------------------------------

        report = self.write_report(
            result
        )

        self.log(
            f"Authorization audit written to: {report}"
        )

        print("")
        print("=" * 60)
        print(
            "FINAL PHASE 15.1 RESULT"
        )
        print("=" * 60)

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

        return result


def main() -> None:

    gate = (
        Phase15_1DeploymentAuthorization(
            authorization_mode="MANUAL"
        )
    )

    gate.run()


if __name__ == "__main__":
    main()