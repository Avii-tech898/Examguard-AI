from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.health import router as health_router
from backend.api.documents import router as documents_router
from backend.api.document_text import router as document_text_router
from backend.api.analysis import router as analysis_router
from backend.api.similarity import router as similarity_router
from backend.api.risk import router as risk_router
from backend.api.alerts import router as alerts_router
from backend.api.analytics import router as analytics_router
from backend.api.processing import router as processing_router


app = FastAPI(
    title="EXAMGUARD AI API",
    description="AI-Powered Examination Security & Leak Risk Detection Platform",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(document_text_router)
app.include_router(documents_router)
app.include_router(analysis_router)
app.include_router(similarity_router)
app.include_router(risk_router)
app.include_router(alerts_router)
app.include_router(analytics_router)
app.include_router(processing_router)


@app.get("/")
def root():
    return {
        "project": "EXAMGUARD AI",
        "status": "online",
        "version": "0.1.0"
    }