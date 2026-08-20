from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Phase15_5EnvironmentVerification:
    """
    PHASE 15.5 - DEPLOYMENT ENVIRONMENT & CREDENTIAL VERIFICATION

    Purpose:
        Verify that the project is ready for a future deployment.

    IMPORTANT SAFETY RULES:
        - This phase NEVER deploys.
        - This phase NEVER pushes to GitHub.
        - This phase NEVER modifies source files.
        - This phase NEVER prints secret values.
        - This phase NEVER consumes approval tokens.
        - This phase only validates deployment readiness.

    Pipeline:

        Phase 15
            |
            v
        Phase 15.1
            |
            v
        Phase 15.2
            |
            v
        Phase 15.3
            |
            v
        Phase 15.4
            |
            v
        Phase 15.5
            |
            v
        DEPLOYMENT_ENVIRONMENT_READY

    Actual deployment remains disabled.
    """

    PHASE = "15.5"

    def __init__(self) -> None:
        self.backend_root = Path(__file__).resolve().parents[3]
        self.project_root = self.backend_root.parent

        self.qa_root = self.backend_root / "generated" / "_code.qa"

        self.phase15_root = self.qa_root / "phase15"
        self.phase151_root = self.qa_root / "phase15.1"
        self.phase152_root = self.qa_root / "phase15.2"
        self.phase153_root = self.qa_root / "phase15.3"
        self.phase154_root = self.qa_root / "phase15.4"
        self.phase155_root = self.qa_root / "phase15.5"

        self.report_dir = self.phase155_root / "environment_verification"

        self.timestamp = datetime.now(timezone.utc).isoformat()

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        print(f"[{now}] [PHASE 15.5] {message}")

    # ---------------------------------------------------------
    # JSON helpers
    # ---------------------------------------------------------

    def load_json(self, path: Path) -> dict[str, Any] | None:
        try:
            if not path.exists() or not path.is_file():
                return None

            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)

            if isinstance(data, dict):
                return data

        except (OSError, json.JSONDecodeError):
            return None

        return None

    def newest_json(self, root: Path) -> Path | None:
        if not root.exists():
            return None

        files = list(root.rglob("*.json"))

        if not files:
            return None

        files.sort(
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )

        return files[0]

    def newest_json_matching(
        self,
        root: Path,
        keywords: list[str],
    ) -> Path | None:
        if not root.exists():
            return None

        files = list(root.rglob("*.json"))

        matching: list[Path] = []

        for path in files:
            name = path.name.lower()

            if all(keyword.lower() in name for keyword in keywords):
                matching.append(path)

        if not matching:
            return None

        matching.sort(
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )

        return matching[0]

    # ---------------------------------------------------------
    # Report discovery
    # ---------------------------------------------------------

    def find_phase_report(
        self,
        phase_root: Path,
        preferred_keywords: list[str] | None = None,
    ) -> Path | None:
        if preferred_keywords:
            result = self.newest_json_matching(
                phase_root,
                preferred_keywords,
            )

            if result:
                return result

        return self.newest_json(phase_root)

    # ---------------------------------------------------------
    # Command execution
    # ---------------------------------------------------------

    def command_exists(self, command: str) -> bool:
        return shutil.which(command) is not None

    def run_command(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout: int = 30,
    ) -> tuple[bool, str]:
        try:
            result = subprocess.run(
                command,
                cwd=str(cwd) if cwd else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
                shell=False,
            )

            output = result.stdout.strip()

            return result.returncode == 0, output

        except (
            subprocess.SubprocessError,
            OSError,
        ) as exc:
            return False, str(exc)

    # ---------------------------------------------------------
    # Phase 15 verification
    # ---------------------------------------------------------

    def verify_phase15(self) -> dict[str, Any]:
        self.log("Checking Phase 15 deployment gate...")

        report_path = self.find_phase_report(
            self.phase15_root,
            ["deployment_gate"],
        )

        if not report_path:
            return {
                "success": False,
                "error": "Phase 15 deployment gate report not found.",
            }

        report = self.load_json(report_path)

        if not report:
            return {
                "success": False,
                "error": "Phase 15 deployment gate report is invalid.",
                "source_report": str(report_path),
            }

        success = (
            report.get("phase") == "15"
            and report.get("success") is True
            and report.get("gate") == "PASSED"
            and report.get("deployment_status") == "DRY_RUN_PASSED"
            and report.get("deployment_executed") is False
            and report.get("source_modified") is False
        )

        return {
            "success": success,
            "source_report": str(report_path),
            "checks": {
                "phase15_identity": report.get("phase") == "15",
                "success": report.get("success") is True,
                "gate": report.get("gate") == "PASSED",
                "dry_run_passed": (
                    report.get("deployment_status")
                    == "DRY_RUN_PASSED"
                ),
                "deployment_not_executed": (
                    report.get("deployment_executed") is False
                ),
                "source_not_modified": (
                    report.get("source_modified") is False
                ),
            },
        }

    # ---------------------------------------------------------
    # Phase 15.1 verification
    # ---------------------------------------------------------

    def verify_phase151(self) -> dict[str, Any]:
        self.log("Checking Phase 15.1 authorization gate...")

        report_path = self.find_phase_report(
            self.phase151_root,
            ["authorization"],
        )

        if not report_path:
            return {
                "success": False,
                "error": "Phase 15.1 authorization report not found.",
            }

        report = self.load_json(report_path)

        if not report:
            return {
                "success": False,
                "error": "Phase 15.1 report is invalid.",
                "source_report": str(report_path),
            }

        success = (
            report.get("phase") == "15.1"
            and report.get("success") is True
            and report.get("gate") == "PASSED"
            and report.get("authorization_mode") == "MANUAL"
            and report.get("deployment_executed") is False
            and report.get("source_modified") is False
        )

        return {
            "success": success,
            "source_report": str(report_path),
            "checks": {
                "phase15_1_identity": (
                    report.get("phase") == "15.1"
                ),
                "success": report.get("success") is True,
                "gate": report.get("gate") == "PASSED",
                "manual_authorization": (
                    report.get("authorization_mode") == "MANUAL"
                ),
                "deployment_not_executed": (
                    report.get("deployment_executed") is False
                ),
                "source_not_modified": (
                    report.get("source_modified") is False
                ),
            },
        }

    # ---------------------------------------------------------
    # Phase 15.2 verification
    # ---------------------------------------------------------

    def verify_phase152(self) -> dict[str, Any]:
        self.log("Checking Phase 15.2 human approval...")

        report_path = self.find_phase_report(
            self.phase152_root,
            ["human_approval"],
        )

        if not report_path:
            return {
                "success": False,
                "error": "Phase 15.2 human approval report not found.",
            }

        report = self.load_json(report_path)

        if not report:
            return {
                "success": False,
                "error": "Phase 15.2 report is invalid.",
                "source_report": str(report_path),
            }

        approval = report.get("approval", {})

        success = (
            report.get("phase") == "15.2"
            and report.get("success") is True
            and report.get("gate") == "PASSED"
            and approval.get("token_hash")
            and approval.get("project_fingerprint")
        )

        return {
            "success": bool(success),
            "source_report": str(report_path),
            "checks": {
                "phase15_2_identity": (
                    report.get("phase") == "15.2"
                ),
                "success": report.get("success") is True,
                "gate": report.get("gate") == "PASSED",
                "token_hash_exists": bool(
                    approval.get("token_hash")
                ),
                "fingerprint_exists": bool(
                    approval.get("project_fingerprint")
                ),
            },
        }

    # ---------------------------------------------------------
    # Phase 15.3 verification
    # ---------------------------------------------------------

    def verify_phase153(self) -> dict[str, Any]:
        self.log("Checking Phase 15.3 authorization...")

        report_path = self.find_phase_report(
            self.phase153_root,
            ["authorization_verification"],
        )

        if not report_path:
            return {
                "success": False,
                "error": "Phase 15.3 authorization report not found.",
            }

        report = self.load_json(report_path)

        if not report:
            return {
                "success": False,
                "error": "Phase 15.3 report is invalid.",
                "source_report": str(report_path),
            }

        success = (
            report.get("phase") == "15.3"
            and report.get("success") is True
            and report.get("gate") == "PASSED"
            and report.get("authorization_status")
            == "DEPLOYMENT_AUTHORIZED"
            and report.get("deployment_executed") is False
            and report.get("source_modified") is False
        )

        return {
            "success": success,
            "source_report": str(report_path),
            "checks": {
                "phase15_3_identity": (
                    report.get("phase") == "15.3"
                ),
                "success": report.get("success") is True,
                "gate": report.get("gate") == "PASSED",
                "deployment_authorized": (
                    report.get("deployment_authorized") is True
                ),
                "deployment_not_executed": (
                    report.get("deployment_executed") is False
                ),
                "source_not_modified": (
                    report.get("source_modified") is False
                ),
            },
        }

    # ---------------------------------------------------------
    # Phase 15.4 verification
    # ---------------------------------------------------------

    def verify_phase154(self) -> dict[str, Any]:
        self.log("Checking Phase 15.4 controlled deployment dry run...")

        report_path = self.find_phase_report(
            self.phase154_root,
            ["deployment"],
        )

        if not report_path:
            report_path = self.newest_json(
                self.phase154_root
            )

        if not report_path:
            return {
                "success": False,
                "error": "Phase 15.4 report not found.",
            }

        report = self.load_json(report_path)

        if not report:
            return {
                "success": False,
                "error": "Phase 15.4 report is invalid.",
                "source_report": str(report_path),
            }

        success = (
            report.get("phase") == "15.4"
            and report.get("success") is True
            and report.get("gate") == "PASSED"
            and report.get("deployment_status")
            == "DRY_RUN_PASSED"
            and report.get("deployment_mode")
            == "DRY_RUN"
        )

        return {
            "success": success,
            "source_report": str(report_path),
            "checks": {
                "phase15_4_identity": (
                    report.get("phase") == "15.4"
                ),
                "success": report.get("success") is True,
                "gate": report.get("gate") == "PASSED",
                "dry_run_passed": (
                    report.get("deployment_status")
                    == "DRY_RUN_PASSED"
                ),
                "dry_run_mode": (
                    report.get("deployment_mode")
                    == "DRY_RUN"
                ),
            },
        }

    # ---------------------------------------------------------
    # Git verification
    # ---------------------------------------------------------

    def verify_git(self) -> dict[str, Any]:
        self.log("Checking Git environment...")

        git_available = self.command_exists("git")

        result: dict[str, Any] = {
            "available": git_available,
            "repository": False,
            "branch": None,
            "remote_configured": False,
            "working_tree_clean": False,
        }

        if not git_available:
            return result

        git_dir = self.project_root / ".git"

        result["repository"] = git_dir.exists()

        if not result["repository"]:
            return result

        branch_ok, branch_output = self.run_command(
            [
                "git",
                "branch",
                "--show-current",
            ],
            cwd=self.project_root,
        )

        if branch_ok:
            result["branch"] = branch_output.strip() or None

        remote_ok, remote_output = self.run_command(
            [
                "git",
                "remote",
                "get-url",
                "origin",
            ],
            cwd=self.project_root,
        )

        result["remote_configured"] = remote_ok

        if remote_ok:
            remote_lower = remote_output.lower()

            if "github.com" in remote_lower:
                result["github_remote"] = True
            else:
                result["github_remote"] = False
        else:
            result["github_remote"] = False

        status_ok, status_output = self.run_command(
            [
                "git",
                "status",
                "--porcelain",
            ],
            cwd=self.project_root,
        )

        result["working_tree_clean"] = (
            status_ok and not status_output.strip()
        )

        return result

    # ---------------------------------------------------------
    # Vercel verification
    # ---------------------------------------------------------

    def verify_vercel(self) -> dict[str, Any]:
        self.log("Checking Vercel environment...")

        available = self.command_exists("vercel")

        result: dict[str, Any] = {
            "cli_available": available,
            "authenticated": False,
            "project_linked": False,
        }

        if not available:
            return result

        auth_ok, auth_output = self.run_command(
            [
                "vercel",
                "whoami",
            ],
            cwd=self.project_root,
            timeout=30,
        )

        result["authenticated"] = auth_ok

        result["authentication_checked"] = True

        link_file = (
            self.project_root
            / ".vercel"
            / "project.json"
        )

        result["project_linked"] = link_file.exists()

        if link_file.exists():
            try:
                data = json.loads(
                    link_file.read_text(
                        encoding="utf-8"
                    )
                )

                result["project_id_present"] = bool(
                    data.get("projectId")
                )

                result["org_id_present"] = bool(
                    data.get("orgId")
                )

            except (
                OSError,
                json.JSONDecodeError,
            ):
                result["project_linked"] = False

        return result

    # ---------------------------------------------------------
    # Environment verification
    # ---------------------------------------------------------

    def verify_environment_files(self) -> dict[str, Any]:
        self.log("Checking deployment configuration files...")

        candidates = [
            ".env",
            ".env.example",
            ".env.production",
            ".env.production.example",
            "vercel.json",
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "docker-compose.yml",
            "docker-compose.yaml",
        ]

        found: list[str] = []

        for name in candidates:
            path = self.project_root / name

            if path.exists():
                found.append(name)

        return {
            "success": True,
            "files_checked": candidates,
            "files_found": found,
        }

    # ---------------------------------------------------------
    # Secret safety verification
    # ---------------------------------------------------------

    def verify_secret_safety(self) -> dict[str, Any]:
        self.log("Checking secret-handling safety...")

        sensitive_names = {
            "GITHUB_TOKEN",
            "GH_TOKEN",
            "VERCEL_TOKEN",
            "VERCEL_ORG_ID",
            "VERCEL_PROJECT_ID",
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "ANTHROPIC_API_KEY",
            "DATABASE_URL",
            "SECRET_KEY",
        }

        present_names: list[str] = []

        for name in sensitive_names:
            if os.environ.get(name):
                present_names.append(name)

        return {
            "success": True,
            "secret_values_printed": False,
            "secret_values_stored": False,
            "environment_secret_names_detected": sorted(
                present_names
            ),
        }

    # ---------------------------------------------------------
    # Build detection
    # ---------------------------------------------------------

    def detect_build_system(self) -> dict[str, Any]:
        self.log("Detecting project build system...")

        package_json = self.project_root / "package.json"
        requirements = self.project_root / "requirements.txt"
        pyproject = self.project_root / "pyproject.toml"

        result: dict[str, Any] = {
            "node_project": package_json.exists(),
            "python_requirements": requirements.exists(),
            "python_project": pyproject.exists(),
            "build_script_detected": False,
        }

        if package_json.exists():
            try:
                data = json.loads(
                    package_json.read_text(
                        encoding="utf-8"
                    )
                )

                scripts = data.get("scripts", {})

                if isinstance(scripts, dict):
                    result["build_script_detected"] = (
                        "build" in scripts
                    )

                    result["npm_build_command"] = (
                        "npm run build"
                        if "build" in scripts
                        else None
                    )

            except (
                OSError,
                json.JSONDecodeError,
            ):
                result["package_json_valid"] = False
            else:
                result["package_json_valid"] = True

        return result

    # ---------------------------------------------------------
    # Project fingerprint
    # ---------------------------------------------------------

    def calculate_fingerprint(self) -> str:
        digest = hashlib.sha256()

        ignored_directories = {
            ".git",
            "__pycache__",
            ".venv",
            "node_modules",
            ".next",
            "dist",
            "build",
            ".vercel",
        }

        files = []

        try:
            for path in self.project_root.rglob("*"):
                if not path.is_file():
                    continue

                if any(
                    part in ignored_directories
                    for part in path.parts
                ):
                    continue

                try:
                    relative = path.relative_to(
                        self.project_root
                    )

                    files.append(
                        (
                            str(relative).replace("\\", "/"),
                            path,
                        )
                    )

                except ValueError:
                    continue

            files.sort(
                key=lambda item: item[0].lower()
            )

            for relative, path in files:
                digest.update(
                    relative.encode("utf-8")
                )

                digest.update(
                    path.read_bytes()
                )

        except OSError:
            pass

        return digest.hexdigest()

    # ---------------------------------------------------------
    # Final safety decision
    # ---------------------------------------------------------

    def calculate_readiness(
        self,
        phase15: dict[str, Any],
        phase151: dict[str, Any],
        phase152: dict[str, Any],
        phase153: dict[str, Any],
        phase154: dict[str, Any],
        git: dict[str, Any],
        vercel: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        failures: list[str] = []

        if not phase15.get("success"):
            failures.append(
                "Phase 15 verification failed."
            )

        if not phase151.get("success"):
            failures.append(
                "Phase 15.1 verification failed."
            )

        if not phase152.get("success"):
            failures.append(
                "Phase 15.2 verification failed."
            )

        if not phase153.get("success"):
            failures.append(
                "Phase 15.3 verification failed."
            )

        if not phase154.get("success"):
            failures.append(
                "Phase 15.4 verification failed."
            )

        if not git.get("available"):
            failures.append(
                "Git is not available."
            )

        if not git.get("repository"):
            failures.append(
                "Git repository was not detected."
            )

        if not git.get("remote_configured"):
            failures.append(
                "Git origin remote is not configured."
            )

        if not git.get("github_remote"):
            failures.append(
                "Git origin does not appear to point to GitHub."
            )

        # Vercel is intentionally reported as a readiness item.
        # It does not make the phase crash if the CLI is missing.
        if not vercel.get("cli_available"):
            failures.append(
                "Vercel CLI is not installed."
            )

        return (
            len(failures) == 0,
            failures,
        )

    # ---------------------------------------------------------
    # Main execution
    # ---------------------------------------------------------

    def run(self) -> dict[str, Any]:
        self.log(
            "Starting Phase 15.5 environment verification..."
        )

        self.log(
            "IMPORTANT: No deployment will be performed."
        )

        self.report_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        phase15 = self.verify_phase15()

        if not phase15["success"]:
            return self.write_blocked_report(
                "phase15",
                phase15,
            )

        self.log(
            "Phase 15 deployment gate PASSED."
        )

        phase151 = self.verify_phase151()

        if not phase151["success"]:
            return self.write_blocked_report(
                "phase15_1",
                phase151,
            )

        self.log(
            "Phase 15.1 authorization gate PASSED."
        )

        phase152 = self.verify_phase152()

        if not phase152["success"]:
            return self.write_blocked_report(
                "phase15_2",
                phase152,
            )

        self.log(
            "Phase 15.2 approval validation PASSED."
        )

        phase153 = self.verify_phase153()

        if not phase153["success"]:
            return self.write_blocked_report(
                "phase15_3",
                phase153,
            )

        self.log(
            "Phase 15.3 authorization PASSED."
        )

        phase154 = self.verify_phase154()

        if not phase154["success"]:
            return self.write_blocked_report(
                "phase15_4",
                phase154,
            )

        self.log(
            "Phase 15.4 controlled deployment dry run PASSED."
        )

        self.log("Validating Git environment...")

        git = self.verify_git()

        self.log(
            f"Git available: {git.get('available')}"
        )

        self.log(
            f"Git repository: {git.get('repository')}"
        )

        if git.get("branch"):
            self.log(
                f"Git branch: {git.get('branch')}"
            )

        self.log("Validating Vercel environment...")

        vercel = self.verify_vercel()

        self.log(
            f"Vercel CLI available: "
            f"{vercel.get('cli_available')}"
        )

        self.log(
            f"Vercel authenticated: "
            f"{vercel.get('authenticated')}"
        )

        environment = (
            self.verify_environment_files()
        )

        secrets = self.verify_secret_safety()

        build = self.detect_build_system()

        fingerprint = self.calculate_fingerprint()

        ready, failures = self.calculate_readiness(
            phase15,
            phase151,
            phase152,
            phase153,
            phase154,
            git,
            vercel,
        )

        if ready:
            stage = "deployment_environment_ready"
            gate = "PASSED"
            status = "ENVIRONMENT_READY"
        else:
            stage = "deployment_environment_blocked"
            gate = "BLOCKED"
            status = "ENVIRONMENT_NOT_READY"

        report: dict[str, Any] = {
            "phase": self.PHASE,
            "success": True,
            "stage": stage,
            "gate": gate,
            "timestamp": self.timestamp,
            "deployment_status": status,
            "deployment_executed": False,
            "source_modified": False,
            "rollback_performed": False,
            "deployment_allowed": False,
            "phase15": phase15,
            "phase15_1": phase151,
            "phase15_2": phase152,
            "phase15_3": phase153,
            "phase15_4": phase154,
            "git": git,
            "vercel": vercel,
            "environment": environment,
            "secrets": secrets,
            "build": build,
            "project": {
                "root": str(self.project_root),
                "exists": self.project_root.exists(),
                "is_directory": (
                    self.project_root.is_dir()
                ),
                "fingerprint": fingerprint,
            },
            "readiness": {
                "ready": ready,
                "failures": failures,
            },
            "safety_policy": {
                "deployment": False,
                "automatic_deployment": False,
                "source_modification": False,
                "token_consumption": False,
                "secret_values_printed": False,
                "secret_values_stored": False,
                "rollback": False,
                "dry_run_only": True,
            },
            "conclusion": (
                "Phase 15.5 completed deployment "
                "environment verification. No deployment "
                "was performed and no source files were "
                "modified."
            ),
        }

        report_path = self.write_report(report)

        self.log(
            f"Phase 15.5 audit written to: {report_path}"
        )

        print()
        print("=" * 60)
        print("FINAL PHASE 15.5 RESULT")
        print("=" * 60)

        print(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
            )
        )

        return report

    # ---------------------------------------------------------
    # Blocked report
    # ---------------------------------------------------------

    def write_blocked_report(
        self,
        stage: str,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        report = {
            "phase": self.PHASE,
            "success": False,
            "stage": stage,
            "gate": "BLOCKED",
            "timestamp": self.timestamp,
            "deployment_status": "BLOCKED",
            "deployment_executed": False,
            "source_modified": False,
            "rollback_performed": False,
            "deployment_allowed": False,
            "details": details,
            "safety_policy": {
                "deployment": False,
                "source_modification": False,
                "automatic_deployment": False,
                "rollback": False,
                "dry_run_only": True,
            },
            "conclusion": (
                "Phase 15.5 was blocked because a required "
                "previous phase did not pass validation."
            ),
        }

        report_path = self.write_report(report)

        self.log(
            f"Phase 15.5 blocked. Audit: {report_path}"
        )

        print()
        print("=" * 60)
        print("FINAL PHASE 15.5 RESULT")
        print("=" * 60)

        print(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
            )
        )

        return report

    # ---------------------------------------------------------
    # Write report
    # ---------------------------------------------------------

    def write_report(
        self,
        report: dict[str, Any],
    ) -> Path:
        self.report_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d_%H%M%S"
        )

        path = (
            self.report_dir
            / f"environment_verification_{timestamp}.json"
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                report,
                handle,
                indent=2,
                ensure_ascii=False,
            )

        return path


def main() -> int:
    executor = Phase15_5EnvironmentVerification()

    result = executor.run()

    # Phase 15.5 is a verification phase.
    # A missing Vercel CLI can make readiness BLOCKED,
    # but the phase itself still completed safely.
    #
    # Return non-zero only when the verification pipeline
    # itself failed, not merely because deployment tooling
    # is missing.

    if result.get("stage") in {
        "phase15",
        "phase15_1",
        "phase15_2",
        "phase15_3",
        "phase15_4",
    }:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
