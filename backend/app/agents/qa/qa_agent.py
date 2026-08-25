import json
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class QAAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "QA Agent",
            "QA Engineer",
            agent_key="qa",
        )

        self.generated_backend = (
            Path(__file__).resolve().parents[3]
            / "generated_code"
            / "backend"
        )

        self.live_base_url = "http://127.0.0.1:8010"

    async def run(self, task: str):
        return await self.test_project(task)

    async def test_project(self, task: str):

        print("QA Agent Started")

        deterministic = self.run_deterministic_checks()

        llm_report = await self.generate_qa_review(
            task,
            deterministic,
        )

        final_report = self.build_final_report(
            deterministic,
            llm_report,
        )

        self.remember(
            "qa",
            final_report,
        )

        memory.save(
            "qa",
            final_report,
        )

        workspace.save(
            "qa/test_plan.md",
            final_report,
        )

        workspace.save(
            "qa/live_validation.json",
            json.dumps(
                deterministic,
                indent=2,
                default=str,
            ),
        )

        print("QA live validation saved")

        # -------------------------------------------------
        # HARD RELEASE GATE
        # -------------------------------------------------
        # Deterministic QA is authoritative.
        # A failed deterministic validation must fail the
        # QA agent so downstream Security/DevOps agents
        # cannot qualify the release.

        if deterministic.get("overall") != "PASS":

            failed_modules = [
                item.get("module", "unknown")
                for item in deterministic.get(
                    "module_imports",
                    [],
                )
                if item.get("status") != "PASS"
            ]

            failed_http = [
                item.get("endpoint", "unknown")
                for item in deterministic.get(
                    "http_checks",
                    [],
                )
                if item.get("status") == "FAIL"
            ]

            details = []

            if failed_modules:
                details.append(
                    "Failed modules: "
                    + ", ".join(failed_modules)
                )

            if failed_http:
                details.append(
                    "Failed HTTP checks: "
                    + ", ".join(failed_http)
                )

            if not details:
                details.append(
                    "Deterministic QA validation failed."
                )

            raise RuntimeError(
                "QA release gate FAILED. "
                + " | ".join(details)
            )

        return final_report

    def run_deterministic_checks(self):

        report = {
            "generated_backend_exists": False,
            "python_compile": False,
            "module_imports": [],
            "fastapi_import": False,
            "openapi_available": False,
            "openapi_paths": [],
            "http_checks": [],
            "overall": "FAIL",
        }

        backend = self.generated_backend

        print("=" * 60)
        print("QA: DETERMINISTIC BACKEND VALIDATION")
        print("=" * 60)

        # -------------------------------------------------
        # Generated backend existence
        # -------------------------------------------------

        if not backend.exists():
            print("FAIL: generated backend directory missing")
            return report

        main_file = backend / "app" / "main.py"

        if not main_file.exists():
            print("FAIL: generated app/main.py missing")
            return report

        report["generated_backend_exists"] = True
        print("PASS: generated backend exists")

        # -------------------------------------------------
        # Python compilation
        # -------------------------------------------------

        compile_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                str(backend),
            ],
            capture_output=True,
            text=True,
        )

        if compile_result.returncode == 0:
            report["python_compile"] = True
            print("PASS: Python compilation")
        else:
            print("FAIL: Python compilation")
            print(
                compile_result.stderr
                or compile_result.stdout
            )

        # -------------------------------------------------
        # Important module imports
        # -------------------------------------------------

        modules = [
            "app.database",
            "app.main",
            "app.core.config",
            "app.core.security",
            "app.models.user",
            "app.models.project",
            "app.schemas.user",
            "app.schemas.project",
            "app.services.user_service",
            "app.services.auth_service",
            "app.services.project_service",
            "app.api.routes.users",
            "app.api.routes.auth",
            "app.api.routes.projects",
        ]

        for module in modules:

            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "import importlib; "
                        f"importlib.import_module('{module}')"
                    ),
                ],
                cwd=str(backend),
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                report["module_imports"].append(
                    {
                        "module": module,
                        "status": "PASS",
                    }
                )
                print(
                    f"PASS: import {module}"
                )
            else:
                report["module_imports"].append(
                    {
                        "module": module,
                        "status": "FAIL",
                        "error": (
                            result.stderr
                            or result.stdout
                        ).strip(),
                    }
                )
                print(
                    f"FAIL: import {module}"
                )

        # -------------------------------------------------
        # FastAPI + OpenAPI
        # -------------------------------------------------

        openapi_script = (
            "import app.main; "
            "spec=app.main.app.openapi(); "
            "print(len(spec.get('paths', {}))); "
            "print('\\n'.join(spec.get('paths', {}).keys()))"
        )

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                openapi_script,
            ],
            cwd=str(backend),
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            report["fastapi_import"] = True
            report["openapi_available"] = True

            lines = [
                line.strip()
                for line in result.stdout.splitlines()
                if line.strip()
            ]

            if lines:
                try:
                    int(lines[0])
                    report["openapi_paths"] = (
                        lines[1:]
                    )
                except ValueError:
                    report["openapi_paths"] = lines

            print("PASS: FastAPI import")
            print(
                "PASS: OpenAPI generation"
            )
            print(
                f"OpenAPI paths: "
                f"{len(report['openapi_paths'])}"
            )

        else:
            print("FAIL: FastAPI/OpenAPI")
            print(
                result.stderr
                or result.stdout
            )

        # -------------------------------------------------
        # Live HTTP checks
        # -------------------------------------------------

        endpoints = [
            "/",
            "/health",
            "/api/health",
            "/openapi.json",
        ]

        for endpoint in endpoints:

            url = (
                self.live_base_url
                + endpoint
            )

            try:

                with urlopen(
                    url,
                    timeout=10,
                ) as response:

                    body = response.read(
                        2000
                    ).decode(
                        "utf-8",
                        errors="replace",
                    )

                    item = {
                        "endpoint": endpoint,
                        "status": "PASS",
                        "http_status": response.status,
                        "body": body,
                    }

                    report["http_checks"].append(
                        item
                    )

                    print(
                        f"PASS: GET {endpoint} "
                        f"({response.status})"
                    )

            except HTTPError as exc:

                report["http_checks"].append(
                    {
                        "endpoint": endpoint,
                        "status": "FAIL",
                        "http_status": exc.code,
                        "error": str(exc),
                    }
                )

                print(
                    f"FAIL: GET {endpoint} "
                    f"({exc.code})"
                )

            except URLError as exc:

                report["http_checks"].append(
                    {
                        "endpoint": endpoint,
                        "status": "NOT_AVAILABLE",
                        "error": str(exc),
                    }
                )

                print(
                    f"NOT AVAILABLE: GET {endpoint}"
                )

            except Exception as exc:

                report["http_checks"].append(
                    {
                        "endpoint": endpoint,
                        "status": "FAIL",
                        "error": str(exc),
                    }
                )

                print(
                    f"FAIL: GET {endpoint}"
                )

        # -------------------------------------------------
        # Overall deterministic status
        # -------------------------------------------------

        module_failures = [
            item
            for item in report[
                "module_imports"
            ]
            if item["status"] != "PASS"
        ]

        http_failures = [
            item
            for item in report[
                "http_checks"
            ]
            if item["status"] == "FAIL"
        ]

        required_http = [
            item
            for item in report[
                "http_checks"
            ]
            if item["endpoint"]
            in {
                "/",
                "/health",
                "/api/health",
                "/openapi.json",
            }
        ]

        required_http_passed = all(
            item["status"] == "PASS"
            for item in required_http
        )

        if (
            report["generated_backend_exists"]
            and report["python_compile"]
            and report["fastapi_import"]
            and report["openapi_available"]
            and len(report["openapi_paths"]) > 0
            and not module_failures
            and not http_failures
            and required_http_passed
        ):
            report["overall"] = "PASS"

        return report

    async def generate_qa_review(
        self,
        task: str,
        deterministic: dict,
    ):

        ceo = self._get(
            "ceo",
            300,
        )

        pm = self._get(
            "pm",
            350,
        )

        cto = self._get(
            "cto",
            450,
        )

        security = self._get(
            "security",
            400,
        )

        prompt = f"""
You are the QA Engineer for an AI Software Company.

Review the actual deterministic validation results below and
produce a concise QA assessment.

Do not invent test results.

DETERMINISTIC VALIDATION:
{json.dumps(deterministic, indent=2, default=str)}

PROJECT REQUEST:
{self._limit(task, 300)}

CEO:
{ceo}

PM:
{pm}

CTO:
{cto}

SECURITY:
{security}

RETURN EXACTLY:

# QA Report

## Overall Status
Use PASS, FAIL, or NEEDS REVIEW based on the deterministic evidence.

## Automated Validation
Summarize actual validation results.

## Backend
Review compilation, imports, FastAPI, and OpenAPI.

## API
Review the live HTTP smoke tests.

## Security
Identify release blockers supported by evidence.

## Integration
Identify backend integration concerns.

## Critical Findings
List confirmed problems only.

## Recommendations
Use "Recommended:" for proposals.

## Release Gate
State whether the generated backend is ready for the next workflow stage.

Do not claim a test was executed unless it appears in the
deterministic validation results.
"""

        return await self.think(
            prompt
        )

    def build_final_report(
        self,
        deterministic: dict,
        llm_report: str,
    ):

        openapi_lines = "\n".join(
            f"- {path}"
            for path in deterministic.get(
                "openapi_paths",
                [],
            )
        )

        if not openapi_lines:
            openapi_lines = "Not available."

        http_lines = "\n".join(
            (
                f"- {item.get('endpoint', '')}: "
                f"{item.get('status', 'UNKNOWN')}"
                + (
                    f" ({item['http_status']})"
                    if "http_status" in item
                    else ""
                )
            )
            for item in deterministic.get(
                "http_checks",
                [],
            )
        )

        if not http_lines:
            http_lines = "No live HTTP checks recorded."

        return (
            "# QA Validation\n\n"
            "## Deterministic Status\n"
            f"{deterministic.get('overall', 'FAIL')}\n\n"
            "## OpenAPI Paths\n"
            f"{openapi_lines}\n\n"
            "## Live HTTP Checks\n"
            f"{http_lines}\n\n"
            "## Module Import Summary\n"
            f"{self._module_summary(deterministic)}\n\n"
            "## QA Assessment\n\n"
            f"{str(llm_report or '').strip()}\n"
        )

    @staticmethod
    def _module_summary(deterministic: dict):

        imports = deterministic.get(
            "module_imports",
            [],
        )

        if not imports:
            return "No module import results recorded."

        lines = []

        for item in imports:
            module = item.get(
                "module",
                "unknown",
            )

            status = item.get(
                "status",
                "UNKNOWN",
            )

            lines.append(
                f"- {module}: {status}"
            )

            if status != "PASS" and item.get(
                "error"
            ):
                lines.append(
                    "  Error: "
                    + str(
                        item["error"]
                    ).replace(
                        "\r",
                        " ",
                    ).replace(
                        "\n",
                        " ",
                    )
                )

        return "\n".join(lines)
    @staticmethod
    def _get(
        key: str,
        maximum: int,
    ):

        value = memory.get(key)

        if not value:
            return (
                "Not provided in current project context."
            )

        value = str(value)

        if len(value) <= maximum:
            return value

        return (
            value[:maximum]
            + "\n[Context truncated.]"
        )

    @staticmethod
    def _limit(
        value: str,
        maximum: int,
    ):

        value = str(value or "")

        if len(value) <= maximum:
            return value

        return (
            value[:maximum]
            + "\n[Context truncated.]"
        )


