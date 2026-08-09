import httpx


class OllamaService:

    def __init__(self):
        self.base_url = "http://127.0.0.1:11434"

    async def generate(self, prompt: str, model: str):

        print(f"[OLLAMA] Using model: {model}")

        try:
            async with httpx.AsyncClient(timeout=None) as client:

                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    }
                )

                response.raise_for_status()

                data = response.json()

                print("[OLLAMA] Response received.")

                return data.get("response", "")

        except httpx.ConnectError:
            return (
                "❌ Cannot connect to Ollama.\n"
                "Start it with:\n"
                "ollama serve"
            )

        except httpx.ReadTimeout:
            return "❌ Ollama took too long to respond."

        except httpx.HTTPStatusError as e:
            return f"❌ Ollama HTTP Error {e.response.status_code}"

        except Exception as e:
            return f"❌ Unexpected Error: {str(e)}"