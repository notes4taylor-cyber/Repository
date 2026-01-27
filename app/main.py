"""
MasterFlow - AI-Powered Music Mastering Platform

Main FastAPI application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.api import router as api_router
from app.models.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await create_tables()
    print(f"🎵 {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    print(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    print(f"📁 Output directory: {settings.OUTPUT_DIR}")
    yield
    # Shutdown
    print(f"👋 {settings.APP_NAME} shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.APP_NAME,
            "pricing": settings.PRICING,
        }
    )


@app.get("/app", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the main application dashboard."""
    return templates.TemplateResponse(
        "app.html",
        {
            "request": request,
            "app_name": settings.APP_NAME,
            "presets": settings.MASTERING_PRESETS,
            "genres": list(settings.GENRE_PRESETS.keys()),
        }
    )


@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    """Render the pricing page."""
    return templates.TemplateResponse(
        "pricing.html",
        {
            "request": request,
            "app_name": settings.APP_NAME,
            "pricing": settings.PRICING,
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_code": 404,
            "error_message": "Page not found",
        },
        status_code=404,
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Handle 500 errors."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_code": 500,
            "error_message": "Internal server error",
        },
        status_code=500,
    )
