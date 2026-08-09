from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import httpx


class RuntimeErrorAnalyzer:
    """
    PHASE 5 — Runtime Error Analyzer

    Takes HTTP failures discovered by the HTTP tester,
    captures useful runtime information, and creates
    structured repair plans.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8766,
        project_dir: str = "generated_code/backend",
        timeout: float = 5.0,
    ):
        self.base_url = f"http://{host}:{port}"
        self.project_dir = Path(project_dir)
        self.timeout = timeout

    # ---------------------------------------------------------
    # Capture endpoint response
    # ---------------------------------------------------------

    async def capture_error(
        self,
        result: dict[str, Any],
    ) -> dict[str, Any]:

        method = result.get("method", "GET")
        path = result.get("path", "/")

        url = f"{self.base_url}{path}"

        payload = result.get("payload")

        try:

            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                if method == "GET":

                    response = await client.get(url)

                elif method == "POST":

                    response = await client.post(
                        url,
                        json=payload or {},
                    )

                elif method == "PUT":

                    response = await client.put(
                        url,
                        json=payload or {},
                    )

                elif method == "PATCH":

                    response = await client.patch(
                        url,
                        json=payload or {},
                    )

                else:

                    return {
                        "success": False,
                        "path": path,
                        "method": method,
                        "error": (
                            f"Unsupported method: {method}"
                        ),
                    }

                body = response.text

                return {
                    "success": True,
                    "path": path,
                    "method": method,
                    "status_code": response.status_code,
                    "response": body,
                    "headers": dict(response.headers),
                }

        except Exception as e:

            return {
                "success": False,
                "path": path,
                "method": method,
                "error": str(e),
            }

    # ---------------------------------------------------------
    # Read possible runtime logs
    # ---------------------------------------------------------

    def find_log_files(self) -> list[Path]:

        possible_files = [
            self.project_dir / "runtime.log",
            self.project_dir / "server.log",
            self.project_dir / "error.log",
            self.project_dir / "uvicorn.log",
        ]

        return [
            path
            for path in possible_files
            if path.exists()
        ]

    def read_logs(self) -> str:

        logs = []

        for path in self.find_log_files():

            try:

                content = path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )

                logs.append(
                    f"\n===== {path.name} =====\n"
                    f"{content}"
                )

            except Exception:
                pass

        return "\n".join(logs)

    # ---------------------------------------------------------
    # Detect common Python runtime errors
    # ---------------------------------------------------------

    def diagnose(
        self,
        response_text: str,
        logs: str = "",
    ) -> dict[str, Any]:

        combined = (
            f"{response_text}\n{logs}"
        )

        combined_lower = combined.lower()

        # -----------------------------------------------------
        # NameError
        # -----------------------------------------------------

        match = re.search(
            r"name ['\"]([^'\"]+)['\"] is not defined",
            combined,
            re.IGNORECASE,
        )

        if match:

            name = match.group(1)

            return {
                "category": "runtime_name_error",
                "error_type": "NameError",
                "symbol": name,
                "description": (
                    f"Python name '{name}' "
                    "is used but is not defined."
                ),
                "repairable": True,
                "action": "fix_missing_name",
            }

        # -----------------------------------------------------
        # ImportError
        # -----------------------------------------------------

        match = re.search(
            r"No module named ['\"]([^'\"]+)['\"]",
            combined,
            re.IGNORECASE,
        )

        if match:

            module = match.group(1)

            return {
                "category": "missing_import",
                "error_type": "ModuleNotFoundError",
                "module": module,
                "description": (
                    f"Python module '{module}' "
                    "is missing."
                ),
                "repairable": True,
                "action": "add_dependency",
            }

        # -----------------------------------------------------
        # AttributeError
        # -----------------------------------------------------

        match = re.search(
            r"AttributeError:\s*(.*)",
            combined,
            re.IGNORECASE,
        )

        if match:

            message = match.group(1).strip()

            return {
                "category": "attribute_error",
                "error_type": "AttributeError",
                "description": message,
                "repairable": True,
                "action": "fix_attribute",
            }

        # -----------------------------------------------------
        # TypeError
        # -----------------------------------------------------

        match = re.search(
            r"TypeError:\s*(.*)",
            combined,
            re.IGNORECASE,
        )

        if match:

            message = match.group(1).strip()

            return {
                "category": "type_error",
                "error_type": "TypeError",
                "description": message,
                "repairable": True,
                "action": "fix_type_error",
            }

        # -----------------------------------------------------
        # SyntaxError
        # -----------------------------------------------------

        match = re.search(
            r"SyntaxError:\s*(.*)",
            combined,
            re.IGNORECASE,
        )

        if match:

            message = match.group(1).strip()

            return {
                "category": "syntax_error",
                "error_type": "SyntaxError",
                "description": message,
                "repairable": True,
                "action": "fix_syntax",
            }

        # -----------------------------------------------------
        # HTTP 500 without traceback
        # -----------------------------------------------------

        if (
            "500" in combined
            or "internal server error"
            in combined_lower
        ):

            return {
                "category": "http_500",
                "error_type": "InternalServerError",
                "description": (
                    "The FastAPI endpoint returned "
                    "HTTP 500. Server traceback is "
                    "required for exact diagnosis."
                ),
                "repairable": False,
                "action": "manual_traceback_required",
            }

        # -----------------------------------------------------
        # Unknown
        # -----------------------------------------------------

        return {
            "category": "unknown",
            "error_type": "Unknown",
            "description": (
                "Runtime failure could not "
                "be diagnosed automatically."
            ),
            "repairable": False,
            "action": "manual_review",
        }

    # ---------------------------------------------------------
    # Analyze QA results
    # ---------------------------------------------------------

    async def analyze(
        self,
        qa_results: dict[str, Any],
    ) -> dict[str, Any]:

        print()
        print("=" * 60)
        print(
            "🔍 PHASE 5 — RUNTIME ERROR ANALYZER"
        )
        print("=" * 60)

        failures = [
            result
            for result in qa_results.get(
                "results",
                [],
            )
            if not result.get("passed", False)
        ]

        print(
            f"❌ Runtime failures: "
            f"{len(failures)}"
        )

        if not failures:

            print(
                "✅ No runtime failures found."
            )

            return {
                "success": True,
                "stage": "runtime_analysis",
                "error_count": 0,
                "repair_count": 0,
                "manual_review_count": 0,
                "repair_plan": [],
            }

        logs = self.read_logs()

        analyses = []
        repair_plan = []
        manual_review = []

        for failure in failures:

            print(
                f"\n🔎 Analyzing "
                f"{failure.get('method')} "
                f"{failure.get('path')}"
            )

            captured = await self.capture_error(
                failure
            )

            response_text = captured.get(
                "response",
                "",
            )

            diagnosis = self.diagnose(
                response_text,
                logs,
            )

            analysis = {
                "endpoint": failure.get(
                    "path"
                ),
                "method": failure.get(
                    "method"
                ),
                "status_code": failure.get(
                    "status_code"
                ),
                "captured": captured,
                "diagnosis": diagnosis,
            }

            analyses.append(analysis)

            print(
                f"   Category: "
                f"{diagnosis['category']}"
            )

            print(
                f"   Action: "
                f"{diagnosis['action']}"
            )

            if diagnosis.get(
                "repairable",
                False,
            ):

                repair = {
                    "repairable": True,
                    "category": diagnosis[
                        "category"
                    ],
                    "action": diagnosis[
                        "action"
                    ],
                    "endpoint": failure.get(
                        "path"
                    ),
                    "method": failure.get(
                        "method"
                    ),
                    "description": diagnosis[
                        "description"
                    ],
                }

                if diagnosis.get(
                    "symbol"
                ):
                    repair["symbol"] = (
                        diagnosis["symbol"]
                    )

                if diagnosis.get(
                    "module"
                ):
                    repair["module"] = (
                        diagnosis["module"]
                    )

                repair_plan.append(
                    repair
                )

            else:

                manual_review.append(
                    analysis
                )

        print()
        print("=" * 60)

        print(
            f"🔧 Repairable: "
            f"{len(repair_plan)}"
        )

        print(
            f"👤 Manual review: "
            f"{len(manual_review)}"
        )

        print("=" * 60)

        return {
            "success": True,
            "stage": "runtime_analysis",
            "error_count": len(
                failures
            ),
            "repair_count": len(
                repair_plan
            ),
            "manual_review_count": len(
                manual_review
            ),
            "analyses": analyses,
            "repair_plan": repair_plan,
            "manual_review": manual_review,
            "logs_available": bool(logs),
        }


# -------------------------------------------------------------
# Manual test
# -------------------------------------------------------------

async def main():

    print(
        "⚠️ FastAPI must be running on "
        "127.0.0.1:8766."
    )

    analyzer = RuntimeErrorAnalyzer()

    # Example QA result.
    # In the real orchestrator this will come
    # directly from http_tester.py.

    qa_results = {
        "success": False,
        "stage": "http_testing",
        "endpoint_count": 2,
        "passed": 0,
        "failed": 2,
        "results": [
            {
                "path": "/analyze",
                "method": "POST",
                "status_code": 500,
                "passed": False,
                "payload": {},
                "error": "HTTP 500",
            },
            {
                "path": "/predict",
                "method": "POST",
                "status_code": 500,
                "passed": False,
                "payload": {},
                "error": "HTTP 500",
            },
        ],
    }

    result = await analyzer.analyze(
        qa_results
    )

    print()
    print("=" * 60)
    print("RESULT:")
    print(result)
    print("=" * 60)


if __name__ == "__main__":

    import asyncio

    asyncio.run(main())