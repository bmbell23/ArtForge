"""Artwork routes for viewing and managing artworks."""

import os
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from PIL import Image
from ..database import get_db
from ..models.user import User
from ..models.artwork import Artwork, ArtworkImage
from ..auth import get_current_user_from_cookie
from ..config import settings

router = APIRouter()

# Setup templates
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    """Create a URL-friendly slug from text."""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def save_uploaded_image(file: UploadFile) -> tuple:
    """Save an uploaded image and return (filename, width, height, file_size)."""
    # Generate unique filename
    ext = file.filename.split('.')[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    # Save file
    with open(filepath, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    # Get image dimensions
    try:
        with Image.open(filepath) as img:
            width, height = img.size
    except:
        width, height = None, None
    
    file_size = os.path.getsize(filepath)
    
    return filename, width, height, file_size


@router.get("/art/browse")
async def browse_artworks(request: Request, db: Session = Depends(get_db)):
    """Browse all public artworks."""
    current_user = get_current_user_from_cookie(request, db)

    # Get all public artworks, ordered by most recent
    artworks = db.query(Artwork).filter(
        Artwork.is_public == True
    ).order_by(Artwork.created_at.desc()).all()

    return templates.TemplateResponse(
        "browse.html",
        {
            "request": request,
            "title": "Browse Art - ArtForge",
            "current_user": current_user,
            "artworks": artworks,
        }
    )


@router.get("/art/{username}")
async def user_gallery(username: str, request: Request, db: Session = Depends(get_db)):
    """Display user's artwork gallery."""
    current_user = get_current_user_from_cookie(request, db)
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's artworks
    artworks = db.query(Artwork).filter(Artwork.artist_id == user.id).order_by(Artwork.created_at.desc()).all()
    
    # Filter to public artworks if not the owner
    if not current_user or current_user.id != user.id:
        artworks = [a for a in artworks if a.is_public]
    
    is_owner = current_user and current_user.id == user.id
    
    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "title": f"{user.username}'s Gallery - ArtForge",
            "current_user": current_user,
            "gallery_user": user,
            "artworks": artworks,
            "is_owner": is_owner,
        }
    )


@router.get("/art/{username}/upload")
async def upload_artwork_page(username: str, request: Request, db: Session = Depends(get_db)):
    """Display artwork upload page."""
    current_user = get_current_user_from_cookie(request, db)
    
    if not current_user or current_user.username != username:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "title": "Upload Artwork - ArtForge",
            "current_user": current_user,
        }
    )


@router.post("/art/{username}/upload")
async def upload_artwork(
    username: str,
    title: str = Form(...),
    description: str = Form(None),
    is_public: bool = Form(True),
    images: List[UploadFile] = File(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Process artwork upload."""
    current_user = get_current_user_from_cookie(request, db)
    
    if not current_user or current_user.username != username:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not images:
        raise HTTPException(status_code=400, detail="At least one image is required")
    
    # Create artwork
    slug = slugify(title)
    # Ensure unique slug
    base_slug = slug
    counter = 1
    while db.query(Artwork).filter(Artwork.slug == slug, Artwork.artist_id == current_user.id).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    artwork = Artwork(
        title=title,
        slug=slug,
        description=description,
        artist_id=current_user.id,
        is_public=is_public
    )
    db.add(artwork)
    db.commit()
    db.refresh(artwork)
    
    # Save images
    for idx, image_file in enumerate(images):
        filename, width, height, file_size = save_uploaded_image(image_file)
        
        artwork_image = ArtworkImage(
            artwork_id=artwork.id,
            filename=filename,
            original_filename=image_file.filename,
            order=idx,
            is_primary=(idx == 0),  # First image is primary
            width=width,
            height=height,
            file_size=file_size
        )
        db.add(artwork_image)
    
    db.commit()
    
    return RedirectResponse(url=f"/art/{username}/{slug}", status_code=302)


@router.get("/art/{username}/{slug}")
async def view_artwork(username: str, slug: str, request: Request, db: Session = Depends(get_db)):
    """Display artwork detail page."""
    current_user = get_current_user_from_cookie(request, db)
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    artwork = db.query(Artwork).filter(
        Artwork.slug == slug,
        Artwork.artist_id == user.id
    ).first()

    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Check permissions
    is_owner = current_user and current_user.id == artwork.artist_id
    if not artwork.is_public and not is_owner:
        raise HTTPException(status_code=403, detail="This artwork is private")

    # Get spark count and check if user has sparked
    spark_count = len(artwork.sparks)
    user_has_sparked = False

    if current_user:
        from ..models.spark import Spark
        user_has_sparked = db.query(Spark).filter(
            Spark.artwork_id == artwork.id,
            Spark.user_id == current_user.id
        ).first() is not None
    else:
        # Check by session ID for anonymous users
        session_id = request.cookies.get("session_id")
        if session_id:
            from ..models.spark import Spark
            user_has_sparked = db.query(Spark).filter(
                Spark.artwork_id == artwork.id,
                Spark.session_id == session_id
            ).first() is not None

    # Get comments
    from ..models.comment import Comment
    comments = db.query(Comment).filter(
        Comment.artwork_id == artwork.id
    ).order_by(Comment.created_at.desc()).all()

    return templates.TemplateResponse(
        "artwork.html",
        {
            "request": request,
            "title": f"{artwork.title} - ArtForge",
            "current_user": current_user,
            "artwork": artwork,
            "is_owner": is_owner,
            "spark_count": spark_count,
            "user_has_sparked": user_has_sparked,
            "comments": comments,
        }
    )


@router.post("/art/{username}/{slug}/delete")
async def delete_artwork(username: str, slug: str, request: Request, db: Session = Depends(get_db)):
    """Delete an artwork and its images."""
    current_user = get_current_user_from_cookie(request, db)

    if not current_user or current_user.username != username:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    artwork = db.query(Artwork).filter(
        Artwork.slug == slug,
        Artwork.artist_id == user.id
    ).first()

    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Delete image files from disk
    for image in artwork.images:
        image_path = UPLOAD_DIR / image.filename
        if image_path.exists():
            image_path.unlink()

    # Delete from database (cascade will handle images)
    db.delete(artwork)
    db.commit()

    return RedirectResponse(url=f"/art/{username}", status_code=302)


@router.post("/art/{username}/{slug}/delete-image/{image_id}")
async def delete_artwork_image(
    username: str,
    slug: str,
    image_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a single image from an artwork."""
    current_user = get_current_user_from_cookie(request, db)

    if not current_user or current_user.username != username:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    artwork = db.query(Artwork).filter(
        Artwork.slug == slug,
        Artwork.artist_id == user.id
    ).first()

    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Don't allow deleting the last image
    if len(artwork.images) <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the last image. Delete the artwork instead.")

    # Find the image
    image = db.query(ArtworkImage).filter(
        ArtworkImage.id == image_id,
        ArtworkImage.artwork_id == artwork.id
    ).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete file from disk
    image_path = UPLOAD_DIR / image.filename
    if image_path.exists():
        image_path.unlink()

    # If this was the primary image, make the first remaining image primary
    was_primary = image.is_primary

    # Delete from database
    db.delete(image)
    db.commit()

    # Update primary image if needed
    if was_primary:
        remaining_images = db.query(ArtworkImage).filter(
            ArtworkImage.artwork_id == artwork.id
        ).order_by(ArtworkImage.order).all()

        if remaining_images:
            remaining_images[0].is_primary = True
            db.commit()

    return RedirectResponse(url=f"/art/{username}/{slug}", status_code=302)

