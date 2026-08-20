from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class Phase101SafetyGate:
    """
    PHASE 10.1 — AI ENGINEERING SAFETY GATE

    Read-only safety validation for Phase 10.

    It:
        1. Finds the newest Phase 10 report.
        2. Validates the Phase 10 report.
        3. Parses the local AI response.
        4. Verifies Phase 9 evidence.
        5. Decides whether the safety gate passes.
        6. Writes a Phase 10.1 audit report.

    It NEVER modifies project source code.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
    ) -> None:
        self.project_root = Path(
            project_root
        ).resolve()

        # Project root:
        #
        # D:\AI Softwear Company\backend\generated_code
        #
        # Canonical QA root:
        #
        # D:\AI Softwear Company\backend\generated\_code.qa
        self.qa_root = (
            self.project_root.parent
            / "generated"
            / "_code.qa"
        )

        self.phase10_dir = (
            self.qa_root
            / "phase10"
            / "run"
        )

        self.output_dir = (
            self.qa_root
            / "phase10.1"
            / "hardening"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message: str) -> None:
        text = str(message)

        try:
            print(text)
        except UnicodeEncodeError:
            print(
                text.encode(
                    "ascii",
                    errors="replace",
                ).decode("ascii")
            )

    # ---------------------------------------------------------
    # Find Phase 10 report
    # ---------------------------------------------------------

    def get_latest_report(self) -> Path | None:
        """
        Find the newest Phase 10 JSON report.

        First searches the canonical run directory.

        If the expected run directory is missing,
        it recursively searches the phase10 directory.
        """

        if not self.phase10_dir.exists():
            return None

        reports = list(
            self.phase10_dir.rglob("*.json")
        )

        if not reports:
            return None

        reports = [
            path
            for path in reports
            if path.is_file()
        ]

        if not reports:
            return None

        return max(
            reports,
            key=lambda path: path.stat().st_mtime,
        )

    # ---------------------------------------------------------
    # Load report
    # ---------------------------------------------------------

    def load_report(
        self,
        report_path: Path,
    ) -> dict[str, Any]:
        try:
            content = report_path.read_text(
                encoding="utf-8",
                errors="replace",
            )

            data = json.loads(content)

            if not isinstance(data, dict):
                raise ValueError(
                    "Phase 10 JSON root must be an object."
                )

            return data

        except Exception as exc:
            raise RuntimeError(
                f"Unable to read Phase 10 report: {exc}"
            ) from exc

    # ---------------------------------------------------------
    # Extract AI fields
    # ---------------------------------------------------------

    def extract_ai_fields(
        self,
        report: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extract AI analysis from the current Phase 10 format.

        Also supports the older ai_repair_plan format.
        """

        analysis = report.get(
            "ai_analysis"
        )

        if not isinstance(analysis, dict):
            analysis = report.get(
                "ai_repair_plan"
            )

        if not isinstance(analysis, dict):
            analysis = {}

        response = str(
            analysis.get(
                "response",
                "",
            )
        )

        # STATUS
        status_match = re.search(
            r"STATUS\s*:\s*([A-Z_ ]+)",
            response,
            re.IGNORECASE,
        )

        ai_status = "UNKNOWN"

        if status_match:
            raw_status = (
                status_match.group(1)
                .strip()
                .upper()
            )

            if "HEALTHY" in raw_status:
                ai_status = "HEALTHY"

            elif (
                "REPAIR_REQUIRED"
                in raw_status
                or "REPAIR REQUIRED"
                in raw_status
            ):
                ai_status = "REPAIR_REQUIRED"

            elif "BLOCK" in raw_status:
                ai_status = "BLOCKED"

        # RISK
        risk_match = re.search(
            r"RISK\s*:\s*([A-Z_]+)",
            response,
            re.IGNORECASE,
        )

        risk = (
            risk_match.group(1)
            .strip()
            .upper()
            if risk_match
            else "UNKNOWN"
        )

        # REPAIR_ALLOWED
        repair_match = re.search(
            r"REPAIR_ALLOWED\s*:\s*([A-Z_]+)",
            response,
            re.IGNORECASE,
        )

        repair_allowed = False

        if repair_match:
            value = (
                repair_match.group(1)
                .strip()
                .upper()
            )

            repair_allowed = value in {
                "YES",
                "TRUE",
                "ALLOWED",
            }

        # Phase 10 success is the actual report success.
        phase10_success = bool(
            report.get(
                "success",
                False,
            )
        )

        # Phase 9 evidence.
        phase9 = report.get(
            "phase9",
            {},
        )

        if not isinstance(phase9, dict):
            phase9 = {}

        phase9_success = bool(
            phase9.get(
                "success",
                False,
            )
        )

        # Compatibility with older Phase 10.
        if not phase9:
            phase9 = report.get(
                "qa_validation_phase9",
                {},
            )

            if isinstance(
                phase9,
                dict,
            ):
                phase9_success = bool(
                    phase9.get(
                        "success",
                        False,
                    )
                )

        return {
            "status": ai_status,
            "risk": risk,
            "repair_allowed": repair_allowed,
            "phase10_success": phase10_success,
            "phase9_success": phase9_success,
            "response": response,
        }

    # ---------------------------------------------------------
    # Evaluate safety gate
    # ---------------------------------------------------------

    def evaluate(
        self,
        report: dict[str, Any],
    ) -> dict[str, Any]:
        ai = self.extract_ai_fields(
            report
        )

        ai_status = ai["status"]
        risk = ai["risk"]
        repair_allowed = ai[
            "repair_allowed"
        ]

        phase10_success = ai[
            "phase10_success"
        ]

        phase9_success = ai[
            "phase9_success"
        ]

        findings: list[str] = []
        warnings: list[str] = []

        gate = "BLOCKED"
        auto_modify = False

        # -----------------------------------------------------
        # Evidence validation
        # -----------------------------------------------------

        if not phase10_success:
            warnings.append(
                "Phase 10 did not report success."
            )

        if not phase9_success:
            warnings.append(
                "Phase 9 did not report successful QA."
            )

        if ai_status == "UNKNOWN":
            findings.append(
                "AI STATUS could not be reliably "
                "extracted from the Phase 10 response."
            )

        # -----------------------------------------------------
        # Healthy path
        # -----------------------------------------------------

        if (
            ai_status == "HEALTHY"
            and phase10_success
            and phase9_success
        ):
            gate = "PASSED"
            auto_modify = False

            findings.append(
                "Phase 10 AI analysis and Phase 9 "
                "QA evidence are consistent."
            )

        # -----------------------------------------------------
        # Repair path
        #
        # IMPORTANT:
        # Even when AI requests repair, this gate does not
        # modify source code. It only authorizes the next
        # controlled repair stage.
        # -----------------------------------------------------

        elif (
            ai_status == "REPAIR_REQUIRED"
            and repair_allowed
            and phase10_success
            and phase9_success
        ):
            gate = "PASSED"
            auto_modify = True

            findings.append(
                "AI requested a controlled repair and "
                "the required QA evidence is available."
            )

        # -----------------------------------------------------
        # Everything else is blocked
        # -----------------------------------------------------

        else:
            gate = "BLOCKED"
            auto_modify = False

            findings.append(
                "Safety constraint triggered or "
                "required evidence is incomplete."
            )

        return {
            "gate": gate,
            "ai_status": ai_status,
            "risk": risk,
            "repair_allowed": repair_allowed,
            "phase10_success": phase10_success,
            "phase9_success": phase9_success,
            "findings": findings,
            "warnings": warnings,
            "auto_modify": auto_modify,
        }

    # ---------------------------------------------------------
    # Write result
    # ---------------------------------------------------------

    def write_result(
        self,
        result: dict[str, Any],
    ) -> Path:
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output_file = (
            self.output_dir
            / f"hardening_{timestamp}.json"
        )

        output_file.write_text(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return output_file

    # ---------------------------------------------------------
    # Main gate
    # ---------------------------------------------------------

    def run(self) -> dict[str, Any]:
        self.log("=" * 60)
        self.log(
            "PHASE 10.1 - AI ENGINEERING SAFETY GATE"
        )
        self.log("=" * 60)

        report_path = (
            self.get_latest_report()
        )

        if report_path is None:
            result = {
                "success": False,
                "stage": "phase10_report",
                "gate": "BLOCKED",
                "error": (
                    "No Phase 10 JSON report was found."
                ),
                "searched_path": str(
                    self.phase10_dir
                ),
                "timestamp": datetime.now().isoformat(),
                "auto_modify": False,
            }

            output = self.write_result(
                result
            )

            self.log(
                f"Report: {output}"
            )

            self.log(
                json.dumps(
                    result,
                    indent=2,
                )
            )

            return result

        self.log(
            f"Evaluating Phase 10 report: "
            f"{report_path}"
        )

        try:
            report = self.load_report(
                report_path
            )

        except Exception as exc:
            result = {
                "success": False,
                "stage": "report_validation",
                "gate": "BLOCKED",
                "error": str(exc),
                "source_report": str(
                    report_path
                ),
                "timestamp": datetime.now().isoformat(),
                "auto_modify": False,
            }

            output = self.write_result(
                result
            )

            self.log(
                f"Report: {output}"
            )

            return result

        evaluation = self.evaluate(
            report
        )

        result = {
            "success": (
                evaluation["gate"]
                == "PASSED"
            ),
            "stage": "phase10.1_completed",
            "timestamp": datetime.now().isoformat(),
            "source_report": str(
                report_path
            ),
            **evaluation,
        }

        output = self.write_result(
            result
        )

        self.log(
            f"Gate: {result['gate']}"
        )

        self.log(
            f"AI status: "
            f"{result['ai_status']}"
        )

        self.log(
            f"Phase 10 success: "
            f"{result['phase10_success']}"
        )

        self.log(
            f"Phase 9 success: "
            f"{result['phase9_success']}"
        )

        self.log(
            f"Repair allowed by AI: "
            f"{result['repair_allowed']}"
        )

        self.log(
            f"Report archived safely at: "
            f"{output}"
        )

        self.log("=" * 60)
        self.log(
            "FINAL PHASE 10.1 RESULT"
        )
        self.log("=" * 60)

        self.log(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

        return result


def main() -> None:
    gate = Phase101SafetyGate()
    gate.run()


if __name__ == "__main__":
    main()