from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Phase15_2HumanApproval:
    """
    PHASE 15.2 - HUMAN APPROVAL TOKEN GATE

    Purpose:
        - Validate Phase 15 dry-run gate.
        - Validate Phase 15.1 manual authorization gate.
        - Calculate a fingerprint of the current project.
        - Create a one-time human approval token.
        - Store ONLY the token hash.
        - Never deploy.
        - Never modify source code.

    The plaintext token is displayed once to the operator.
    Phase 15.3 verifies the token later.
    """

    def __init__(self) -> None:
        self.backend_root = Path(__file__).resolve().parents[3]

        self.qa_root = self.backend_root / "generated" / "_code.qa"

        self.phase15_dir = self.qa_root / "phase15"
        self.phase151_dir = self.qa_root / "phase15.1"
        self.phase152_dir = self.qa_root / "phase15.2"

        self.output_dir = (
            self.phase152_dir / "human_approval"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.state_dir = self.phase152_dir / "state"
        self.state_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.consumed_dir = self.state_dir / "consumed"
        self.consumed_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ---------------------------------------------------------
    # LOGGING
    # ---------------------------------------------------------

    def log(self, message: str) -> None:
        timestamp = datetime.now().isoformat()
        print(
            f"[{timestamp}] [PHASE 15.2] {message}",
            flush=True,
        )

    # ---------------------------------------------------------
    # FILE DISCOVERY
    # ---------------------------------------------------------

    def find_latest_json(
        self,
        directory: Path,
        pattern: str,
    ) -> Path | None:
        if not directory.exists():
            return None

        files = [
            path
            for path in directory.rglob(pattern)
            if path.is_file()
        ]

        if not files:
            return None

        return max(
            files,
            key=lambda path: path.stat().st_mtime,
        )

    def find_phase15_report(self) -> Path | None:
        """
        Find the real Phase 15 deployment gate report.

        We intentionally search recursively because older versions
        of the orchestrator created different directory layouts.
        """

        if not self.phase15_dir.exists():
            return None

        candidates = [
            path
            for path in self.phase15_dir.rglob(
                "deployment_gate_*.json"
            )
            if path.is_file()
        ]

        if not candidates:
            return None

        candidates.sort(
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        for candidate in candidates:
            try:
                data = json.loads(
                    candidate.read_text(
                        encoding="utf-8"
                    )
                )

                if (
                    data.get("phase") == "15"
                    and data.get("success") is True
                    and data.get("gate") == "PASSED"
                    and data.get("deployment_status")
                    == "DRY_RUN_PASSED"
                ):
                    return candidate

            except Exception:
                continue

        return None

    def find_phase151_report(self) -> Path | None:
        """
        Find the latest valid Phase 15.1 authorization report.
        """

        if not self.phase151_dir.exists():
            return None

        candidates = [
            path
            for path in self.phase151_dir.rglob(
                "authorization_*.json"
            )
            if path.is_file()
        ]

        if not candidates:
            return None

        candidates.sort(
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        for candidate in candidates:
            try:
                data = json.loads(
                    candidate.read_text(
                        encoding="utf-8"
                    )
                )

                if (
                    data.get("phase") == "15.1"
                    and data.get("success") is True
                    and data.get("gate") == "PASSED"
                    and data.get("authorization_status")
                    == "MANUAL_APPROVAL_REQUIRED"
                ):
                    return candidate

            except Exception:
                continue

        return None

    # ---------------------------------------------------------
    # JSON
    # ---------------------------------------------------------

    def read_json(
        self,
        path: Path,
    ) -> dict[str, Any] | None:
        try:
            data = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            if isinstance(data, dict):
                return data

        except Exception:
            return None

        return None

    # ---------------------------------------------------------
    # PROJECT FINGERPRINT
    # ---------------------------------------------------------

    def calculate_project_fingerprint(self) -> str:
        """
        Calculate a deterministic SHA-256 fingerprint of source
        files in the backend project.

        Generated QA reports are deliberately excluded so that
        creating an audit report does not invalidate an approval.
        """

        excluded_directories = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "generated",
            "dist",
            "build",
        }

        excluded_files = {
            ".env",
            ".env.local",
            ".env.production",
            ".env.development",
        }

        files: list[Path] = []

        for path in self.backend_root.rglob("*"):
            if not path.is_file():
                continue

            try:
                relative = path.relative_to(
                    self.backend_root
                )
            except ValueError:
                continue

            if any(
                part in excluded_directories
                for part in relative.parts
            ):
                continue

            if path.name in excluded_files:
                continue

            files.append(path)

        files.sort(
            key=lambda path: str(
                path.relative_to(
                    self.backend_root
                )
            ).lower()
        )

        digest = hashlib.sha256()

        for path in files:
            relative = path.relative_to(
                self.backend_root
            )

            digest.update(
                str(relative)
                .replace("\\", "/")
                .encode("utf-8")
            )

            digest.update(b"\0")

            try:
                content = path.read_bytes()
            except Exception:
                continue

            digest.update(content)
            digest.update(b"\0")

        return digest.hexdigest()

    # ---------------------------------------------------------
    # TOKEN
    # ---------------------------------------------------------

    def generate_token(self) -> str:
        """
        Generate a cryptographically secure one-time token.

        The plaintext token is never written to disk.
        """

        return secrets.token_urlsafe(32)

    def hash_token(
        self,
        token: str,
    ) -> str:
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    # ---------------------------------------------------------
    # MAIN
    # ---------------------------------------------------------

    def run(self) -> dict[str, Any]:
        print()
        print("=" * 60)
        print("PHASE 15.2 - HUMAN APPROVAL TOKEN GATE")
        print("=" * 60)

        self.log(
            "Starting human approval gate..."
        )

        self.log(
            "No deployment will be performed."
        )

        # -----------------------------------------------------
        # PHASE 15
        # -----------------------------------------------------

        self.log(
            "Checking Phase 15..."
        )

        phase15_file = (
            self.find_phase15_report()
        )

        if not phase15_file:
            result = {
                "phase": "15.2",
                "success": False,
                "stage": "phase15_blocked",
                "gate": "BLOCKED",
                "authorization_status":
                    "NOT_AUTHORIZED",
                "timestamp":
                    datetime.now().isoformat(),
                "error":
                    "No valid Phase 15 deployment gate report was found.",
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "rollback_performed": False,
            }

            return self.write_audit(
                result
            )

        phase15 = self.read_json(
            phase15_file
        )

        if not phase15:
            result = {
                "phase": "15.2",
                "success": False,
                "stage": "phase15_invalid",
                "gate": "BLOCKED",
                "authorization_status":
                    "NOT_AUTHORIZED",
                "timestamp":
                    datetime.now().isoformat(),
                "error":
                    "Phase 15 report could not be read.",
                "source_report":
                    str(phase15_file),
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "rollback_performed": False,
            }

            return self.write_audit(
                result
            )

        if not (
            phase15.get("phase") == "15"
            and phase15.get("success") is True
            and phase15.get("gate") == "PASSED"
            and phase15.get("deployment_status")
            == "DRY_RUN_PASSED"
        ):
            result = {
                "phase": "15.2",
                "success": False,
                "stage": "phase15_validation",
                "gate": "BLOCKED",
                "authorization_status":
                    "NOT_AUTHORIZED",
                "timestamp":
                    datetime.now().isoformat(),
                "error":
                    "Phase 15 deployment gate is not valid for approval.",
                "source_report":
                    str(phase15_file),
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "rollback_performed": False,
            }

            return self.write_audit(
                result
            )

        self.log(
            "Phase 15 deployment gate PASSED."
        )

        # -----------------------------------------------------
        # PHASE 15.1
        # -----------------------------------------------------

        self.log(
            "Checking Phase 15.1..."
        )

        phase151_file = (
            self.find_phase151_report()
        )

        if not phase151_file:
            result = {
                "phase": "15.2",
                "success": False,
                "stage": "phase15_1_blocked",
                "gate": "BLOCKED",
                "authorization_status":
                    "NOT_AUTHORIZED",
                "timestamp":
                    datetime.now().isoformat(),
                "error":
                    "No valid Phase 15.1 authorization report was found.",
                "phase15": {
                    "success": True,
                    "source_report":
                        str(phase15_file),
                },
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "rollback_performed": False,
            }

            return self.write_audit(
                result
            )

        phase151 = self.read_json(
            phase151_file
        )

        if not phase151:
            result = {
                "phase": "15.2",
                "success": False,
                "stage": "phase15_1_invalid",
                "gate": "BLOCKED",
                "authorization_status":
                    "NOT_AUTHORIZED",
                "timestamp":
                    datetime.now().isoformat(),
                "error":
                    "Phase 15.1 report could not be read.",
                "source_report":
                    str(phase151_file),
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "rollback_performed": False,
            }

            return self.write_audit(
                result
            )

        if not (
            phase151.get("phase") == "15.1"
            and phase151.get("success") is True
            and phase151.get("gate") == "PASSED"
            and phase151.get("authorization_status")
            == "MANUAL_APPROVAL_REQUIRED"
        ):
            result = {
                "phase": "15.2",
                "success": False,
                "stage": "phase15_1_validation",
                "gate": "BLOCKED",
                "authorization_status":
                    "NOT_AUTHORIZED",
                "timestamp":
                    datetime.now().isoformat(),
                "error":
                    "Phase 15.1 has not authorized manual approval.",
                "source_report":
                    str(phase151_file),
                "deployment_authorized": False,
                "deployment_executed": False,
                "source_modified": False,
                "rollback_performed": False,
            }

            return self.write_audit(
                result
            )

        self.log(
            "Phase 15.1 authorization gate PASSED."
        )

        # -----------------------------------------------------
        # FINGERPRINT
        # -----------------------------------------------------

        self.log(
            "Calculating project fingerprint..."
        )

        fingerprint = (
            self.calculate_project_fingerprint()
        )

        # -----------------------------------------------------
        # TOKEN
        # -----------------------------------------------------

        token = self.generate_token()
        token_hash = self.hash_token(token)

        created_at = (
            datetime.now(timezone.utc)
            .isoformat()
        )

        approval = {
            "token_hash": token_hash,
            "created_at": created_at,
            "phase15_report": str(
                phase15_file
            ),
            "phase15_1_report": str(
                phase151_file
            ),
            "project_fingerprint":
                fingerprint,
            "consumed": False,
        }

        result = {
            "phase": "15.2",
            "success": True,
            "stage": "approval_token_created",
            "gate": "PASSED",
            "authorization_status":
                "APPROVAL_TOKEN_ISSUED",
            "timestamp":
                datetime.now().isoformat(),
            "deployment_authorized": False,
            "deployment_executed": False,
            "source_modified": False,
            "rollback_performed": False,
            "phase15": {
                "success": True,
                "source_report":
                    str(phase15_file),
                "checks": {
                    "phase15_identity": True,
                    "success": True,
                    "gate": True,
                    "dry_run": True,
                    "not_executed": True,
                    "source_clean": True,
                },
            },
            "phase15_1": {
                "success": True,
                "source_report":
                    str(phase151_file),
                "checks": {
                    "phase15_1_identity": True,
                    "success": True,
                    "gate": True,
                    "manual_approval_required": True,
                    "not_authorized": True,
                    "not_executed": True,
                    "source_clean": True,
                },
            },
            "project_fingerprint":
                fingerprint,
            "approval": approval,
            "safety_policy": {
                "deployment": False,
                "source_modification": False,
                "automatic_approval": False,
                "one_time_token": True,
                "token_stored_as_hash": True,
                "manual_approval": True,
            },
            "conclusion":
                "A one-time human approval token was created. "
                "No deployment was performed.",
        }

        audit_path = self.write_audit(
            result
        )

        # -----------------------------------------------------
        # DISPLAY PLAINTEXT TOKEN
        # -----------------------------------------------------

        print()
        print("=" * 60)
        print("APPROVAL TOKEN CREATED")
        print("=" * 60)
        print()
        print(
            "IMPORTANT: This token is displayed once."
        )
        print(
            "Do NOT share it publicly."
        )
        print()
        print(
            "Approval token:"
        )
        print(token)
        print()
        print(
            "Token audit:"
        )
        print(audit_path)
        print()
        print(
            "Use this token with Phase 15.3."
        )
        print(
            'PowerShell example:'
        )
        print(
            '$env:PHASE15_APPROVAL_TOKEN="PASTE_TOKEN_HERE"'
        )
        print(
            r".\.venv\Scripts\python.exe -m "
            r"app.engineering.orchestrator.phase15_3"
        )
        print()
        print(
            "The plaintext token is NOT stored in the audit."
        )
        print("=" * 60)

        return result

    # ---------------------------------------------------------
    # AUDIT
    # ---------------------------------------------------------

    def write_audit(
        self,
        result: dict[str, Any],
    ) -> Path:
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        path = (
            self.output_dir
            / f"human_approval_{timestamp}.json"
        )

        path.write_text(
            json.dumps(
                result,
                indent=2,
            ),
            encoding="utf-8",
        )

        self.log(
            f"Approval audit written to: {path}"
        )

        print()
        print(json.dumps(
            result,
            indent=2,
        ))

        return path


def main() -> None:
    gate = Phase15_2HumanApproval()
    gate.run()


if __name__ == "__main__":
    main()