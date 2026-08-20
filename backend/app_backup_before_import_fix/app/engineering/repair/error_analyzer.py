from __future__ import annotations

from typing import Any


class ErrorAnalyzer:
    """
    Phase 4 â€” Step 3

    Converts Project Validator errors into
    structured repair instructions.

    This class analyzes errors only.
    It does NOT modify project files.
    """

    def __init__(self):
        self.repairable_types = {
            "missing_dependency",
            "missing_file",
            "missing_import",
            "syntax_error",
            "read_error",
            "missing_main",
            "missing_fastapi_app",
            "fastapi_check_error",
            "requirements_error",
        }

    # ---------------------------------------------------------
    # Analyze one error
    # ---------------------------------------------------------

    def analyze_error(
        self,
        error: dict[str, Any],
    ) -> dict[str, Any]:

        error_type = error.get(
            "type",
            "unknown",
        )

        file_path = error.get(
            "file",
            "",
        )

        module = error.get(
            "module",
            "",
        )

        message = error.get(
            "message",
            "Unknown error",
        )

        # -----------------------------------------------------
        # Missing dependency
        # -----------------------------------------------------

        if error_type == "missing_dependency":

            return {
                "repairable": True,
                "category": "dependency",
                "action": "update_requirements",
                "file": (
                    "requirements.txt"
                ),
                "module": module,
                "description": (
                    f"Add '{module}' "
                    "to requirements.txt."
                ),
            }

        # -----------------------------------------------------
        # Missing import
        # -----------------------------------------------------

        if error_type == "missing_import":

            return {
                "repairable": True,
                "category": "dependency",
                "action": "install_dependency",
                "file": file_path,
                "module": module,
                "description": (
                    f"Resolve missing "
                    f"Python module '{module}'."
                ),
            }

        # -----------------------------------------------------
        # Missing file
        # -----------------------------------------------------

        if error_type == "missing_file":

            return {
                "repairable": True,
                "category": "file",
                "action": "create_file",
                "file": file_path,
                "description": (
                    f"Create missing "
                    f"required file '{file_path}'."
                ),
            }

        # -----------------------------------------------------
        # Syntax error
        # -----------------------------------------------------

        if error_type == "syntax_error":

            return {
                "repairable": True,
                "category": "code",
                "action": "repair_syntax",
                "file": file_path,
                "line": error.get(
                    "line"
                ),
                "column": error.get(
                    "column"
                ),
                "description": (
                    "Repair the Python syntax "
                    "error in the generated file."
                ),
                "error": message,
            }

        # -----------------------------------------------------
        # Missing main.py
        # -----------------------------------------------------

        if error_type == "missing_main":

            return {
                "repairable": True,
                "category": "fastapi",
                "action": "create_main",
                "file": "app/main.py",
                "description": (
                    "Create the FastAPI "
                    "application entry point."
                ),
            }

        # -----------------------------------------------------
        # Missing FastAPI app
        # -----------------------------------------------------

        if error_type == "missing_fastapi_app":

            return {
                "repairable": True,
                "category": "fastapi",
                "action": "repair_fastapi_app",
                "file": file_path,
                "description": (
                    "Create or repair the "
                    "FastAPI 'app' instance."
                ),
            }

        # -----------------------------------------------------
        # Generic repairable error
        # -----------------------------------------------------

        if error_type in self.repairable_types:

            return {
                "repairable": True,
                "category": "general",
                "action": "inspect_and_repair",
                "file": file_path,
                "description": message,
            }

        # -----------------------------------------------------
        # Unknown error
        # -----------------------------------------------------

        return {
            "repairable": False,
            "category": "unknown",
            "action": "manual_review",
            "file": file_path,
            "description": message,
        }

    # ---------------------------------------------------------
    # Analyze complete validator result
    # ---------------------------------------------------------

    def analyze(
        self,
        validation_result: dict[str, Any],
    ) -> dict[str, Any]:

        errors = validation_result.get(
            "errors",
            [],
        )

        repair_plan = []

        for error in errors:

            if not isinstance(
                error,
                dict,
            ):
                continue

            plan = self.analyze_error(
                error
            )

            repair_plan.append(plan)

        repairable = [
            item
            for item in repair_plan
            if item.get("repairable")
        ]

        manual_review = [
            item
            for item in repair_plan
            if not item.get("repairable")
        ]

        return {
            "success": True,
            "error_count": len(errors),
            "repair_count": len(repairable),
            "manual_review_count": len(
                manual_review
            ),
            "repair_plan": repair_plan,
        }


# -------------------------------------------------------------
# Manual test
# -------------------------------------------------------------

if __name__ == "__main__":

    analyzer = ErrorAnalyzer()

    test_result = {
        "success": False,
        "stage": "validation",
        "errors": [
            {
                "type": "missing_dependency",
                "module": "fastapi",
                "message": (
                    "FastAPI is imported "
                    "but not listed in "
                    "requirements.txt."
                ),
            },
            {
                "type": "missing_dependency",
                "module": "uvicorn",
                "message": (
                    "Uvicorn is required "
                    "to run FastAPI."
                ),
            },
        ],
    }

    result = analyzer.analyze(
        test_result
    )

    print("=" * 60)
    print("ðŸ” ERROR ANALYZER TEST")
    print("=" * 60)

    print(result)
