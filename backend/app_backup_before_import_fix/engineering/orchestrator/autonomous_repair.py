from __future__ import annotations

import asyncio
from typing import Any

from app.engineering.validator.project_validator import (
    ProjectValidator,
)
from app.engineering.repair.error_analyzer import (
    ErrorAnalyzer,
)
from app.engineering.repair.repair_agent import (
    RepairAgent,
)


class AutonomousRepairLoop:
    """
    Phase 4 — Step 6

    Coordinates:

        Validator
            ↓
        Error Analyzer
            ↓
        Repair Agent
            ↓
        Validator again

    The loop stops when:
        1. Validation passes
        2. No repairable errors remain
        3. Maximum repair attempts are reached
    """

    def __init__(
        self,
        max_attempts: int = 3,
        project_root: str = "generated_code",
    ):

        self.max_attempts = max_attempts

        self.project_root = project_root

        self.validator = ProjectValidator(
            project_root=project_root
        )

        self.analyzer = ErrorAnalyzer()

        self.repair_agent = RepairAgent(
            project_root=project_root
        )

    # ---------------------------------------------------------
    # Run validation
    # ---------------------------------------------------------

    async def validate_project(
        self,
    ) -> dict[str, Any]:

        return await self.validator.validate()

    # ---------------------------------------------------------
    # Run one repair cycle
    # ---------------------------------------------------------

    def repair_project(
        self,
        validation_result: dict[str, Any],
    ) -> dict[str, Any]:

        analysis = self.analyzer.analyze(
            validation_result
        )

        print()
        print("=" * 60)
        print("🧠 ERROR ANALYSIS")
        print("=" * 60)

        print(
            f"Errors found: "
            f"{analysis.get('error_count', 0)}"
        )

        print(
            f"Repairable: "
            f"{analysis.get('repair_count', 0)}"
        )

        print(
            f"Manual review: "
            f"{analysis.get('manual_review_count', 0)}"
        )

        # -----------------------------------------------------
        # Nothing repairable
        # -----------------------------------------------------

        if analysis.get(
            "repair_count",
            0,
        ) == 0:

            print(
                "⚠️ No automatic repairs available."
            )

            return {
                "success": False,
                "stage": "analysis",
                "analysis": analysis,
                "repair": None,
            }

        # -----------------------------------------------------
        # Apply repair
        # -----------------------------------------------------

        repair_result = (
            self.repair_agent.repair(
                analysis
            )
        )

        return {
            "success": repair_result.get(
                "success",
                False,
            ),
            "stage": "repair",
            "analysis": analysis,
            "repair": repair_result,
        }

    # ---------------------------------------------------------
    # Main autonomous loop
    # ---------------------------------------------------------

    async def run(self) -> dict[str, Any]:

        print("=" * 60)
        print("🤖 PHASE 4 — AUTONOMOUS REPAIR LOOP")
        print("=" * 60)

        history = []

        # -----------------------------------------------------
        # Initial validation
        # -----------------------------------------------------

        print()
        print("🔎 Initial project validation...")

        validation = await self.validate_project()

        history.append(
            {
                "attempt": 0,
                "validation": validation,
            }
        )

        # -----------------------------------------------------
        # Already healthy
        # -----------------------------------------------------

        if validation.get(
            "success"
        ):

            print()
            print(
                "🎉 PROJECT IS ALREADY HEALTHY"
            )

            return {
                "success": True,
                "stage": "validation",
                "attempts": 0,
                "history": history,
                "message": (
                    "Project passed validation "
                    "without requiring repairs."
                ),
            }

        # -----------------------------------------------------
        # Repair attempts
        # -----------------------------------------------------

        for attempt in range(
            1,
            self.max_attempts + 1,
        ):

            print()
            print("=" * 60)
            print(
                f"🔧 REPAIR ATTEMPT "
                f"{attempt}/{self.max_attempts}"
            )
            print("=" * 60)

            # -------------------------------------------------
            # Analyze + repair
            # -------------------------------------------------

            repair_cycle = (
                self.repair_project(
                    validation
                )
            )

            history.append(
                {
                    "attempt": attempt,
                    "repair": repair_cycle,
                }
            )

            # -------------------------------------------------
            # Repair failed
            # -------------------------------------------------

            if not repair_cycle.get(
                "success"
            ):

                print()
                print(
                    "❌ Automatic repair failed."
                )

                return {
                    "success": False,
                    "stage": "repair",
                    "attempts": attempt,
                    "history": history,
                    "message": (
                        "Automatic repair could "
                        "not resolve the project."
                    ),
                }

            # -------------------------------------------------
            # Validate repaired project
            # -------------------------------------------------

            print()
            print(
                "🔎 Validating repaired project..."
            )

            validation = (
                await self.validate_project()
            )

            history.append(
                {
                    "attempt": attempt,
                    "validation": validation,
                }
            )

            # -------------------------------------------------
            # Repair successful
            # -------------------------------------------------

            if validation.get(
                "success"
            ):

                print()
                print("=" * 60)
                print(
                    "🎉 AUTONOMOUS REPAIR "
                    "SUCCESSFUL"
                )
                print("=" * 60)

                return {
                    "success": True,
                    "stage": "validation",
                    "attempts": attempt,
                    "history": history,
                    "message": (
                        "Project was automatically "
                        "repaired and validated."
                    ),
                }

            # -------------------------------------------------
            # Still broken
            # -------------------------------------------------

            remaining = validation.get(
                "error_count",
                0,
            )

            print()
            print(
                f"⚠️ Project still has "
                f"{remaining} error(s)."
            )

        # -----------------------------------------------------
        # Maximum attempts reached
        # -----------------------------------------------------

        print()
        print("=" * 60)
        print(
            "🛑 MAXIMUM REPAIR ATTEMPTS REACHED"
        )
        print("=" * 60)

        return {
            "success": False,
            "stage": "max_attempts",
            "attempts": self.max_attempts,
            "history": history,
            "message": (
                "Project could not be automatically "
                "repaired within the allowed attempts."
            ),
        }


# -------------------------------------------------------------
# Manual execution
# -------------------------------------------------------------

async def main():

    loop = AutonomousRepairLoop(
        max_attempts=3,
        project_root="generated_code",
    )

    result = await loop.run()

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":

    asyncio.run(main())