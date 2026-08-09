from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class Phase111RepairPlanValidator:
    """
    PHASE 11.1 — REPAIR PLAN VALIDATOR

    Validates an AI-generated Phase 11 repair plan before
    any source-code modification is allowed.

    This phase DOES NOT modify source code.
    """

    MAX_PATCHES = 10
    MIN_CONFIDENCE = 0.85

    PROTECTED_PARTS = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
    }

    ALLOWED_EXTENSIONS = {
        ".py",
        ".json",
        ".txt",
        ".md",
        ".yaml",
        ".yml",
        ".toml",
    }

    def __init__(
        self,
        project_root: str = "generated_code",
    ):
        self.project_root = Path(
            project_root
        ).resolve()

        self.backend_root = (
            self.project_root / "backend"
        )

        self.qa_root = (
            self.project_root.parent
            / "generated"
            / "_code.qa"
        )

        self.phase11_root = (
            self.qa_root / "phase11"
        )

        self.output_root = (
            self.phase11_root
            / "validation"
        )

        self.output_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        self.report_file = (
            self.output_root
            / f"validation_{timestamp}.json"
        )

    def log(self, message: str) -> None:
        try:
            print(message)
        except UnicodeEncodeError:
            print(
                str(message)
                .encode(
                    "ascii",
                    errors="replace",
                )
                .decode("ascii")
            )

    def load_plan(
        self,
        plan_path: str | Path,
    ) -> dict[str, Any]:

        path = Path(plan_path).resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"Repair plan not found: {path}"
            )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(data, dict):
            raise ValueError(
                "Repair plan must be a JSON object."
            )

        return data

    def validate_patch(
        self,
        patch: Any,
        index: int,
    ) -> dict[str, Any]:

        if not isinstance(
            patch,
            dict,
        ):
            return {
                "success": False,
                "index": index,
                "error": (
                    "Patch must be a JSON object."
                ),
            }

        file_name = patch.get("file")
        search = patch.get("search")
        replace = patch.get("replace")

        if not isinstance(
            file_name,
            str,
        ) or not file_name.strip():

            return {
                "success": False,
                "index": index,
                "error": (
                    "Patch file must be "
                    "a non-empty string."
                ),
            }

        if not isinstance(
            search,
            str,
        ):
            return {
                "success": False,
                "index": index,
                "error": (
                    "Patch search must be a string."
                ),
            }

        if not isinstance(
            replace,
            str,
        ):
            return {
                "success": False,
                "index": index,
                "error": (
                    "Patch replace must be a string."
                ),
            }

        target = (
            self.backend_root
            / file_name
        ).resolve()

        try:
            target.relative_to(
                self.backend_root
            )
        except ValueError:
            return {
                "success": False,
                "index": index,
                "error": (
                    "Patch attempts to escape "
                    "the backend directory."
                ),
            }

        relative_parts = target.relative_to(
            self.backend_root
        ).parts

        if any(
            part in self.PROTECTED_PARTS
            for part in relative_parts
        ):
            return {
                "success": False,
                "index": index,
                "error": (
                    "Patch targets a protected "
                    "directory."
                ),
            }

        if target.suffix.lower() not in (
            self.ALLOWED_EXTENSIONS
        ):
            return {
                "success": False,
                "index": index,
                "error": (
                    f"File extension is not "
                    f"allowed: {target.suffix}"
                ),
            }

        if not target.exists():
            return {
                "success": False,
                "index": index,
                "error": (
                    f"Target file does not exist: "
                    f"{file_name}"
                ),
            }

        if not target.is_file():
            return {
                "success": False,
                "index": index,
                "error": (
                    "Patch target is not a file."
                ),
            }

        content = target.read_text(
            encoding="utf-8",
            errors="replace",
        )

        occurrences = content.count(
            search
        )

        if occurrences != 1:
            return {
                "success": False,
                "index": index,
                "error": (
                    "Search text must occur "
                    f"exactly once; found "
                    f"{occurrences} occurrences."
                ),
            }

        if search == replace:
            return {
                "success": False,
                "index": index,
                "error": (
                    "Search and replacement "
                    "are identical."
                ),
            }

        return {
            "success": True,
            "index": index,
            "file": file_name,
            "target": str(target),
            "search_length": len(search),
            "replace_length": len(replace),
        }

    def validate(
        self,
        plan: dict[str, Any],
    ) -> dict[str, Any]:

        findings: list[str] = []
        warnings: list[str] = []
        validated: list[dict[str, Any]] = []

        repair_required = bool(
            plan.get(
                "repair_required",
                False,
            )
        )

        reason = str(
            plan.get(
                "reason",
                "",
            )
        )

        try:
            confidence = float(
                plan.get(
                    "confidence",
                    0,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            confidence = 0.0

        patches = plan.get(
            "patches",
            [],
        )

        if not repair_required:
            return {
                "success": True,
                "valid": True,
                "repair_required": False,
                "confidence": confidence,
                "reason": reason,
                "patch_count": 0,
                "validated_patches": [],
                "findings": [
                    "AI plan does not request a repair."
                ],
                "warnings": [],
            }

        if not isinstance(
            patches,
            list,
        ):
            findings.append(
                "Patches must be a list."
            )

            return {
                "success": True,
                "valid": False,
                "repair_required": True,
                "confidence": confidence,
                "findings": findings,
                "warnings": warnings,
            }

        if not patches:
            findings.append(
                "Repair was requested but "
                "no patches were supplied."
            )

        if len(patches) > self.MAX_PATCHES:
            findings.append(
                f"Patch count exceeds maximum "
                f"of {self.MAX_PATCHES}."
            )

        if confidence < self.MIN_CONFIDENCE:
            findings.append(
                f"AI confidence {confidence:.2f} "
                f"is below safe threshold "
                f"{self.MIN_CONFIDENCE:.2f}."
            )

        if len(reason.strip()) < 10:
            warnings.append(
                "Repair reason is unusually short."
            )

        if not findings:
            for index, patch in enumerate(
                patches,
                start=1,
            ):
                result = self.validate_patch(
                    patch,
                    index,
                )

                if result["success"]:
                    validated.append(
                        result
                    )
                else:
                    findings.append(
                        result["error"]
                    )

        valid = (
            len(findings) == 0
        )

        return {
            "success": True,
            "valid": valid,
            "repair_required": repair_required,
            "confidence": confidence,
            "reason": reason,
            "patch_count": len(patches),
            "validated_patches": validated,
            "findings": findings,
            "warnings": warnings,
        }

    def save_report(
        self,
        report: dict[str, Any],
    ) -> None:

        self.report_file.write_text(
            json.dumps(
                report,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

    def run(
        self,
        plan_path: str,
    ) -> dict[str, Any]:

        self.log("=" * 60)
        self.log(
            "PHASE 11.1 - REPAIR PLAN VALIDATOR"
        )
        self.log("=" * 60)

        try:
            plan = self.load_plan(
                plan_path
            )
        except Exception as exc:

            result = {
                "success": False,
                "stage": "plan_load_failed",
                "valid": False,
                "error": str(exc),
            }

            self.save_report(result)
            return result

        evaluation = self.validate(
            plan
        )

        result = {
            "success": evaluation["valid"],
            "stage": (
                "phase11.1_validation_completed"
            ),
            "timestamp": datetime.now().isoformat(),
            "plan": plan,
            "evaluation": evaluation,
            "modification_allowed": (
                evaluation["valid"]
                and evaluation[
                    "repair_required"
                ]
            ),
        }

        self.save_report(result)

        self.log(
            f"VALID: {evaluation['valid']}"
        )

        self.log(
            f"Repair required: "
            f"{evaluation['repair_required']}"
        )

        self.log(
            f"Confidence: "
            f"{evaluation.get('confidence', 0)}"
        )

        self.log(
            f"Validated patches: "
            f"{len(evaluation['validated_patches'])}"
        )

        self.log(
            f"Report: {self.report_file}"
        )

        return result


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Phase 11.1 Repair Plan Validator"
        )
    )

    parser.add_argument(
        "plan",
        help="Path to Phase 11 repair plan JSON",
    )

    args = parser.parse_args()

    result = (
        Phase111RepairPlanValidator()
        .run(args.plan)
    )

    print("")
    print("=" * 60)
    print("FINAL PHASE 11.1 RESULT")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()