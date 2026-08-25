import os
import httpx


class OllamaService:

    def __init__(self):
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://127.0.0.1:11434"
        ).rstrip("/")

        self.connect_timeout = float(
            os.getenv("OLLAMA_CONNECT_TIMEOUT", "10")
        )

        self.read_timeout = float(
            os.getenv("OLLAMA_READ_TIMEOUT", "300")
        )

        self.write_timeout = float(
            os.getenv("OLLAMA_WRITE_TIMEOUT", "30")
        )

        self.pool_timeout = float(
            os.getenv("OLLAMA_POOL_TIMEOUT", "10")
        )

        self.num_predict = int(
            os.getenv("OLLAMA_NUM_PREDICT", "700")
        )

        self.num_ctx = int(
            os.getenv("OLLAMA_NUM_CTX", "4096")
        )

        self.temperature = float(
            os.getenv("OLLAMA_TEMPERATURE", "0.1")
        )

    async def generate(self, prompt: str, model: str) -> str:

        print(f"[OLLAMA] URL: {self.base_url}")
        print(f"[OLLAMA] Using model: {model}")
        print(f"[OLLAMA] Prompt length: {len(prompt):,} characters")
        print(f"[OLLAMA] Max output tokens: {self.num_predict}")
        print(f"[OLLAMA] Context window: {self.num_ctx}")
        print(f"[OLLAMA] Read timeout: {self.read_timeout:g}s")

        timeout = httpx.Timeout(
            connect=self.connect_timeout,
            read=self.read_timeout,
            write=self.write_timeout,
            pool=self.pool_timeout,
        )

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": self.num_predict,
                "num_ctx": self.num_ctx,
                "temperature": self.temperature,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:

                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

                result = (data.get("response") or "").strip()

                if not result:
                    raise RuntimeError(
                        f"Ollama returned an empty response for model '{model}'."
                    )

                print(
                    f"[OLLAMA] Response received "
                    f"({len(result):,} characters)."
                )

                return result

        except httpx.ConnectTimeout as e:
            raise RuntimeError(
                f"Ollama connection timed out after "
                f"{self.connect_timeout:g} seconds."
            ) from e

        except httpx.ReadTimeout as e:
            raise RuntimeError(
                f"Ollama model '{model}' did not finish generation within "
                f"{self.read_timeout:g} seconds."
            ) from e

        except httpx.ConnectError as e:
            raise RuntimeError(
                "Ollama is unavailable. "
                f"Could not connect to {self.base_url}."
            ) from e

        except httpx.HTTPStatusError as e:
            body = e.response.text[:500]

            raise RuntimeError(
                f"Ollama HTTP error {e.response.status_code}: {body}"
            ) from e

        except httpx.RequestError as e:
            raise RuntimeError(
                f"Ollama request failed: {str(e)}"
            ) from e

        except Exception as e:
            raise RuntimeError(
                f"Unexpected Ollama error: {str(e)}"
            ) from e
