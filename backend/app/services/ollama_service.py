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
            os.getenv("OLLAMA_READ_TIMEOUT", "180")
        )

        self.write_timeout = float(
            os.getenv("OLLAMA_WRITE_TIMEOUT", "30")
        )

        self.pool_timeout = float(
            os.getenv("OLLAMA_POOL_TIMEOUT", "10")
        )

        self.num_predict = int(os.getenv("OLLAMA_NUM_PREDICT", "500"))

        self.num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "4096"))

    async def generate(self, prompt: str, model: str):

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

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:

                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": self.num_predict,
                            "num_ctx": self.num_ctx,
                            "temperature": 0.1,
                        },
                    }
                )

                response.raise_for_status()

                data = response.json()

                result = (data.get("response") or "").strip()

                print(
                    f"[OLLAMA] Response received "
                    f"({len(result):,} characters)."
                )

                return result

        except httpx.ConnectTimeout:
            return "Ollama connection timed out."

        except httpx.ReadTimeout:
            return (
                f"Ollama generation exceeded "
                f"{self.read_timeout:g} seconds."
            )

        except httpx.ConnectError:
            return (
                "Ollama is unavailable from this deployment. "
                "The configured Ollama endpoint is not reachable."
            )

        except httpx.HTTPStatusError as e:
            return f"Ollama HTTP Error {e.response.status_code}"

        except Exception as e:
            return f"Unexpected Ollama Error: {str(e)}"

