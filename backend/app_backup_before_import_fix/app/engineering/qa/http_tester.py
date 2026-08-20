from __future__ import annotations

from typing import Any

import httpx


class HTTPEndpointTester:
    """
    PHASE 5 — HTTP ENDPOINT TESTER

    Discovers FastAPI endpoints from OpenAPI and performs
    safe smoke tests using valid example payloads.
    """

    SAFE_METHODS = {
        "GET",
        "POST",
        "PUT",
        "PATCH",
    }

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8766,
        timeout: float = 5.0,
    ):
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout

    async def get_openapi(self) -> dict[str, Any]:
        url = f"{self.base_url}/openapi.json"

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    def discover_endpoints(
        self,
        openapi: dict[str, Any],
    ) -> list[dict[str, Any]]:

        paths = openapi.get("paths", {})
        endpoints: list[dict[str, Any]] = []

        for path, methods in paths.items():

            if not isinstance(methods, dict):
                continue

            for method, definition in methods.items():

                method_upper = method.upper()

                if method_upper not in self.SAFE_METHODS:
                    continue

                if not isinstance(definition, dict):
                    definition = {}

                endpoints.append(
                    {
                        "path": path,
                        "method": method_upper,
                        "definition": definition,
                    }
                )

        return sorted(
            endpoints,
            key=lambda item: (
                item["path"],
                item["method"],
            ),
        )

    def build_payload(
        self,
        endpoint: dict[str, Any],
    ) -> dict[str, Any] | None:

        method = endpoint["method"]

        if method == "GET":
            return None

        path = endpoint["path"]

        # -----------------------------------------------------
        # Known application endpoints
        # -----------------------------------------------------

        if path in {"/predict", "/analyze"}:

            return {
                "input_data": {
                    "value": 100,
                    "category": "test",
                },
                "target_variable": "value",
            }

        # -----------------------------------------------------
        # Generic OpenAPI payload generation
        # -----------------------------------------------------

        definition = endpoint["definition"]

        request_body = definition.get("requestBody")

        if not request_body:
            return {}

        content = request_body.get("content", {})

        json_content = content.get(
            "application/json",
            {},
        )

        schema = json_content.get("schema", {})

        # Resolve local $ref schemas
        if "$ref" in schema:

            ref_name = schema["$ref"].split("/")[-1]

            # The tester does not receive the full OpenAPI document
            # here, so use a safe fallback.
            if ref_name == "PredictionRequest":

                return {
                    "input_data": {
                        "value": 100,
                        "category": "test",
                    },
                    "target_variable": "value",
                }

        properties = schema.get(
            "properties",
            {},
        )

        required = schema.get(
            "required",
            [],
        )

        payload: dict[str, Any] = {}

        for field in required:

            field_schema = properties.get(
                field,
                {},
            )

            field_type = field_schema.get(
                "type"
            )

            if field_type == "string":

                payload[field] = "test"

            elif field_type == "integer":

                payload[field] = 1

            elif field_type == "number":

                payload[field] = 1

            elif field_type == "boolean":

                payload[field] = True

            elif field_type == "array":

                payload[field] = []

            elif field_type == "object":

                payload[field] = {
                    "value": 100,
                    "category": "test",
                }

            else:

                payload[field] = "test"

        return payload

    async def test_endpoint(
        self,
        client: httpx.AsyncClient,
        endpoint: dict[str, Any],
    ) -> dict[str, Any]:

        path = endpoint["path"]
        method = endpoint["method"]

        url = f"{self.base_url}{path}"

        payload = self.build_payload(endpoint)

        try:

            if method == "GET":

                response = await client.get(url)

            elif method == "POST":

                response = await client.post(
                    url,
                    json=payload,
                )

            elif method == "PUT":

                response = await client.put(
                    url,
                    json=payload,
                )

            elif method == "PATCH":

                response = await client.patch(
                    url,
                    json=payload,
                )

            else:

                return {
                    "path": path,
                    "method": method,
                    "status_code": None,
                    "passed": False,
                    "payload": payload,
                    "error": "Unsupported HTTP method",
                }

            status = response.status_code

            try:
                response_body = response.json()
            except Exception:
                response_body = response.text

            # -------------------------------------------------
            # IMPORTANT:
            # Only 2xx responses are successful endpoint tests.
            # -------------------------------------------------

            passed = 200 <= status < 300

            return {
                "path": path,
                "method": method,
                "status_code": status,
                "passed": passed,
                "payload": payload,
                "response": response_body,
                "error": (
                    None
                    if passed
                    else f"HTTP {status}"
                ),
            }

        except Exception as e:

            return {
                "path": path,
                "method": method,
                "status_code": None,
                "passed": False,
                "payload": payload,
                "response": None,
                "error": str(e),
            }

    async def run(self) -> dict[str, Any]:

        print()
        print("=" * 60)
        print("🌐 PHASE 5 — HTTP ENDPOINT TESTER")
        print("=" * 60)

        # -----------------------------------------------------
        # OpenAPI
        # -----------------------------------------------------

        try:

            openapi = await self.get_openapi()

        except Exception as e:

            print("❌ Could not connect to FastAPI.")
            print(f"   {e}")

            return {
                "success": False,
                "stage": "openapi",
                "error": str(e),
            }

        # -----------------------------------------------------
        # Discover endpoints
        # -----------------------------------------------------

        endpoints = self.discover_endpoints(
            openapi
        )

        print(
            f"🔎 HTTP endpoints found: "
            f"{len(endpoints)}"
        )

        if not endpoints:

            print(
                "❌ No testable HTTP endpoints found."
            )

            return {
                "success": False,
                "stage": "http_testing",
                "endpoint_count": 0,
                "passed": 0,
                "failed": 0,
                "results": [],
            }

        results = []

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            for endpoint in endpoints:

                method = endpoint["method"]
                path = endpoint["path"]

                print(
                    f"🌐 {method} {path}"
                )

                result = await self.test_endpoint(
                    client,
                    endpoint,
                )

                results.append(result)

                if result["passed"]:

                    print(
                        f"   ✅ {result['status_code']}"
                    )

                else:

                    print(
                        f"   ❌ HTTP "
                        f"{result['status_code']}"
                    )

                    if result.get("payload") is not None:

                        print(
                            f"   📦 Payload:"
                        )

                        print(
                            f"      "
                            f"{result['payload']}"
                        )

                    if result.get("response") is not None:

                        print(
                            f"   📄 Response:"
                        )

                        print(
                            f"      "
                            f"{result['response']}"
                        )

        passed = [
            result
            for result in results
            if result["passed"]
        ]

        failed = [
            result
            for result in results
            if not result["passed"]
        ]

        success = len(failed) == 0

        print()
        print("=" * 60)

        if success:

            print(
                "🎉 HTTP ENDPOINT TESTS PASSED"
            )

        else:

            print(
                f"❌ HTTP ENDPOINT TESTS FAILED "
                f"({len(failed)} errors)"
            )

        print("=" * 60)

        return {
            "success": success,
            "stage": "http_testing",
            "endpoint_count": len(results),
            "passed": len(passed),
            "failed": len(failed),
            "results": results,
        }


async def main():

    tester = HTTPEndpointTester(
        host="127.0.0.1",
        port=8766,
    )

    print(
        "📡 Connecting to generated FastAPI..."
    )

    result = await tester.run()

    print()
    print("=" * 60)
    print("RESULT:")
    print(result)
    print("=" * 60)


if __name__ == "__main__":

    import asyncio

    asyncio.run(main())
