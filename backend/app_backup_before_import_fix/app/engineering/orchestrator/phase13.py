from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class Phase13PostExecutionVerification:
    """
    PHASE 13 - POST-EXECUTION VERIFICATION

    Responsibilities:
    1. Locate the latest Phase 12.1 audit.
    2. Validate the Phase 12.1 result.
    3. Verify whether source files were modified.
    4. Verify source integrity.
    5. Run Phase 9 again after Phase 12.1.
    6. Produce an independent Phase 13 verdict.

    Phase 13 does NOT modify source code.
    Phase 13 does NOT perform repairs.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
    ) -> None:
        self.project_root = Path(project_root).resolve()

        self.backend_root = (
            self.project_root / "backend"
        )

        self.qa_root = (
            self.project_root.parent
            / "generated"
            / "_code.qa"
        )

        self.phase12_1_dir = (
            self.qa_root / "phase12.1"
        )

        self.phase13_dir = (
            self.qa_root / "phase13"
        )

        self.phase13_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log(self, message: str) -> None:
        print(
            f"[{datetime.now().isoformat()}] "
            f"[PHASE 13] {message}"
        )

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

    def calculate_file_hash(
        self,
        path: Path,
    ) -> str:
        digest = hashlib.sha256()

        with path.open(
            "rb"
        ) as handle:
            for chunk in iter(
                lambda: handle.read(1024 * 1024),
                b"",
            ):
                digest.update(chunk)

        return digest.hexdigest()

    def snapshot_source(
        self,
    ) -> dict[str, str]:
        """
        Create a deterministic hash snapshot
        of the backend source tree.

        Generated QA directories and caches are excluded.
        """

        snapshot: dict[str, str] = {}

        if not self.backend_root.exists():
            return snapshot

        excluded = {
            ".git",
            ".venv",
            "__pycache__",
            "node_modules",
        }

        for path in self.backend_root.rglob("*"):
            if not path.is_file():
                continue

            relative = path.relative_to(
                self.backend_root
            )

            if any(
                part in excluded
                for part in relative.parts
            ):
                continue

            try:
                snapshot[str(relative)] = (
                    self.calculate_file_hash(path)
                )
            except OSError:
                continue

        return snapshot

    def compare_snapshots(
        self,
        before: dict[str, str],
        after: dict[str, str],
    ) -> dict[str, Any]:
        before_keys = set(before)
        after_keys = set(after)

        added = sorted(
            after_keys - before_keys
        )

        removed = sorted(
            before_keys - after_keys
        )

        changed = sorted(
            key
            for key in (
                before_keys & after_keys
            )
            if before[key] != after[key]
        )

        return {
            "changed": changed,
            "added": added,
            "removed": removed,
            "modified": bool(
                changed
                or added
                or removed
            ),
        }

    def check_phase12_1(
        self,
    ) -> tuple[bool, dict[str, Any]]:
        self.log(
            "Checking Phase 12.1 execution audit..."
        )

        report = self.latest_json(
            self.phase12_1_dir
        )

        if report is None:
            result = {
                "success": False,
                "error": (
                    "No Phase 12.1 audit was found."
                ),
                "directory": str(
                    self.phase12_1_dir
                ),
            }

            return False, result

        try:
            data = self.load_json(report)
        except Exception as exc:
            return False, {
                "success": False,
                "error": str(exc),
                "source_report": str(report),
            }

        phase = str(
            data.get("phase", "")
        )

        success = bool(
            data.get("success", False)
        )

        gate = str(
            data.get("gate", "")
        ).upper()

        source_modified = bool(
            data.get(
                "source_modified",
                False,
            )
        )

        repair_executed = bool(
            data.get(
                "repair_executed",
                False,
            )
        )

        rollback_performed = bool(
            data.get(
                "rollback_performed",
                False,
            )
        )

        valid_phase = phase == "12.1"

        audit_valid = (
            valid_phase
            and success
            and gate == "PASSED"
        )

        result = {
            "success": audit_valid,
            "phase": phase,
            "gate": gate,
            "source_modified":
                source_modified,
            "repair_executed":
                repair_executed,
            "rollback_performed":
                rollback_performed,
            "audit_valid":
                audit_valid,
            "source_report":
                str(report),
        }

        if audit_valid:
            self.log(
                "Phase 12.1 audit is valid."
            )
        else:
            self.log(
                "Phase 12.1 audit validation FAILED."
            )

        return audit_valid, result

    def run_phase9(
        self,
    ) -> dict[str, Any]:
        self.log(
            "Running independent Phase 9 post-execution QA..."
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
                timeout=300,
            )

            return {
                "success":
                    result.returncode == 0,
                "returncode":
                    result.returncode,
                "stdout":
                    result.stdout[-15000:],
                "stderr":
                    result.stderr[-15000:],
            }

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    def write_audit(
        self,
        result: dict[str, Any],
    ) -> Path:
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output = (
            self.phase13_dir
            / f"verification_{timestamp}.json"
        )

        output.write_text(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return output

    def run(self) -> dict[str, Any]:
        self.log(
            "Starting Phase 13 post-execution verification..."
        )

        # ---------------------------------------------------------
        # PHASE 12.1 AUDIT
        # ---------------------------------------------------------

        phase12_ok, phase12 = (
            self.check_phase12_1()
        )

        if not phase12_ok:
            result = {
                "phase": "13",
                "success": False,
                "stage":
                    "phase12_1_validation",
                "gate": "BLOCKED",
                "error":
                    "Phase 12.1 audit could not be validated.",
                "phase12_1":
                    phase12,
                "verification": {
                    "phase12_1_audit_valid":
                        False,
                    "source_integrity":
                        False,
                    "post_execution_qa":
                        False,
                },
                "source_modified":
                    False,
                "repair_executed":
                    False,
                "rollback_performed":
                    False,
            }

            audit = self.write_audit(
                result
            )

            self.log(
                f"Verification blocked. Audit: {audit}"
            )

            return result

        # ---------------------------------------------------------
        # SOURCE SNAPSHOT
        # ---------------------------------------------------------

        self.log(
            "Creating current source integrity snapshot..."
        )

        source_before = (
            self.snapshot_source()
        )

        self.log(
            f"Source files hashed: {len(source_before)}"
        )

        # ---------------------------------------------------------
        # POST-EXECUTION QA
        # ---------------------------------------------------------

        phase9 = self.run_phase9()

        # ---------------------------------------------------------
        # SECOND SOURCE SNAPSHOT
        # ---------------------------------------------------------

        self.log(
            "Creating post-QA source integrity snapshot..."
        )

        source_after = (
            self.snapshot_source()
        )

        integrity = self.compare_snapshots(
            source_before,
            source_after,
        )

        source_integrity = not integrity[
            "modified"
        ]

        self.log(
            "Source integrity: "
            + (
                "UNCHANGED"
                if source_integrity
                else "CHANGED"
            )
        )

        # ---------------------------------------------------------
        # EXPECTED MODIFICATION STATE
        # ---------------------------------------------------------

        expected_modified = bool(
            phase12.get(
                "source_modified",
                False,
            )
        )

        repair_executed = bool(
            phase12.get(
                "repair_executed",
                False,
            )
        )

        rollback_performed = bool(
            phase12.get(
                "rollback_performed",
                False,
            )
        )

        actual_modified = bool(
            integrity["modified"]
        )

        modification_consistent = (
            actual_modified
            == expected_modified
        )

        # ---------------------------------------------------------
        # FINAL VERIFICATION
        # ---------------------------------------------------------

        post_qa_success = bool(
            phase9.get(
                "success",
                False,
            )
        )

        all_checks_passed = (
            phase12_ok
            and post_qa_success
            and source_integrity
            and modification_consistent
        )

        if all_checks_passed:
            gate = "PASSED"
            stage = (
                "post_execution_verification"
            )

            conclusion = (
                "Phase 12.1 completed safely. "
                "No unexpected source modifications "
                "were detected and independent Phase 9 "
                "verification passed."
            )

            self.log(
                "Phase 13 verification PASSED."
            )

        else:
            gate = "BLOCKED"
            stage = (
                "post_execution_verification_failed"
            )

            conclusion = (
                "Phase 13 detected a verification "
                "failure. Manual investigation is required."
            )

            self.log(
                "Phase 13 verification BLOCKED."
            )

        result = {
            "phase": "13",
            "success":
                all_checks_passed,
            "stage":
                stage,
            "gate":
                gate,
            "timestamp":
                datetime.now().isoformat(),

            "phase12_1": {
                "success":
                    phase12.get(
                        "success",
                        False,
                    ),
                "audit_valid":
                    phase12.get(
                        "audit_valid",
                        False,
                    ),
                "source_modified":
                    expected_modified,
                "repair_executed":
                    repair_executed,
                "rollback_performed":
                    rollback_performed,
                "source_report":
                    phase12.get(
                        "source_report"
                    ),
            },

            "verification": {
                "phase12_1_audit_valid":
                    phase12_ok,
                "source_integrity":
                    source_integrity,
                "post_execution_qa":
                    post_qa_success,
                "modification_consistent":
                    modification_consistent,
            },

            "source_integrity": {
                "files_before":
                    len(source_before),
                "files_after":
                    len(source_after),
                "actual_modified":
                    actual_modified,
                "changed":
                    integrity["changed"],
                "added":
                    integrity["added"],
                "removed":
                    integrity["removed"],
            },

            "phase9_post_execution":
                phase9,

            "source_modified":
                actual_modified,

            "repair_executed":
                repair_executed,

            "rollback_performed":
                rollback_performed,

            "conclusion":
                conclusion,
        }

        audit = self.write_audit(
            result
        )

        self.log(
            f"Phase 13 audit written to: {audit}"
        )

        print("")
        print("=" * 60)
        print("FINAL PHASE 13 RESULT")
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
    verifier = Phase13PostExecutionVerification()
    verifier.run()


if __name__ == "__main__":
    main()

