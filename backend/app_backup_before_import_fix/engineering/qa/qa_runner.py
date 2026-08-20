from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import httpx


class QARunner:
    """
    PHASE 6 — INTEGRATED QA RUNNER

    Responsibilities:
    1. Detect an already-running FastAPI server.
    2. Start FastAPI if it is not running.
    3. Wait for /health.
    4. Validate /openapi.json.
    5. Test all important application endpoints.
    6. Require expected HTTP status codes.
    7. Validate response bodies.
    8. Stop only the server started by this runner.
    """

    def __init__(
        self,
        project_root: str = "generated_code",
        host: str = "127.0.0.1",
        port: int = 8766,
        startup_timeout: int = 15,
    ):
        self.project_root = Path(project_root).resolve()
        self.host = host
        self.port = port
        self.startup_timeout = startup_timeout

        self.app_directory = (
            self.project_root / "backend"
        )

        self.main_file = (
            self.app_directory
            / "app"
            / "main.py"
        )

        self.base_url = (
            f"http://{self.host}:{self.port}"
        )

        self.process = None
        self.started_by_runner = False

    # ---------------------------------------------------------
    # Python executable
    # ---------------------------------------------------------

    def find_python(self) -> str:

        candidates = [
            self.project_root.parent
            / ".venv"
            / "Scripts"
            / "python.exe",

            Path(sys.executable),
        ]

        for python in candidates:

            if python.exists():
                return str(python)

        return sys.executable

    # ---------------------------------------------------------
    # Check existing server
    # ---------------------------------------------------------

    async def server_is_running(self) -> bool:

        try:

            async with httpx.AsyncClient(
                timeout=2
            ) as client:

                response = await client.get(
                    f"{self.base_url}/health"
                )

                return response.status_code == 200

        except (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadError,
            httpx.RemoteProtocolError,
        ):

            return False

    # ---------------------------------------------------------
    # Start FastAPI
    # ---------------------------------------------------------

    async def start_server(self):

        if not self.main_file.exists():

            return {
                "success": False,
                "stage": "startup",
                "error": (
                    "FastAPI main.py not found: "
                    f"{self.main_file}"
                ),
            }

        python = self.find_python()

        print(
            f"🐍 Python: {python}"
        )

        print(
            f"📁 Backend: "
            f"{self.app_directory}"
        )

        print(
            f"🚀 Starting FastAPI on "
            f"{self.host}:{self.port}"
        )

        self.process = (
            await asyncio.create_subprocess_exec(
                python,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                self.host,
                "--port",
                str(self.port),
                cwd=str(self.app_directory),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        )

        self.started_by_runner = True

        return self.process

    # ---------------------------------------------------------
    # Wait for server
    # ---------------------------------------------------------

    async def wait_for_server(self) -> dict[str, Any]:

        print(
            "⏳ Waiting for FastAPI..."
        )

        deadline = (
            asyncio.get_running_loop().time()
            + self.startup_timeout
        )

        while (
            asyncio.get_running_loop().time()
            < deadline
        ):

            if self.process is not None:

                if self.process.returncode is not None:

                    stdout, stderr = (
                        await self.process.communicate()
                    )

                    return {
                        "success": False,
                        "stage": "startup",
                        "error": (
                            "FastAPI process exited "
                            "before becoming ready."
                        ),
                        "stdout": stdout.decode(
                            "utf-8",
                            errors="replace",
                        ),
                        "stderr": stderr.decode(
                            "utf-8",
                            errors="replace",
                        ),
                    }

            if await self.server_is_running():

                print(
                    "✅ FastAPI is responding."
                )

                return {
                    "success": True,
                    "url": (
                        f"{self.base_url}/health"
                    ),
                }

            await asyncio.sleep(0.5)

        return {
            "success": False,
            "stage": "startup_timeout",
            "error": (
                "FastAPI did not respond within "
                f"{self.startup_timeout} seconds."
            ),
        }

    # ---------------------------------------------------------
    # HTTP request helper
    # ---------------------------------------------------------

    async def request(
        self,
        client: httpx.AsyncClient,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        url = f"{self.base_url}{path}"

        try:

            if method == "GET":

                response = await client.get(url)

            elif method == "POST":

                response = await client.post(
                    url,
                    json=payload,
                )

            else:

                return {
                    "passed": False,
                    "method": method,
                    "path": path,
                    "status_code": None,
                    "error": (
                        f"Unsupported method: {method}"
                    ),
                }

            try:
                body = response.json()
            except Exception:
                body = response.text

            return {
                "passed": response.status_code < 400,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "body": body,
                "payload": payload,
                "error": (
                    None
                    if response.status_code < 400
                    else f"HTTP {response.status_code}"
                ),
            }

        except Exception as exc:

            return {
                "passed": False,
                "method": method,
                "path": path,
                "status_code": None,
                "body": None,
                "payload": payload,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Validate response
    # ---------------------------------------------------------

    def validate_response(
        self,
        result: dict[str, Any],
        required_keys: list[str] | None = None,
    ) -> dict[str, Any]:

        if not result.get("passed"):

            return result

        body = result.get("body")

        if required_keys:

            if not isinstance(body, dict):

                result["passed"] = False
                result["error"] = (
                    "Response body is not a JSON object."
                )

                return result

            missing = [
                key
                for key in required_keys
                if key not in body
            ]

            if missing:

                result["passed"] = False
                result["error"] = (
                    "Missing response fields: "
                    + ", ".join(missing)
                )

        return result

    # ---------------------------------------------------------
    # Run integration tests
    # ---------------------------------------------------------

    async def run_endpoint_tests(
        self,
    ) -> dict[str, Any]:

        print()
        print(
            "🌐 Running integration HTTP tests..."
        )

        results = []

        async with httpx.AsyncClient(
            timeout=5
        ) as client:

            # -------------------------------------------------
            # GET /
            # -------------------------------------------------

            print("🌐 GET /")

            result = await self.request(
                client,
                "GET",
                "/",
            )

            result = self.validate_response(
                result,
                [
                    "status",
                    "service",
                ],
            )

            results.append(result)

            print(
                "   "
                + (
                    "✅ PASS"
                    if result["passed"]
                    else "❌ FAIL"
                )
                + f" — HTTP {result.get('status_code')}"
            )

            # -------------------------------------------------
            # GET /health
            # -------------------------------------------------

            print("🌐 GET /health")

            result = await self.request(
                client,
                "GET",
                "/health",
            )

            result = self.validate_response(
                result,
                ["status"],
            )

            if result["passed"]:

                if result["body"].get(
                    "status"
                ) != "healthy":

                    result["passed"] = False
                    result["error"] = (
                        "Health status is not 'healthy'."
                    )

            results.append(result)

            print(
                "   "
                + (
                    "✅ PASS"
                    if result["passed"]
                    else "❌ FAIL"
                )
                + f" — HTTP {result.get('status_code')}"
            )

            # -------------------------------------------------
            # POST /predict
            # -------------------------------------------------

            print("🌐 POST /predict")

            predict_payload = {
                "input_data": {
                    "value": 100,
                    "category": "test",
                },
                "target_variable": "value",
            }

            result = await self.request(
                client,
                "POST",
                "/predict",
                predict_payload,
            )

            result = self.validate_response(
                result,
                [
                    "predicted_value",
                    "target_variable",
                    "input_data",
                ],
            )

            results.append(result)

            print(
                "   "
                + (
                    "✅ PASS"
                    if result["passed"]
                    else "❌ FAIL"
                )
                + f" — HTTP {result.get('status_code')}"
            )

            # -------------------------------------------------
            # POST /analyze
            # -------------------------------------------------

            print("🌐 POST /analyze")

            analyze_payload = {
                "input_data": {
                    "value": 100,
                    "category": "test",
                },
                "target_variable": "value",
            }

            result = await self.request(
                client,
                "POST",
                "/analyze",
                analyze_payload,
            )

            result = self.validate_response(
                result,
                [
                    "predicted_value",
                    "target_variable",
                    "input_data",
                ],
            )

            results.append(result)

            print(
                "   "
                + (
                    "✅ PASS"
                    if result["passed"]
                    else "❌ FAIL"
                )
                + f" — HTTP {result.get('status_code')}"
            )

        failed = [
            item
            for item in results
            if not item["passed"]
        ]

        passed = [
            item
            for item in results
            if item["passed"]
        ]

        return {
            "success": len(failed) == 0,
            "endpoint_count": len(results),
            "passed": len(passed),
            "failed": len(failed),
            "results": results,
        }

    # ---------------------------------------------------------
    # OpenAPI test
    # ---------------------------------------------------------

    async def test_openapi(
        self,
    ) -> dict[str, Any]:

        print()
        print(
            "📚 Checking OpenAPI..."
        )

        try:

            async with httpx.AsyncClient(
                timeout=5
            ) as client:

                response = await client.get(
                    f"{self.base_url}/openapi.json"
                )

            if response.status_code != 200:

                return {
                    "success": False,
                    "status_code": (
                        response.status_code
                    ),
                    "error": (
                        f"Expected HTTP 200, "
                        f"got {response.status_code}"
                    ),
                }

            document = response.json()

            paths = document.get(
                "paths",
                {},
            )

            required_paths = {
                "/",
                "/health",
                "/predict",
                "/analyze",
            }

            missing = (
                required_paths
                - set(paths.keys())
            )

            if missing:

                return {
                    "success": False,
                    "status_code": 200,
                    "error": (
                        "Missing OpenAPI paths: "
                        + ", ".join(
                            sorted(missing)
                        )
                    ),
                }

            print(
                "   ✅ OpenAPI valid"
            )

            return {
                "success": True,
                "status_code": 200,
                "paths": sorted(paths.keys()),
            }

        except Exception as exc:

            return {
                "success": False,
                "status_code": None,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Stop server
    # ---------------------------------------------------------

    async def stop_server(self):

        if (
            self.process is None
            or not self.started_by_runner
        ):
            return

        if self.process.returncode is not None:
            return

        print()
        print(
            "🛑 Stopping FastAPI..."
        )

        try:

            self.process.terminate()

            await asyncio.wait_for(
                self.process.wait(),
                timeout=5,
            )

        except (
            asyncio.TimeoutError,
            ProcessLookupError,
        ):

            try:
                self.process.kill()
            except ProcessLookupError:
                pass

    # ---------------------------------------------------------
    # Main QA pipeline
    # ---------------------------------------------------------

    async def run(self) -> dict[str, Any]:

        print()
        print("=" * 60)
        print(
            "🧪 PHASE 6 — INTEGRATED QA RUNNER"
        )
        print("=" * 60)

        try:

            # -------------------------------------------------
            # Existing server?
            # -------------------------------------------------

            if await self.server_is_running():

                print(
                    "♻️ Existing FastAPI server detected."
                )

                print(
                    "ℹ️ QA will use the existing server."
                )

            else:

                process = await self.start_server()

                if isinstance(process, dict):

                    return process

            # -------------------------------------------------
            # Wait
            # -------------------------------------------------

            startup = (
                await self.wait_for_server()
            )

            if not startup.get(
                "success",
                False,
            ):

                return startup

            # -------------------------------------------------
            # OpenAPI
            # -------------------------------------------------

            openapi = (
                await self.test_openapi()
            )

            if not openapi.get(
                "success",
                False,
            ):

                return {
                    "success": False,
                    "stage": "openapi",
                    "openapi": openapi,
                }

            # -------------------------------------------------
            # Endpoints
            # -------------------------------------------------

            endpoint_tests = (
                await self.run_endpoint_tests()
            )

            success = (
                endpoint_tests["success"]
                and openapi["success"]
            )

            print()
            print("=" * 60)

            if success:

                print(
                    "🎉 ALL PHASE 6 QA TESTS PASSED"
                )

            else:

                print(
                    "❌ PHASE 6 QA TESTS FAILED"
                )

            print("=" * 60)

            return {
                "success": success,
                "stage": "integration_qa",
                "host": self.host,
                "port": self.port,
                "openapi": openapi,
                "endpoint_tests": endpoint_tests,
            }

        except Exception as exc:

            return {
                "success": False,
                "stage": "qa_runner",
                "error": str(exc),
            }

        finally:

            await self.stop_server()


# -------------------------------------------------------------
# Manual execution
# -------------------------------------------------------------

async def main():

    runner = QARunner(
        project_root="generated_code",
        host="127.0.0.1",
        port=8766,
    )

    result = await runner.run()

    print()
    print("=" * 60)
    print("FINAL QA RESULT")
    print("=" * 60)

    print(result)

    if not result.get(
        "success",
        False,
    ):

        raise SystemExit(1)


if __name__ == "__main__":

    asyncio.run(main())