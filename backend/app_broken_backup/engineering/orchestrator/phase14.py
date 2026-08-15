from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class Phase14ReleaseGate:
    """
    PHASE 14 - ENGINEERING RELEASE GATE

    Final read-only release verification layer.

    Responsibilities:
    1. Locate the latest Phase 13 verification report.
    2. Validate Phase 13 success.
    3. Validate Phase 13 gate status.
    4. Validate Phase 12.1 audit evidence.
    5. Validate source integrity.
    6. Validate post-execution Phase 9 QA.
    7. Confirm no unexpected source modifications.
    8. Produce RELEASE_READY or BLOCKED.

    Phase 14 NEVER modifies source code.
    Phase 14 NEVER performs repairs.
    Phase 14 NEVER deploys the application.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
    ) -> None:
        self.project_root = Path(project_root).resolve()

        self.qa_root = (
            self.project_root.parent
            / "generated"
            / "_code.qa"
        )

        self.phase13_dir = (
            self.qa_root / "phase13"
        )

        self.phase14_dir = (
            self.qa_root / "phase14"
        )

        self.phase14_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log(self, message: str) -> None:
        print(
            f"[{datetime.now().isoformat()}] "
            f"[PHASE 14] {message}"
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

    def validate_phase13(
        self,
    ) -> tuple[bool, dict[str, Any]]:
        self.log(
            "Checking latest Phase 13 verification..."
        )

        report = self.latest_json(
            self.phase13_dir
        )

        if report is None:
            return False, {
                "success": False,
                "error":
                    "No Phase 13 verification report was found.",
                "searched_path":
                    str(self.phase13_dir),
            }

        try:
            data = self.load_json(report)
        except Exception as exc:
            return False, {
                "success": False,
                "error":
                    f"Invalid Phase 13 JSON: {exc}",
                "source_report":
                    str(report),
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

        stage = str(
            data.get("stage", "")
        )

        verification = data.get(
            "verification",
            {},
        )

        if not isinstance(
            verification,
            dict,
        ):
            verification = {}

        phase12_1 = data.get(
            "phase12_1",
            {},
        )

        if not isinstance(
            phase12_1,
            dict,
        ):
            phase12_1 = {}

        phase9 = data.get(
            "phase9_post_execution",
            {},
        )

        if not isinstance(
            phase9,
            dict,
        ):
            phase9 = {}

        checks = {
            "phase13_identity":
                phase == "13",

            "phase13_success":
                success,

            "phase13_gate":
                gate == "PASSED",

            "post_execution_stage":
                stage
                == "post_execution_verification",

            "phase12_1_audit_valid":
                bool(
                    verification.get(
                        "phase12_1_audit_valid",
                        False,
                    )
                ),

            "source_integrity":
                bool(
                    verification.get(
                        "source_integrity",
                        False,
                    )
                ),

            "post_execution_qa":
                bool(
                    verification.get(
                        "post_execution_qa",
                        False,
                    )
                ),

            "modification_consistent":
                bool(
                    verification.get(
                        "modification_consistent",
                        False,
                    )
                ),

            "phase12_1_success":
                bool(
                    phase12_1.get(
                        "success",
                        False,
                    )
                ),

            "phase9_success":
                bool(
                    phase9.get(
                        "success",
                        False,
                    )
                ),

            "unexpected_modification":
                not bool(
                    data.get(
                        "source_modified",
                        False,
                    )
                ),
        }

        all_checks_passed = all(
            checks.values()
        )

        result = {
            "success":
                all_checks_passed,
            "source_report":
                str(report),
            "checks":
                checks,
            "phase13": {
                "phase":
                    phase,
                "success":
                    success,
                "gate":
                    gate,
                "stage":
                    stage,
            },
            "phase12_1": {
                "success":
                    bool(
                        phase12_1.get(
                            "success",
                            False,
                        )
                    ),
                "source_modified":
                    bool(
                        phase12_1.get(
                            "source_modified",
                            False,
                        )
                    ),
                "repair_executed":
                    bool(
                        phase12_1.get(
                            "repair_executed",
                            False,
                        )
                    ),
                "rollback_performed":
                    bool(
                        phase12_1.get(
                            "rollback_performed",
                            False,
                        )
                    ),
            },
            "phase9_post_execution": {
                "success":
                    bool(
                        phase9.get(
                            "success",
                            False,
                        )
                    ),
            },
        }

        if all_checks_passed:
            self.log(
                "Phase 13 evidence is valid."
            )
        else:
            self.log(
                "Phase 13 release evidence FAILED."
            )

        return (
            all_checks_passed,
            result,
        )

    def write_report(
        self,
        result: dict[str, Any],
    ) -> Path:
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output = (
            self.phase14_dir
            / f"release_gate_{timestamp}.json"
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
        print("=" * 60)
        print(
            "PHASE 14 - ENGINEERING RELEASE GATE"
        )
        print("=" * 60)

        self.log(
            "Starting final read-only release verification..."
        )

        valid, phase13 = (
            self.validate_phase13()
        )

        if not valid:
            result = {
                "phase": "14",
                "success": False,
                "stage":
                    "phase13_validation",
                "gate": "BLOCKED",
                "release_status":
                    "BLOCKED",
                "timestamp":
                    datetime.now().isoformat(),
                "phase13":
                    phase13,
                "source_modified":
                    False,
                "repair_executed":
                    False,
                "deployment_authorized":
                    False,
                "conclusion":
                    (
                        "Release blocked because "
                        "Phase 13 verification evidence "
                        "is incomplete or failed."
                    ),
            }

            report = self.write_report(
                result
            )

            self.log(
                f"Release audit written to: {report}"
            )

            print("")
            print("=" * 60)
            print(
                "FINAL PHASE 14 RESULT"
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

        result = {
            "phase": "14",
            "success": True,
            "stage":
                "release_gate_verification",
            "gate": "PASSED",
            "release_status":
                "RELEASE_READY",
            "timestamp":
                datetime.now().isoformat(),

            "phase13": phase13,

            "release_checks": {
                "phase13_verified":
                    True,

                "phase12_1_verified":
                    True,

                "source_integrity_verified":
                    True,

                "post_execution_qa_verified":
                    True,

                "unexpected_modifications":
                    False,

                "repair_execution_required":
                    False,
            },

            "source_modified":
                False,

            "repair_executed":
                False,

            "deployment_authorized":
                False,

            "conclusion": (
                "All engineering release checks passed. "
                "The project is RELEASE_READY. "
                "Phase 14 performs no deployment."
            ),
        }

        report = self.write_report(
            result
        )

        self.log(
            "All release checks PASSED."
        )

        self.log(
            "Release status: RELEASE_READY"
        )

        self.log(
            f"Release audit written to: {report}"
        )

        print("")
        print("=" * 60)
        print(
            "FINAL PHASE 14 RESULT"
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
    gate = Phase14ReleaseGate()
    gate.run()


if __name__ == "__main__":
    main()