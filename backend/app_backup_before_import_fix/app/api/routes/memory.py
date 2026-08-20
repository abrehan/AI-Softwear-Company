from fastapi import APIRouter
from backend.app.memory.memory_store import MemoryStore

router = APIRouter()

memory = MemoryStore()


@router.get("/")
async def all_memory():
    return memory.all()
