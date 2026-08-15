from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Phase154DeploymentExecutor:
    """
    PHASE 15.4 - CONTROLLED DEPLOYMENT EXECUTOR

    Deployment target:
        GitHub + Vercel

    Responsibilities:
        1. Validate Phase 15 deployment gate.
        2. Validate Phase 15.1 authorization.
        3. Validate Phase 15.2 approval.
        4. Validate Phase 15.3 authorization.
        5. Validate project integrity.
        6. Detect Git.
        7. Detect Vercel CLI.
        8. Prepare deployment.
        9. Execute deployment only when explicitly enabled.

    SAFETY DEFAULT:
        DEPLOYMENT_EXECUTE=false

    Therefore this phase will NOT accidentally deploy simply because
    Phase 15.3 authorization exists.

    To explicitly enable deployment:

        $env:DEPLOYMENT_EXECUTE="true"

    Then run:

        python -m app.engineering.orchestrator.phase15_4
    """

    PHASE = "15.4"

    def __init__(self) -> None:
        self.backend_dir = Path(__file__).resolve().parents[3]
        self.project_root = self.backend_dir.parent

        self.qa_root = (
            self.backend_dir
            / "generated"
            / "_code.qa"
        )

        self.phase15_dir = self.qa_root / "phase15"
        self.phase151_dir = self.qa_root / "phase15.1"
        self.phase152_dir = self.qa_root / "phase15.2"
        self.phase153_dir = self.qa_root / "phase15.3"
        self.phase154_dir = self.qa_root / "phase15.4"

        self.deployment_dir = self.phase154_dir / "deployment"

        self.deployment_execute = (
            os.getenv("DEPLOYMENT_EXECUTE", "false")
            .strip()
            .lower()
            in {
                "1",
                "true",
                "yes",
                "on",
            }
        )

        self.github_enabled = (
            os.getenv("DEPLOY_GITHUB", "true")
            .strip()
            .lower()
            in {
                "1",
                "true",
                "yes",
                "on",
            }
        )

        self.vercel_enabled = (
            os.getenv("DEPLOY_VERCEL", "true")
            .strip()
            .lower()
            in {
                "1",
                "true",
                "yes",
                "on",
            }
        )

        self.timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d_%H%M%S")

        self.audit_path = (
            self.deployment_dir
            / f"deployment_{self.timestamp}.json"
        )

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message: str) -> None:
        now = datetime.now(
            timezone.utc
        ).isoformat()

        print(
            f"[{now}] [PHASE 15.4] {message}",
            flush=True,
        )

    # ---------------------------------------------------------
    # JSON helpers
    # ---------------------------------------------------------

    def load_json(
        self,
        path: Path,
    ) -> dict[str, Any] | None:
        try:
            if not path.exists():
                return None

            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            if isinstance(data, dict):
                return data

            return None

        except Exception:
            return None

    def find_latest_report(
        self,
        directory: Path,
    ) -> Path | None:
        if not directory.exists():
            return None

        reports = list(
            directory.rglob("*.json")
        )

        if not reports:
            return None

        reports.sort(
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )

        return reports[0]

    # ---------------------------------------------------------
    # Command helpers
    # ---------------------------------------------------------

    def command_exists(
        self,
        command: str,
    ) -> bool:
        return shutil.which(command) is not None

    def run_command(
        self,
        command: list[str],
        cwd: Path,
    ) -> dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout[-10000:],
                "stderr": result.stderr[-10000:],
                "command": command,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": None,
                "stdout": "",
                "stderr": "Command timed out.",
                "command": command,
            }

        except Exception as exc:
            return {
                "success": False,
                "returncode": None,
                "stdout": "",
                "stderr": str(exc),
                "command": command,
            }

    # ---------------------------------------------------------
    # Report validation
    # ---------------------------------------------------------

    def validate_phase15(self) -> dict[str, Any]:
        report = self.find_latest_report(
            self.phase15_dir
        )

        if report is None:
            return {
                "success": False,
                "error": "No Phase 15 deployment gate report found.",
            }

        data = self.load_json(report)

        if data is None:
            return {
                "success": False,
                "error": "Phase 15 report could not be read.",
                "source_report": str(report),
            }

        checks = {
            "phase_identity": data.get("phase") == "15",
            "success": data.get("success") is True,
            "gate": data.get("gate") == "PASSED",
            "dry_run": (
                data.get("deployment_status")
                == "DRY_RUN_PASSED"
            ),
            "deployment_not_executed": (
                data.get("deployment_executed")
                is False
            ),
            "source_not_modified": (
                data.get("source_modified")
                is False
            ),
        }

        valid = all(checks.values())

        return {
            "success": valid,
            "source_report": str(report),
            "checks": checks,
        }

    def validate_phase151(self) -> dict[str, Any]:
        report = self.find_latest_report(
            self.phase151_dir
        )

        if report is None:
            return {
                "success": False,
                "error": (
                    "No Phase 15.1 authorization report found."
                ),
            }

        data = self.load_json(report)

        if data is None:
            return {
                "success": False,
                "error": (
                    "Phase 15.1 report could not be read."
                ),
                "source_report": str(report),
            }

        checks = {
            "phase_identity": data.get("phase") == "15.1",
            "success": data.get("success") is True,
            "gate": data.get("gate") == "PASSED",
            "manual_approval_required": (
                data.get("authorization_status")
                == "MANUAL_APPROVAL_REQUIRED"
            ),
            "deployment_not_executed": (
                data.get("deployment_executed")
                is False
            ),
            "source_not_modified": (
                data.get("source_modified")
                is False
            ),
        }

        valid = all(checks.values())

        return {
            "success": valid,
            "source_report": str(report),
            "checks": checks,
        }

    def validate_phase152(self) -> dict[str, Any]:
        report = self.find_latest_report(
            self.phase152_dir
        )

        if report is None:
            return {
                "success": False,
                "error": (
                    "No Phase 15.2 approval report found."
                ),
            }

        data = self.load_json(report)

        if data is None:
            return {
                "success": False,
                "error": (
                    "Phase 15.2 report could not be read."
                ),
                "source_report": str(report),
            }

        checks = {
            "phase_identity": data.get("phase") == "15.2",
            "success": data.get("success") is True,
            "gate": data.get("gate") == "PASSED",
            "token_issued": (
                data.get("authorization_status")
                == "APPROVAL_TOKEN_ISSUED"
            ),
        }

        approval = data.get(
            "approval",
            {},
        )

        checks["token_hash_exists"] = bool(
            approval.get("token_hash")
        )

        checks["fingerprint_exists"] = bool(
            approval.get("project_fingerprint")
        )

        checks["token_not_consumed"] = (
            approval.get("consumed") is False
        )

        valid = all(checks.values())

        return {
            "success": valid,
            "source_report": str(report),
            "checks": checks,
        }

    def validate_phase153(self) -> dict[str, Any]:
        report = self.find_latest_report(
            self.phase153_dir
        )

        if report is None:
            return {
                "success": False,
                "error": (
                    "No Phase 15.3 authorization "
                    "verification report found."
                ),
            }

        data = self.load_json(report)

        if data is None:
            return {
                "success": False,
                "error": (
                    "Phase 15.3 report could not be read."
                ),
                "source_report": str(report),
            }

        checks = {
            "phase_identity": data.get("phase") == "15.3",
            "success": data.get("success") is True,
            "gate": data.get("gate") == "PASSED",
            "authorized": (
                data.get("authorization_status")
                == "DEPLOYMENT_AUTHORIZED"
            ),
            "deployment_not_executed": (
                data.get("deployment_executed")
                is False
            ),
            "source_not_modified": (
                data.get("source_modified")
                is False
            ),
        }

        token_data = data.get(
            "token",
            {},
        )

        checks["token_verified"] = (
            token_data.get("verified") is True
        )

        checks["token_consumed"] = (
            token_data.get("consumed") is True
        )

        valid = all(checks.values())

        return {
            "success": valid,
            "source_report": str(report),
            "checks": checks,
        }

    # ---------------------------------------------------------
    # Project validation
    # ---------------------------------------------------------

    def validate_project(self) -> dict[str, Any]:
        checks = {
            "project_exists": self.project_root.exists(),
            "project_is_directory": (
                self.project_root.is_dir()
            ),
            "git_directory_exists": (
                (self.project_root / ".git").exists()
            ),
        }

        return {
            "success": all(checks.values()),
            "checks": checks,
        }

    # ---------------------------------------------------------
    # Tool detection
    # ---------------------------------------------------------

    def detect_tools(self) -> dict[str, Any]:
        git_available = self.command_exists("git")
        vercel_available = self.command_exists("vercel")

        return {
            "git": {
                "available": git_available,
            },
            "vercel": {
                "available": vercel_available,
            },
        }

    # ---------------------------------------------------------
    # Git status
    # ---------------------------------------------------------

    def git_status(self) -> dict[str, Any]:
        if not self.command_exists("git"):
            return {
                "success": False,
                "error": "Git executable was not found.",
            }

        result = self.run_command(
            [
                "git",
                "status",
                "--short",
            ],
            self.project_root,
        )

        return {
            "success": result["success"],
            "output": result["stdout"],
            "error": result["stderr"],
        }

    # ---------------------------------------------------------
    # Git branch
    # ---------------------------------------------------------

    def git_branch(self) -> dict[str, Any]:
        if not self.command_exists("git"):
            return {
                "success": False,
                "error": "Git executable was not found.",
            }

        result = self.run_command(
            [
                "git",
                "branch",
                "--show-current",
            ],
            self.project_root,
        )

        return {
            "success": result["success"],
            "branch": result["stdout"].strip(),
            "error": result["stderr"],
        }

    # ---------------------------------------------------------
    # GitHub deployment
    # ---------------------------------------------------------

    def deploy_github(self) -> dict[str, Any]:
        self.log(
            "Preparing GitHub deployment..."
        )

        if not self.github_enabled:
            return {
                "success": True,
                "executed": False,
                "status": "DISABLED",
            }

        if not self.command_exists("git"):
            return {
                "success": False,
                "executed": False,
                "status": "GIT_NOT_FOUND",
            }

        status = self.git_status()

        branch = self.git_branch()

        if not branch.get("success"):
            return {
                "success": False,
                "executed": False,
                "status": "BRANCH_CHECK_FAILED",
                "details": branch,
            }

        current_branch = (
            branch.get("branch")
            or "unknown"
        )

        self.log(
            f"Git branch detected: {current_branch}"
        )

        if not self.deployment_execute:
            return {
                "success": True,
                "executed": False,
                "status": "DRY_RUN",
                "branch": current_branch,
                "working_tree": status,
            }

        self.log(
            "GitHub deployment execution enabled."
        )

        # Only push an existing committed branch.
        # This phase intentionally does not create commits
        # automatically.

        push_result = self.run_command(
            [
                "git",
                "push",
                "origin",
                current_branch,
            ],
            self.project_root,
        )

        return {
            "success": push_result["success"],
            "executed": push_result["success"],
            "status": (
                "DEPLOYED"
                if push_result["success"]
                else "PUSH_FAILED"
            ),
            "branch": current_branch,
            "stdout": push_result["stdout"],
            "stderr": push_result["stderr"],
        }

    # ---------------------------------------------------------
    # Vercel deployment
    # ---------------------------------------------------------

    def deploy_vercel(self) -> dict[str, Any]:
        self.log(
            "Preparing Vercel deployment..."
        )

        if not self.vercel_enabled:
            return {
                "success": True,
                "executed": False,
                "status": "DISABLED",
            }

        if not self.command_exists("vercel"):
            return {
                "success": True,
                "executed": False,
                "status": "VERCEL_CLI_NOT_FOUND",
                "message": (
                    "Vercel CLI is not installed. "
                    "GitHub deployment can still be used."
                ),
            }

        if not self.deployment_execute:
            return {
                "success": True,
                "executed": False,
                "status": "DRY_RUN",
            }

        self.log(
            "Vercel deployment execution enabled."
        )

        result = self.run_command(
            [
                "vercel",
                "--prod",
                "--yes",
            ],
            self.project_root,
        )

        return {
            "success": result["success"],
            "executed": result["success"],
            "status": (
                "DEPLOYED"
                if result["success"]
                else "DEPLOYMENT_FAILED"
            ),
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        }

    # ---------------------------------------------------------
    # Audit
    # ---------------------------------------------------------

    def write_audit(
        self,
        report: dict[str, Any],
    ) -> None:
        self.deployment_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.audit_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report,
                file,
                indent=2,
                ensure_ascii=False,
            )

    # ---------------------------------------------------------
    # Main execution
    # ---------------------------------------------------------

    def execute(self) -> dict[str, Any]:
        print()
        print("=" * 60)
        print(
            "PHASE 15.4 - CONTROLLED DEPLOYMENT EXECUTOR"
        )
        print("=" * 60)

        self.log(
            "Starting Phase 15.4 deployment executor..."
        )

        self.log(
            "Deployment target: GitHub + Vercel."
        )

        self.log(
            "Checking Phase 15 deployment gate..."
        )

        phase15 = self.validate_phase15()

        if not phase15["success"]:
            self.log(
                "Phase 15 deployment gate FAILED."
            )

            report = {
                "phase": self.PHASE,
                "success": False,
                "stage": "phase15_validation",
                "gate": "BLOCKED",
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "phase15": phase15,
            }

            self.write_audit(report)
            return report

        self.log(
            "Phase 15 deployment gate PASSED."
        )

        self.log(
            "Checking Phase 15.1 authorization..."
        )

        phase151 = self.validate_phase151()

        if not phase151["success"]:
            self.log(
                "Phase 15.1 authorization validation FAILED."
            )

            report = {
                "phase": self.PHASE,
                "success": False,
                "stage": "phase15_1_validation",
                "gate": "BLOCKED",
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "phase15": phase15,
                "phase15_1": phase151,
            }

            self.write_audit(report)
            return report

        self.log(
            "Phase 15.1 authorization gate PASSED."
        )

        self.log(
            "Checking Phase 15.2 approval..."
        )

        phase152 = self.validate_phase152()

        if not phase152["success"]:
            self.log(
                "Phase 15.2 approval validation FAILED."
            )

            report = {
                "phase": self.PHASE,
                "success": False,
                "stage": "phase15_2_validation",
                "gate": "BLOCKED",
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "phase15": phase15,
                "phase15_1": phase151,
                "phase15_2": phase152,
            }

            self.write_audit(report)
            return report

        self.log(
            "Phase 15.2 approval validation PASSED."
        )

        self.log(
            "Checking Phase 15.3 authorization..."
        )

        phase153 = self.validate_phase153()

        if not phase153["success"]:
            self.log(
                "Phase 15.3 authorization validation FAILED."
            )

            report = {
                "phase": self.PHASE,
                "success": False,
                "stage": "phase15_3_validation",
                "gate": "BLOCKED",
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "phase15": phase15,
                "phase15_1": phase151,
                "phase15_2": phase152,
                "phase15_3": phase153,
            }

            self.write_audit(report)
            return report

        self.log(
            "Phase 15.3 authorization PASSED."
        )

        self.log(
            "Validating project..."
        )

        project = self.validate_project()

        if not project["success"]:
            self.log(
                "Project validation FAILED."
            )

            report = {
                "phase": self.PHASE,
                "success": False,
                "stage": "project_validation",
                "gate": "BLOCKED",
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "phase15": phase15,
                "phase15_1": phase151,
                "phase15_2": phase152,
                "phase15_3": phase153,
                "project": project,
            }

            self.write_audit(report)
            return report

        tools = self.detect_tools()

        self.log(
            f"Git available: {tools['git']['available']}"
        )

        self.log(
            f"Vercel CLI available: "
            f"{tools['vercel']['available']}"
        )

        if not self.deployment_execute:
            self.log(
                "DEPLOYMENT_EXECUTE is not enabled."
            )

            self.log(
                "Running controlled deployment dry run."
            )

        else:
            self.log(
                "DEPLOYMENT_EXECUTE=true."
            )

            self.log(
                "Actual deployment execution is ENABLED."
            )

        github = self.deploy_github()
        vercel = self.deploy_vercel()

        deployment_executed = (
            github.get("executed") is True
            or vercel.get("executed") is True
        )

        deployment_success = (
            github.get("success") is True
            and vercel.get("success") is True
        )

        if not self.deployment_execute:
            stage = "dry_run"
            deployment_status = "DRY_RUN_PASSED"
        elif deployment_success:
            stage = "deployment_executed"
            deployment_status = "DEPLOYMENT_COMPLETED"
        else:
            stage = "deployment_failed"
            deployment_status = "DEPLOYMENT_FAILED"

        report = {
            "phase": self.PHASE,
            "success": deployment_success,
            "stage": stage,
            "gate": (
                "PASSED"
                if deployment_success
                else "BLOCKED"
            ),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "deployment_status": deployment_status,
            "deployment_mode": (
                "EXECUTE"
                if self.deployment_execute
                else "DRY_RUN"
            ),
            "target": {
                "github": self.github_enabled,
                "vercel": self.vercel_enabled,
            },
            "authorization": {
                "phase15": phase15["success"],
                "phase15_1": phase151["success"],
                "phase15_2": phase152["success"],
                "phase15_3": phase153["success"],
                "deployment_authorized": True,
            },
            "project": project,
            "tools": tools,
            "github": github,
            "vercel": vercel,
            "deployment_authorized": True,
            "deployment_executed": deployment_executed,
            "source_modified": False,
            "rollback_performed": False,
            "safety_policy": {
                "explicit_execution_required": True,
                "automatic_deployment": False,
                "source_modification": False,
                "rollback_performed": False,
                "github_target": True,
                "vercel_target": True,
                "dry_run_default": True,
            },
        }

        self.write_audit(report)

        return report


def main() -> int:
    executor = Phase154DeploymentExecutor()

    result = executor.execute()

    print()
    print("=" * 60)
    print("FINAL PHASE 15.4 RESULT")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print(
        f"Audit: {executor.audit_path}"
    )

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())