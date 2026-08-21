from fastapi import FastAPI

app = FastAPI(
    title="EXAMGUARD AI API",
    description="AI-Powered Examination Security & Leak Risk Detection Platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "project": "EXAMGUARD AI",
        "status": "online",
        "version": "0.1.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "EXAMGUARD AI Backend"
    }