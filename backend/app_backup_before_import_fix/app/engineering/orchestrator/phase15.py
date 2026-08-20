from __future__ import annotations
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


class Phase15DeploymentGate:
    """
    PHASE 15 - CONTROLLED DEPLOYMENT GATE

    Safety-first deployment preparation layer.

    Modes:
        DRY_RUN
            Validates deployment readiness without modifying
            or deploying the application.

        MANUAL_APPROVAL
            Performs deployment preparation and requires an
            explicit approval flag before deployment.

        AUTOMATIC
            Allows deployment only when every safety condition
            has passed.

    IMPORTANT:
        This implementation defaults to DRY_RUN.

        It does not automatically deploy anything unless the
        deployment mode is explicitly changed.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
        deployment_mode: str = "DRY_RUN",
    ) -> None:
        self.project_root = Path(project_root).resolve()

        self.qa_root = (
            self.project_root.parent
            / "generated"
            / "_code.qa"
        )

        self.phase14_dir = (
            self.qa_root
            / "phase14"
        )

        self.phase15_dir = (
            self.qa_root
            / "phase15"
        )

        self.snapshot_dir = (
            self.phase15_dir
            / "snapshots"
        )

        self.phase15_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.snapshot_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.deployment_mode = (
            deployment_mode.upper().strip()
        )

        allowed_modes = {
            "DRY_RUN",
            "MANUAL_APPROVAL",
            "AUTOMATIC",
        }

        if self.deployment_mode not in allowed_modes:
            raise ValueError(
                "Invalid deployment mode. "
                f"Allowed: {sorted(allowed_modes)}"
            )

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message: str) -> None:
        print(
            f"[{datetime.now().isoformat()}] "
            f"[PHASE 15] {message}"
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

        if not isinstance(data, dict):
            raise ValueError(
                "Expected JSON object."
            )

        return data

    # ---------------------------------------------------------
    # Phase 14 verification
    # ---------------------------------------------------------

    def check_phase14(
        self,
    ) -> tuple[bool, dict[str, Any]]:
        self.log(
            "Checking Phase 14 release gate..."
        )

        report_file = self.latest_json(
            self.phase14_dir
        )

        if report_file is None:
            return False, {
                "success": False,
                "error":
                    "No Phase 14 release report found.",
                "searched_path":
                    str(self.phase14_dir),
            }

        try:
            report = self.load_json(
                report_file
            )
        except Exception as exc:
            return False, {
                "success": False,
                "error":
                    f"Invalid Phase 14 JSON: {exc}",
                "source_report":
                    str(report_file),
            }

        phase = str(
            report.get("phase", "")
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

        release_status = str(
            report.get(
                "release_status",
                "",
            )
        ).upper()

        deployment_authorized = bool(
            report.get(
                "deployment_authorized",
                False,
            )
        )

        checks = {
            "phase14_identity":
                phase == "14",

            "phase14_success":
                success,

            "phase14_gate":
                gate == "PASSED",

            "release_ready":
                release_status
                == "RELEASE_READY",

            "deployment_not_already_authorized":
                deployment_authorized
                is False,
        }

        passed = all(
            checks.values()
        )

        result = {
            "success": passed,
            "source_report":
                str(report_file),
            "checks": checks,
            "phase14": {
                "phase":
                    phase,
                "success":
                    success,
                "gate":
                    gate,
                "release_status":
                    release_status,
                "deployment_authorized":
                    deployment_authorized,
                },
        }

        if passed:
            self.log(
                "Phase 14 release gate PASSED."
            )
        else:
            self.log(
                "Phase 14 release gate FAILED."
            )

        return passed, result

    # ---------------------------------------------------------
    # Source snapshot
    # ---------------------------------------------------------

    def create_snapshot(
        self,
    ) -> tuple[bool, str | None]:
        """
        Creates a read-only deployment snapshot.

        The snapshot is copied into the Phase 15 audit area.
        The original source is never modified.
        """

        self.log(
            "Creating deployment snapshot..."
        )

        if not self.project_root.exists():
            self.log(
                "Project root does not exist."
            )
            return False, None

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        destination = (
            self.snapshot_dir
            / f"snapshot_{timestamp}"
        )

        try:
            shutil.copytree(
                self.project_root,
                destination,
                ignore=shutil.ignore_patterns(
                    ".git",
                    "__pycache__",
                    ".venv",
                    "node_modules",
                    "*.pyc",
                ),
            )

            self.log(
                f"Snapshot created: {destination}"
            )

            return True, str(
                destination
            )

        except Exception as exc:
            self.log(
                f"Snapshot creation failed: {exc}"
            )
            return False, None

    # ---------------------------------------------------------
    # Deployment preparation
    # ---------------------------------------------------------

    def pre_deployment_checks(
        self,
    ) -> dict[str, Any]:
        self.log(
            "Running pre-deployment checks..."
        )

        checks = {
            "project_exists":
                self.project_root.exists(),

            "phase14_directory_exists":
                self.phase14_dir.exists(),

            "phase15_directory_exists":
                self.phase15_dir.exists(),

            "deployment_mode_valid":
                self.deployment_mode
                in {
                    "DRY_RUN",
                    "MANUAL_APPROVAL",
                    "AUTOMATIC",
                },
        }

        success = all(
            checks.values()
        )

        return {
            "success": success,
            "checks": checks,
        }

    # ---------------------------------------------------------
    # Deployment decision
    # ---------------------------------------------------------

    def determine_deployment_action(
        self,
        phase14_valid: bool,
        preflight_valid: bool,
    ) -> dict[str, Any]:
        """
        Determines whether deployment is permitted.

        This method never performs deployment.
        """

        if not phase14_valid:
            return {
                "allowed": False,
                "action": "BLOCKED",
                "reason":
                    "Phase 14 release gate failed.",
            }

        if not preflight_valid:
            return {
                "allowed": False,
                "action": "BLOCKED",
                "reason":
                    "Pre-deployment checks failed.",
            }

        if self.deployment_mode == "DRY_RUN":
            return {
                "allowed": False,
                "action": "DRY_RUN",
                "reason":
                    (
                        "Dry-run mode is active. "
                        "No deployment will occur."
                    ),
            }

        if self.deployment_mode == "MANUAL_APPROVAL":
            return {
                "allowed": False,
                "action": "WAITING_FOR_APPROVAL",
                "reason":
                    (
                        "Manual approval is required "
                        "before deployment."
                    ),
            }

        if self.deployment_mode == "AUTOMATIC":
            return {
                "allowed": True,
                "action": "DEPLOYMENT_AUTHORIZED",
                "reason":
                    (
                        "All automated deployment "
                        "preconditions passed."
                    ),
            }

        return {
            "allowed": False,
            "action": "BLOCKED",
            "reason":
                "Unknown deployment mode.",
        }

    # ---------------------------------------------------------
    # Audit report
    # ---------------------------------------------------------

    def write_report(
        self,
        result: dict[str, Any],
    ) -> Path:
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        report_file = (
            self.phase15_dir
            / f"deployment_gate_{timestamp}.json"
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
    # Main execution
    # ---------------------------------------------------------

    def run(self) -> dict[str, Any]:
        print("=" * 60)
        print(
            "PHASE 15 - CONTROLLED DEPLOYMENT GATE"
        )
        print("=" * 60)

        self.log(
            "Starting controlled deployment gate..."
        )

        self.log(
            f"Deployment mode: "
            f"{self.deployment_mode}"
        )

        # -----------------------------------------------------
        # 1. Phase 14
        # -----------------------------------------------------

        phase14_valid, phase14 = (
            self.check_phase14()
        )

        if not phase14_valid:
            result = {
                "phase": "15",
                "success": False,
                "stage":
                    "phase14_validation",
                "gate": "BLOCKED",
                "deployment_status":
                    "BLOCKED",
                "timestamp":
                    datetime.now().isoformat(),
                "deployment_mode":
                    self.deployment_mode,
                "phase14":
                    phase14,
                "source_modified":
                    False,
                "deployment_executed":
                    False,
                "rollback_performed":
                    False,
            }

            report = self.write_report(
                result
            )

            self.log(
                f"Deployment audit: {report}"
            )

            print("")
            print("=" * 60)
            print(
                "FINAL PHASE 15 RESULT"
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

        self.log(
            "Phase 14 release gate PASSED."
        )

        # -----------------------------------------------------
        # 2. Snapshot
        # -----------------------------------------------------

        snapshot_success, snapshot = (
            self.create_snapshot()
        )

        if not snapshot_success:
            result = {
                "phase": "15",
                "success": False,
                "stage":
                    "snapshot_creation",
                "gate": "BLOCKED",
                "deployment_status":
                    "BLOCKED",
                "timestamp":
                    datetime.now().isoformat(),
                "deployment_mode":
                    self.deployment_mode,
                "phase14":
                    phase14,
                "snapshot":
                    None,
                "source_modified":
                    False,
                "deployment_executed":
                    False,
                "rollback_performed":
                    False,
            }

            report = self.write_report(
                result
            )

            self.log(
                f"Deployment audit: {report}"
            )

            print(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            return result

        # -----------------------------------------------------
        # 3. Preflight
        # -----------------------------------------------------

        self.log(
            "Running deployment preflight..."
        )

        preflight = (
            self.pre_deployment_checks()
        )

        # -----------------------------------------------------
        # 4. Determine action
        # -----------------------------------------------------

        decision = (
            self.determine_deployment_action(
                phase14_valid,
                preflight["success"],
            )
        )

        deployment_executed = False
        deployment_authorized = bool(
            decision["allowed"]
        )

        if decision["action"] == "DRY_RUN":
            self.log(
                "DRY_RUN active."
            )
            self.log(
                "No deployment will be executed."
            )

        elif decision["action"] == "WAITING_FOR_APPROVAL":
            self.log(
                "Deployment requires manual approval."
            )

        elif decision["action"] == "DEPLOYMENT_AUTHORIZED":
            self.log(
                "Deployment authorization granted."
            )

            # IMPORTANT:
            # No real deployment is performed here yet.
            #
            # This is intentionally left as a safety
            # boundary until a real deployment provider
            # is explicitly configured.
            self.log(
                "No deployment provider configured."
            )
            self.log(
                "Deployment remains unexecuted."
            )

            deployment_authorized = False

        # -----------------------------------------------------
        # 5. Final result
        # -----------------------------------------------------

        if decision["action"] == "DRY_RUN":
            deployment_status = (
                "DRY_RUN_PASSED"
            )
            success = True
            stage = "dry_run"
            gate = "PASSED"

        elif decision["action"] == "WAITING_FOR_APPROVAL":
            deployment_status = (
                "WAITING_FOR_APPROVAL"
            )
            success = True
            stage = "manual_approval_required"
            gate = "PASSED"

        elif decision["action"] == "DEPLOYMENT_AUTHORIZED":
            deployment_status = (
                "DEPLOYMENT_NOT_EXECUTED"
            )
            success = False
            stage = "deployment_provider_missing"
            gate = "BLOCKED"

        else:
            deployment_status = "BLOCKED"
            success = False
            stage = "pre_deployment_validation"
            gate = "BLOCKED"

        result = {
            "phase": "15",
            "success": success,
            "stage": stage,
            "gate": gate,
            "deployment_status":
                deployment_status,
            "timestamp":
                datetime.now().isoformat(),

            "deployment_mode":
                self.deployment_mode,

            "phase14":
                phase14,

            "snapshot": {
                "success":
                    snapshot_success,
                "path":
                    snapshot,
                },

            "preflight":
                preflight,

            "decision":
                decision,

            "source_modified":
                False,

            "deployment_authorized":
                deployment_authorized,

            "deployment_executed":
                deployment_executed,

            "rollback_performed":
                False,

            "safety_policy": {
                "source_modification":
                    False,

                "automatic_deployment":
                    False,

                "rollback_enabled":
                    False,

                "dry_run_default":
                    True,
                },

            "conclusion": (
                "Phase 15 deployment gate completed "
                "without modifying source code."
                ),
        }

        report = self.write_report(
            result
        )

        self.log(
            f"Deployment audit written to: {report}"
        )

        print("")
        print("=" * 60)
        print(
            "FINAL PHASE 15 RESULT"
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
    gate = Phase15DeploymentGate(
        deployment_mode="DRY_RUN"
    )
    gate.run()


if __name__ == "__main__":
    main()
