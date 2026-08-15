from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any


class RepairAgent:
    """
    Phase 4 — Step 4

    Applies safe, deterministic repairs to the generated project.

    Current supported repairs:
        - Add missing Python dependencies
        - Create missing directories/files when explicitly requested

    The RepairAgent does NOT blindly rewrite source code.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
    ):
        self.project_root = Path(project_root)

    # ---------------------------------------------------------
    # Locate generated backend
    # ---------------------------------------------------------

    def find_backend(self) -> Path | None:

        possible_paths = [
            self.project_root / "backend",
            self.project_root,
        ]

        for path in possible_paths:

            if (
                path / "app" / "main.py"
            ).exists():

                return path.resolve()

        return None

    # ---------------------------------------------------------
    # Add dependency
    # ---------------------------------------------------------

    def add_dependency(
        self,
        backend: Path,
        package: str,
    ) -> dict[str, Any]:

        requirements = (
            backend
            / "requirements.txt"
        )

        if not requirements.exists():

            requirements.write_text(
                "",
                encoding="utf-8",
            )

        content = requirements.read_text(
            encoding="utf-8",
            errors="replace",
        )

        lines = content.splitlines()

        # Normalize package name for comparison.
        package_key = (
            package
            .strip()
            .lower()
            .replace("_", "-")
        )

        # Check existing dependencies.
        for line in lines:

            clean = line.strip()

            if not clean:
                continue

            if clean.startswith("#"):
                continue

            # Remove version operators.
            existing_name = (
                clean
                .split("==")[0]
                .split(">=")[0]
                .split("<=")[0]
                .split(">")[0]
                .split("<")[0]
                .split("~=")[0]
                .strip()
                .lower()
                .replace("_", "-")
            )

            if existing_name == package_key:

                return {
                    "success": True,
                    "changed": False,
                    "package": package,
                    "file": str(
                        requirements
                    ),
                    "message": (
                        f"{package} already "
                        "exists in requirements.txt."
                    ),
                }

        # Add package.
        if content and not content.endswith(
            "\n"
        ):
            content += "\n"

        content += package + "\n"

        requirements.write_text(
            content,
            encoding="utf-8",
        )

        return {
            "success": True,
            "changed": True,
            "package": package,
            "file": str(
                requirements
            ),
            "message": (
                f"Added {package} "
                "to requirements.txt."
            ),
        }

    # ---------------------------------------------------------
    # Create missing file
    # ---------------------------------------------------------

    def create_file(
        self,
        backend: Path,
        relative_path: str,
    ) -> dict[str, Any]:

        file_path = (
            backend
            / relative_path
        )

        if file_path.exists():

            return {
                "success": True,
                "changed": False,
                "file": str(file_path),
                "message": (
                    "File already exists."
                ),
            }

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path.write_text(
            "",
            encoding="utf-8",
        )

        return {
            "success": True,
            "changed": True,
            "file": str(file_path),
            "message": (
                "Created missing file."
            ),
        }

    # ---------------------------------------------------------
    # Apply one repair
    # ---------------------------------------------------------

    def apply_repair(
        self,
        backend: Path,
        repair: dict[str, Any],
    ) -> dict[str, Any]:

        action = repair.get(
            "action"
        )

        # -----------------------------------------------------
        # Dependency repair
        # -----------------------------------------------------

        if action == "update_requirements":

            package = repair.get(
                "module"
            )

            if not package:

                return {
                    "success": False,
                    "changed": False,
                    "error": (
                        "No dependency/module "
                        "was provided."
                    ),
                }

            return self.add_dependency(
                backend,
                package,
            )

        # -----------------------------------------------------
        # Missing file
        # -----------------------------------------------------

        if action == "create_file":

            relative_path = repair.get(
                "file"
            )

            if not relative_path:

                return {
                    "success": False,
                    "changed": False,
                    "error": (
                        "No file path "
                        "was provided."
                    ),
                }

            return self.create_file(
                backend,
                relative_path,
            )

        # -----------------------------------------------------
        # Unsupported repair
        # -----------------------------------------------------

        return {
            "success": False,
            "changed": False,
            "unsupported": True,
            "action": action,
            "error": (
                f"Repair action "
                f"'{action}' is not "
                "supported yet."
            ),
        }

    # ---------------------------------------------------------
    # Apply complete repair plan
    # ---------------------------------------------------------

    def repair(
        self,
        analysis_result: dict[str, Any],
    ) -> dict[str, Any]:

        print("=" * 60)
        print("🔧 PHASE 4 — REPAIR AGENT")
        print("=" * 60)

        backend = self.find_backend()

        if backend is None:

            print(
                "❌ Generated backend not found."
            )

            return {
                "success": False,
                "stage": "repair",
                "error": (
                    "Could not find "
                    "generated_code/backend."
                ),
                "repairs": [],
            }

        print(
            f"📁 Backend: {backend}"
        )

        repair_plan = (
            analysis_result.get(
                "repair_plan",
                [],
            )
        )

        if not repair_plan:

            print(
                "ℹ️ No repairs required."
            )

            return {
                "success": True,
                "stage": "repair",
                "changed": False,
                "repairs": [],
            }

        results = []

        changed = False

        for index, repair in enumerate(
            repair_plan,
            start=1,
        ):

            print()
            print(
                f"🔧 Repair "
                f"{index}/{len(repair_plan)}"
            )

            print(
                f"Action: "
                f"{repair.get('action')}"
            )

            print(
                f"File: "
                f"{repair.get('file', '')}"
            )

            result = self.apply_repair(
                backend,
                repair,
            )

            results.append(result)

            if result.get("changed"):
                changed = True

            if result.get("success"):

                print(
                    f"✅ "
                    f"{result.get('message')}"
                )

            else:

                print(
                    f"❌ "
                    f"{result.get('error')}"
                )

        successful = [
            result
            for result in results
            if result.get("success")
        ]

        failed = [
            result
            for result in results
            if not result.get("success")
        ]

        success = len(failed) == 0

        print()
        print("=" * 60)

        if success:

            print(
                "✅ REPAIR COMPLETED"
            )

        else:

            print(
                f"❌ REPAIR FAILED "
                f"({len(failed)} errors)"
            )

        print("=" * 60)

        return {
            "success": success,
            "stage": "repair",
            "changed": changed,
            "repair_count": len(results),
            "successful_repairs": len(
                successful
            ),
            "failed_repairs": len(
                failed
            ),
            "repairs": results,
        }


# -------------------------------------------------------------
# Manual test
# -------------------------------------------------------------

def main():

    agent = RepairAgent()

    test_analysis = {
        "success": True,
        "error_count": 2,
        "repair_count": 2,
        "manual_review_count": 0,
        "repair_plan": [
            {
                "repairable": True,
                "category": "dependency",
                "action": "update_requirements",
                "file": "requirements.txt",
                "module": "fastapi",
                "description": (
                    "Add 'fastapi' "
                    "to requirements.txt."
                ),
            },
            {
                "repairable": True,
                "category": "dependency",
                "action": "update_requirements",
                "file": "requirements.txt",
                "module": "uvicorn",
                "description": (
                    "Add 'uvicorn' "
                    "to requirements.txt."
                ),
            },
        ],
    }

    result = agent.repair(
        test_analysis
    )

    print()
    print("RESULT:")
    print(result)


if __name__ == "__main__":
    main()