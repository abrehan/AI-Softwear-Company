from fastapi import FastAPI

app = FastAPI(title="AI Software Company Vercel Test")

@app.get("/api/status")
async def status():
    return {
        "version": "1.0.0",
        "backend": "Online",
        "frontend": "Online",
        "ollama": "Not Checked",
        "database": "Not Connected",
        "system": "Healthy",
        "vercel_test": True
    }

@app.get("/")
async def root():
    return {"message": "Vercel Python backend is working"}
