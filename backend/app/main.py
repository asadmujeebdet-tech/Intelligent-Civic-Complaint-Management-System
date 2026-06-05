from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Scope, Receive, Send
from backend.app.config import settings
from backend.app.database import Database
from backend.app.routes import complaints, maps, chatbot
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_ASSET_VERSION = "7"


class NoCacheStaticFiles(StaticFiles):
    """Serve static files without browser caching (dev-friendly)."""

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend([
                    (b"cache-control", b"no-cache, no-store, must-revalidate"),
                    (b"pragma", b"no-cache"),
                    (b"expires", b"0"),
                ])
                message = {**message, "headers": headers}
            await send(message)

        await super().__call__(scope, receive, send_wrapper)


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AllowStreamlitIframeMiddleware(BaseHTTPMiddleware):
    """Allow the HTML UI to load inside Streamlit's iframe shell."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if not request.url.path.startswith("/api"):
            response.headers["Content-Security-Policy"] = (
                "frame-ancestors 'self' http://localhost:* http://127.0.0.1:* "
                "https://*.streamlit.app https://share.streamlit.io"
            )
        return response


app.add_middleware(AllowStreamlitIframeMiddleware)

# Events
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    logger.info("🚀 Starting CivicLens AI Backend")
    try:
        Database.connect()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown"""
    logger.info("🛑 Shutting down CivicLens AI Backend")
    Database.disconnect()

# Routes
app.include_router(complaints.router)
app.include_router(maps.router)
app.include_router(chatbot.router)


# Legacy feedback endpoint alias (spec compatibility)
from backend.app.models.complaint import FeedbackCreate, FeedbackResponse
from backend.app.services.complaint_service import ComplaintService as _ComplaintService


@app.post("/api/complaint/{complaint_id}/feedback", response_model=FeedbackResponse)
async def legacy_submit_feedback(complaint_id: str, feedback: FeedbackCreate):
    success = _ComplaintService.submit_feedback(complaint_id, feedback.rating, feedback.comment)
    if not success:
        raise HTTPException(status_code=400, detail="Feedback not allowed.")
    return FeedbackResponse(success=True)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CivicLens AI Backend",
        "version": settings.API_VERSION
    }

# Serve frontend static files
frontend_path = Path(__file__).parent.parent.parent / "frontend"

if frontend_path.exists():
    logger.info(f"📁 Serving frontend from: {frontend_path}")

    @app.get("/info")
    async def info():
        """API information endpoint"""
        return {
            "name": "CivicLens AI",
            "description": "Intelligent Civic Complaint Management System",
            "version": settings.API_VERSION,
            "api_docs": "/api/docs",
            "frontend": "/",
            "api_base": "/api/v1",
            "asset_version": APP_ASSET_VERSION,
        }

    app.mount(
        "/",
        NoCacheStaticFiles(directory=str(frontend_path), html=True),
        name="frontend",
    )
else:
    logger.warning(f"⚠️  Frontend path not found: {frontend_path}")

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Welcome to CivicLens AI - Intelligent Civic Complaint Management System",
            "docs": "/api/docs",
            "api_version": settings.API_VERSION
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
