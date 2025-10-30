"""Authentication routes."""

from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from ..database import get_db
from ..models.user import User
from ..auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user_from_cookie,
)

router = APIRouter()

# Setup templates
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/art/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    """Display login page."""
    current_user = get_current_user_from_cookie(request, db)
    if current_user:
        return RedirectResponse(url=f"/art/{current_user.username}", status_code=302)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "title": "Login - ArtForge"}
    )


@router.post("/art/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login form."""
    user = authenticate_user(db, username, password)
    if not user:
        return RedirectResponse(url="/art/login?error=invalid", status_code=302)
    
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url=f"/art/{user.username}", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        samesite="lax"
    )
    return response


@router.get("/art/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    """Display registration page."""
    current_user = get_current_user_from_cookie(request, db)
    if current_user:
        return RedirectResponse(url=f"/art/{current_user.username}", status_code=302)

    return templates.TemplateResponse(
        "register.html",
        {"request": request, "title": "Register - ArtForge"}
    )


@router.post("/art/register")
async def register(
    username: str = Form(...),
    email: str = Form(None),
    password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db)
):
    """Process registration form."""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return RedirectResponse(url="/art/register?error=username_exists", status_code=302)
    
    # Check if email already exists
    if email:
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            return RedirectResponse(url="/art/register?error=email_exists", status_code=302)
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log them in
    access_token = create_access_token(data={"sub": new_user.username})
    response = RedirectResponse(url=f"/art/{new_user.username}", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax"
    )
    return response


@router.get("/art/logout")
async def logout():
    """Logout user."""
    response = RedirectResponse(url="/art/", status_code=302)
    response.delete_cookie("access_token")
    return response

