from __future__ import annotations

import argparse
import hashlib
import json
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any


class Phase15_3AuthorizationVerifier:
    """
    PHASE 15.3 - DEPLOYMENT AUTHORIZATION VERIFIER

    This phase verifies:

        Phase 15
            |
            v
        Phase 15.1
            |
            v
        Phase 15.2 approval token
            |
            v
        Current project fingerprint
            |
            v
        DEPLOYMENT AUTHORIZED

    IMPORTANT:

        This phase DOES NOT deploy anything.

        This phase:
            - verifies the approval token
            - verifies the project fingerprint
            - verifies the Phase 15 chain
            - consumes the token once
            - writes an audit report

    Token input methods:

        1. --token "TOKEN"

        2. Environment variable:
           PHASE15_APPROVAL_TOKEN

        3. Interactive prompt as a final fallback
    """

    def __init__(
        self,
        token: str | None = None,
    ) -> None:
        self.backend_root = Path(__file__).resolve().parents[3]

        self.qa_root = (
            self.backend_root
            / "generated"
            / "_code.qa"
        )

        self.phase15_dir = (
            self.qa_root / "phase15"
        )

        self.phase151_dir = (
            self.qa_root / "phase15.1"
        )

        self.phase152_dir = (
            self.qa_root / "phase15.2"
        )

        self.phase153_dir = (
            self.qa_root / "phase15.3"
        )

        self.output_dir = (
            self.phase153_dir
            / "authorization_verification"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.state_dir = (
            self.phase152_dir / "state"
        )

        self.consumed_dir = (
            self.state_dir / "consumed"
        )

        self.consumed_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.supplied_token = (
            token.strip()
            if token
            else None
        )

    # ---------------------------------------------------------
    # LOGGING
    # ---------------------------------------------------------

    def log(
        self,
        message: str,
    ) -> None:
        timestamp = datetime.now().isoformat()

        print(
            f"[{timestamp}] [PHASE 15.3] {message}",
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

    def find_phase15_report(
        self,
    ) -> Path | None:
        if not self.phase15_dir.exists():
            return None

        candidates = list(
            self.phase15_dir.rglob(
                "deployment_gate_*.json"
            )
        )

        candidates.sort(
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        for path in candidates:
            try:
                data = self.read_json(path)

                if not data:
                    continue

                if (
                    data.get("phase") == "15"
                    and data.get("success") is True
                    and data.get("gate") == "PASSED"
                    and data.get("deployment_status")
                    == "DRY_RUN_PASSED"
                ):
                    return path

            except Exception:
                continue

        return None

    def find_phase151_report(
        self,
    ) -> Path | None:
        if not self.phase151_dir.exists():
            return None

        candidates = list(
            self.phase151_dir.rglob(
                "authorization_*.json"
            )
        )

        candidates.sort(
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        for path in candidates:
            try:
                data = self.read_json(path)

                if not data:
                    continue

                if (
                    data.get("phase") == "15.1"
                    and data.get("success") is True
                    and data.get("gate") == "PASSED"
                    and data.get("authorization_status")
                    == "MANUAL_APPROVAL_REQUIRED"
                ):
                    return path

            except Exception:
                continue

        return None

    def find_latest_phase152_report(
        self,
    ) -> Path | None:
        if not self.phase152_dir.exists():
            return None

        candidates = list(
            self.phase152_dir.rglob(
                "human_approval_*.json"
            )
        )

        candidates.sort(
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        for path in candidates:
            try:
                data = self.read_json(path)

                if not data:
                    continue

                if (
                    data.get("phase") == "15.2"
                    and data.get("success") is True
                    and data.get("gate") == "PASSED"
                    and data.get(
                        "authorization_status"
                    )
                    == "APPROVAL_TOKEN_ISSUED"
                ):
                    return path

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
    # FINGERPRINT
    # ---------------------------------------------------------

    def calculate_project_fingerprint(
        self,
    ) -> str:
        """
        Must match Phase 15.2 fingerprint logic.

        Generated QA artifacts are excluded.
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

    def get_token(
        self,
    ) -> str | None:
        """
        Token priority:

        1. Constructor token
        2. PHASE15_APPROVAL_TOKEN
        3. Interactive input
        """

        if self.supplied_token:
            return self.supplied_token

        environment_token = (
            __import__("os").environ.get(
                "PHASE15_APPROVAL_TOKEN"
            )
        )

        if environment_token:
            return environment_token.strip()

        print()
        print(
            "A valid Phase 15.2 approval token is required."
        )
        print(
            "Enter the one-time token issued by Phase 15.2."
        )
        print(
            "The token will NOT be stored."
        )

        try:
            token = input(
                "Approval token: "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            return None

        return token or None

    def hash_token(
        self,
        token: str,
    ) -> str:
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    # ---------------------------------------------------------
    # TOKEN CONSUMPTION
    # ---------------------------------------------------------

    def consumed_marker(
        self,
        token_hash: str,
    ) -> Path:
        return (
            self.consumed_dir
            / f"{token_hash}.consumed"
        )

    def is_token_consumed(
        self,
        token_hash: str,
    ) -> bool:
        return self.consumed_marker(
            token_hash
        ).exists()

    def consume_token(
        self,
        token_hash: str,
    ) -> Path:
        marker = self.consumed_marker(
            token_hash
        )

        marker.write_text(
            datetime.now().isoformat(),
            encoding="utf-8",
        )

        return marker

    # ---------------------------------------------------------
    # MAIN
    # ---------------------------------------------------------

    def run(self) -> dict[str, Any]:
        print()
        print("=" * 60)
        print(
            "PHASE 15.3 - DEPLOYMENT AUTHORIZATION VERIFIER"
        )
        print("=" * 60)

        self.log(
            "Starting final deployment authorization verification..."
        )

        # -----------------------------------------------------
        # PHASE 15
        # -----------------------------------------------------

        self.log(
            "Checking Phase 15 deployment gate..."
        )

        phase15_file = (
            self.find_phase15_report()
        )

        if not phase15_file:
            return self.block(
                "phase15_validation",
                "No valid Phase 15 deployment gate report was found.",
            )

        phase15 = self.read_json(
            phase15_file
        )

        if not phase15:
            return self.block(
                "phase15_validation",
                "Phase 15 report could not be read.",
            )

        phase15_valid = (
            phase15.get("phase") == "15"
            and phase15.get("success") is True
            and phase15.get("gate") == "PASSED"
            and phase15.get(
                "deployment_status"
            )
            == "DRY_RUN_PASSED"
            and phase15.get(
                "deployment_executed"
            )
            is False
            and phase15.get(
                "source_modified"
            )
            is False
        )

        if not phase15_valid:
            return self.block(
                "phase15_validation",
                "Phase 15 deployment gate is invalid.",
            )

        self.log(
            "Phase 15 deployment gate PASSED."
        )

        # -----------------------------------------------------
        # PHASE 15.1
        # -----------------------------------------------------

        self.log(
            "Checking Phase 15.1 authorization gate..."
        )

        phase151_file = (
            self.find_phase151_report()
        )

        if not phase151_file:
            return self.block(
                "phase15_1_validation",
                "No valid Phase 15.1 authorization report was found.",
            )

        phase151 = self.read_json(
            phase151_file
        )

        if not phase151:
            return self.block(
                "phase15_1_validation",
                "Phase 15.1 report could not be read.",
            )

        phase151_valid = (
            phase151.get("phase")
            == "15.1"
            and phase151.get("success")
            is True
            and phase151.get("gate")
            == "PASSED"
            and phase151.get(
                "authorization_status"
            )
            == "MANUAL_APPROVAL_REQUIRED"
            and phase151.get(
                "deployment_authorized"
            )
            is False
            and phase151.get(
                "deployment_executed"
            )
            is False
            and phase151.get(
                "source_modified"
            )
            is False
        )

        if not phase151_valid:
            return self.block(
                "phase15_1_validation",
                "Phase 15.1 authorization gate is invalid.",
            )

        self.log(
            "Phase 15.1 authorization gate PASSED."
        )

        # -----------------------------------------------------
        # PHASE 15.2
        # -----------------------------------------------------

        self.log(
            "Checking Phase 15.2 approval token..."
        )

        phase152_file = (
            self.find_latest_phase152_report()
        )

        if not phase152_file:
            return self.block(
                "phase15_2_validation",
                "No valid Phase 15.2 approval token report was found.",
            )

        phase152 = self.read_json(
            phase152_file
        )

        if not phase152:
            return self.block(
                "phase15_2_validation",
                "Phase 15.2 report could not be read.",
            )

        approval = phase152.get(
            "approval",
            {}
        )

        token_hash_expected = (
            approval.get("token_hash")
        )

        fingerprint_expected = (
            approval.get(
                "project_fingerprint"
            )
        )

        if not token_hash_expected:
            return self.block(
                "phase15_2_validation",
                "Phase 15.2 token hash is missing.",
            )

        if not fingerprint_expected:
            return self.block(
                "phase15_2_validation",
                "Phase 15.2 project fingerprint is missing.",
            )

        # -----------------------------------------------------
        # CURRENT FINGERPRINT
        # -----------------------------------------------------

        self.log(
            "Calculating current project fingerprint..."
        )

        current_fingerprint = (
            self.calculate_project_fingerprint()
        )

        fingerprint_match = secrets.compare_digest(
            current_fingerprint,
            fingerprint_expected,
        )

        self.log(
            "Project fingerprint verification: "
            + (
                "PASSED"
                if fingerprint_match
                else "FAILED"
            )
        )

        if not fingerprint_match:
            return self.block(
                "fingerprint_validation",
                "Project fingerprint changed after Phase 15.2 approval.",
                extra={
                    "fingerprint_expected":
                        fingerprint_expected,
                    "fingerprint_current":
                        current_fingerprint,
                },
            )

        # -----------------------------------------------------
        # TOKEN INPUT
        # -----------------------------------------------------

        token = self.get_token()

        if not token:
            return self.block(
                "token_validation",
                "No approval token was supplied.",
            )

        supplied_hash = self.hash_token(
            token
        )

        token_match = secrets.compare_digest(
            supplied_hash,
            token_hash_expected,
        )

        if not token_match:
            return self.block(
                "token_validation",
                "Invalid approval token.",
            )

        # -----------------------------------------------------
        # ONE-TIME TOKEN CHECK
        # -----------------------------------------------------

        if self.is_token_consumed(
            token_hash_expected
        ):
            return self.block(
                "token_consumption",
                "This approval token has already been consumed.",
            )

        # -----------------------------------------------------
        # CONSUME TOKEN
        # -----------------------------------------------------

        consumed_marker = (
            self.consume_token(
                token_hash_expected
            )
        )

        self.log(
            "Approval token verified successfully."
        )

        self.log(
            f"Token consumption marker: {consumed_marker}"
        )

        # -----------------------------------------------------
        # SUCCESS
        # -----------------------------------------------------

        result = {
            "phase": "15.3",
            "success": True,
            "stage":
                "authorization_verified",
            "gate": "PASSED",
            "authorization_status":
                "DEPLOYMENT_AUTHORIZED",
            "timestamp":
                datetime.now().isoformat(),
            "deployment_authorized": True,
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
                    "deployment_not_executed":
                        True,
                    "source_not_modified":
                        True,
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
                    "manual_approval_required":
                        True,
                    "deployment_not_authorized":
                        True,
                    "deployment_not_executed":
                        True,
                    "source_not_modified":
                        True,
                },
            },
            "phase15_2": {
                "success": True,
                "source_report":
                    str(phase152_file),
                "checks": {
                    "phase15_2_identity": True,
                    "success": True,
                    "gate": True,
                    "token_valid": True,
                    "fingerprint_valid":
                        True,
                    "token_not_previously_consumed":
                        True,
                },
            },
            "fingerprint": {
                "expected":
                    fingerprint_expected,
                "current":
                    current_fingerprint,
                "match": True,
            },
            "token": {
                "verified": True,
                "consumed": True,
                "plaintext_stored": False,
                "hash_stored": True,
            },
            "safety_policy": {
                "deployment": False,
                "authorization_verified":
                    True,
                "source_modification": False,
                "rollback": False,
                "one_time_token": True,
            },
            "conclusion":
                "Phase 15.3 verified the human approval token "
                "and project fingerprint. Deployment remains "
                "unexecuted.",
        }

        self.write_audit(
            result
        )

        print()
        print("=" * 60)
        print(
            "FINAL PHASE 15.3 RESULT"
        )
        print("=" * 60)
        print(
            json.dumps(
                result,
                indent=2,
            )
        )

        return result

    # ---------------------------------------------------------
    # BLOCK
    # ---------------------------------------------------------

    def block(
        self,
        stage: str,
        error: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "phase": "15.3",
            "success": False,
            "stage": stage,
            "gate": "BLOCKED",
            "authorization_status":
                "DEPLOYMENT_BLOCKED",
            "timestamp":
                datetime.now().isoformat(),
            "error": error,
            "deployment_authorized": False,
            "deployment_executed": False,
            "source_modified": False,
            "rollback_performed": False,
        }

        if extra:
            result.update(extra)

        self.write_audit(
            result
        )

        print()
        print("=" * 60)
        print(
            "FINAL PHASE 15.3 RESULT"
        )
        print("=" * 60)
        print(
            json.dumps(
                result,
                indent=2,
            )
        )

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
            / (
                "authorization_verification_"
                f"{timestamp}.json"
            )
        )

        path.write_text(
            json.dumps(
                result,
                indent=2,
            ),
            encoding="utf-8",
        )

        self.log(
            f"Authorization audit: {path}"
        )

        return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 15.3 deployment authorization verifier"
        )
    )

    parser.add_argument(
        "--token",
        "-Token",
        dest="token",
        default=None,
        help=(
            "One-time Phase 15.2 approval token."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    verifier = (
        Phase15_3AuthorizationVerifier(
            token=args.token
        )
    )

    verifier.run()


if __name__ == "__main__":
    main()