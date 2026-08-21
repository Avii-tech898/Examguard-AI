from fastapi import FastAPI

from backend.api.health import router as health_router


app = FastAPI(
    title="EXAMGUARD AI API",
    description="AI-Powered Examination Security & Leak Risk Detection Platform",
    version="0.1.0"
)


app.include_router(health_router)


@app.get("/")
def root():
    return {
        "project": "EXAMGUARD AI",
        "status": "online",
        "version": "0.1.0"
    }