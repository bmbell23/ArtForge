"""Main FastAPI application."""

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from sqlalchemy.orm import Session
from .config import settings
from .database import engine, Base, get_db
from .routes import auth, artworks
from .auth import get_current_user_from_cookie

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A platform for artists to showcase and share their artwork",
    version="0.1.0"
)

# Setup paths
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOAD_DIR = Path(settings.upload_dir)

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files under /art/ prefix to avoid conflicts with other apps
app.mount("/art/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/art/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include routers
app.include_router(auth.router, tags=["auth"])
app.include_router(artworks.router, tags=["artworks"])


@app.get("/", response_class=HTMLResponse)
async def redirect_to_art():
    """Redirect root to /art/."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/art/")


@app.get("/art/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page - landing page for ArtForge."""
    current_user = get_current_user_from_cookie(request, db)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": settings.app_name,
            "current_user": current_user,
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}

