from fastapi import APIRouter
from app.services.ollama_service import OllamaService

router = APIRouter()

ollama = OllamaService()


@router.get("/ask")
async def ask_ai(prompt: str):

    answer = await ollama.generate(
        prompt,
        "llama3.2:1b"
    )

    return {
        "success": True,
        "model": "llama3.2:1b",
        "answer": answer
    }