from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class Phase121GuardedExecution:
    """Phase 12.1 - guarded autonomous execution."""

    def __init__(self, project_root: str = "generated_code") -> None:
        self.project_root = Path(project_root).resolve()

        self.qa_root = (
            self.project_root.parent
            / "generated"
            / "_code.qa"
        )

        self.phase10_1_dir = self.qa_root / "phase10.1"
        self.phase11_dir = self.qa_root / "phase11"
        self.output_dir = self.qa_root / "phase12.1"

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log(self, message: str) -> None:
        print(
            f"[{datetime.now().isoformat()}] "
            f"[PHASE 12.1] {message}"
        )

    def latest_json(self, directory: Path) -> Path | None:
        if not directory.exists():
            return None

        files = list(directory.rglob("*.json"))

        if not files:
            return None

        return max(
            files,
            key=lambda p: p.stat().st_mtime,
        )

    def load_json(self, path: Path) -> dict[str, Any]:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        if not isinstance(data, dict):
            raise ValueError(
                "JSON report must contain an object."
            )

        return data

    def check_phase10_1(
        self,
    ) -> tuple[bool, dict[str, Any]]:
        self.log("Checking Phase 10.1 safety gate...")

        report = self.latest_json(
            self.phase10_1_dir
        )

        if report is None:
            return False, {
                "error": "No Phase 10.1 safety report was found.",
                "directory": str(self.phase10_1_dir),
            }

        try:
            data = self.load_json(report)
        except Exception as exc:
            return False, {
                "error": str(exc),
                "source_report": str(report),
            }

        gate = str(
            data.get("gate", "")
        ).upper()

        ai_status = str(
            data.get("ai_status", "UNKNOWN")
        ).upper()

        phase9_success = bool(
            data.get("phase9_success", False)
        )

        repair_allowed = bool(
            data.get("repair_allowed", False)
        )

        success = bool(
            data.get("success", False)
        )

        authorized = (
            success
            and gate == "PASSED"
            and phase9_success
            and repair_allowed
        )

        result = {
            "success": authorized,
            "gate": gate,
            "ai_status": ai_status,
            "phase9_success": phase9_success,
            "repair_allowed": repair_allowed,
            "source_report": str(report),
        }

        if authorized:
            self.log(
                "Phase 10.1 safety gate PASSED."
            )
        else:
            self.log(
                "Phase 10.1 safety gate BLOCKED."
            )

        return authorized, result

    def check_phase11(
        self,
    ) -> tuple[bool, dict[str, Any]]:
        self.log("Checking Phase 11 repair plan...")

        report = self.latest_json(
            self.phase11_dir
        )

        if report is None:
            return False, {
                "error": "No Phase 11 repair plan was found.",
                "directory": str(self.phase11_dir),
            }

        try:
            data = self.load_json(report)
        except Exception as exc:
            return False, {
                "error": str(exc),
                "source_report": str(report),
            }

        repair_required = bool(
            data.get(
                "repair_required",
                data.get(
                    "repair_requested",
                    False,
                ),
            )
        )

        result = {
            "success": bool(
                data.get("success", False)
            ),
            "repair_required": repair_required,
            "repair_executed": bool(
                data.get("repair_executed", False)
            ),
            "source_modified": bool(
                data.get("source_modified", False)
            ),
            "source_report": str(report),
        }

        if repair_required:
            self.log(
                "Phase 11 contains a repair request."
            )
        else:
            self.log(
                "Phase 11 reports that no repair is required."
            )

        return True, result

    def write_audit(
        self,
        result: dict[str, Any],
    ) -> Path:
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output = (
            self.output_dir
            / f"guarded_execution_{timestamp}.json"
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
            "Starting Phase 12.1 guarded execution..."
        )

        safety_ok, safety = (
            self.check_phase10_1()
        )

        if not safety_ok:
            result = {
                "phase": "12.1",
                "success": False,
                "stage": "phase10.1_safety",
                "gate": "BLOCKED",
                "error": (
                    "Phase 10.1 safety gate "
                    "did not authorize execution."
                ),
                "phase10_1": safety,
                "source_report": None,
                "source_modified": False,
                "repair_executed": False,
                "rollback_performed": False,
            }

            audit = self.write_audit(result)

            self.log(
                f"Execution blocked. Audit: {audit}"
            )

            return result

        phase11_found, phase11 = (
            self.check_phase11()
        )

        if not phase11_found:
            result = {
                "phase": "12.1",
                "success": False,
                "stage": "phase11_plan",
                "gate": "BLOCKED",
                "error": (
                    "Phase 11 repair plan "
                    "could not be located."
                ),
                "phase10_1": safety,
                "phase11": phase11,
                "source_report": None,
                "source_modified": False,
                "repair_executed": False,
                "rollback_performed": False,
            }

            audit = self.write_audit(result)

            self.log(
                f"Execution blocked. Audit: {audit}"
            )

            return result

        if not phase11.get(
            "repair_required",
            False,
        ):
            self.log(
                "Phase 11 reports that no repair is required."
            )

            self.log(
                "No source files will be modified."
            )

            result = {
                "phase": "12.1",
                "success": True,
                "stage": "no_repair_required",
                "gate": "PASSED",
                "phase10_1": safety,
                "phase11": phase11,
                "source_report": phase11.get(
                    "source_report"
                ),
                "source_modified": False,
                "repair_executed": False,
                "rollback_performed": False,
            }

            audit = self.write_audit(result)

            self.log(
                f"Phase 12.1 completed safely. Audit: {audit}"
            )

            return result

        self.log(
            "Phase 11 requested a repair."
        )

        self.log(
            "Guarded execution prevents source modification."
        )

        result = {
            "phase": "12.1",
            "success": False,
            "stage": "execution_guard",
            "gate": "BLOCKED",
            "error": (
                "Repair requested, but Phase 12.1 "
                "guarded mode does not modify source code."
            ),
            "phase10_1": safety,
            "phase11": phase11,
            "source_report": phase11.get(
                "source_report"
            ),
            "source_modified": False,
            "repair_executed": False,
            "rollback_performed": False,
        }

        audit = self.write_audit(result)

        self.log(
            f"Execution blocked by guard. Audit: {audit}"
        )

        return result


def main() -> None:
    executor = Phase121GuardedExecution()
    result = executor.run()

    print("")
    print("=" * 60)
    print("FINAL PHASE 12.1 RESULT")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

