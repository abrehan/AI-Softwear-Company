from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def status():
    return {
        "application": "AI Software Company",
        "version": "1.0.0",
        "backend": "Online",
        "frontend": "Online",
        "ollama": "Not Connected",
        "database": "Not Connected",
        "system": "Healthy"
    }
