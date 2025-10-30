"""Routes for sparks (likes) and comments."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.artwork import Artwork
from ..models.spark import Spark
from ..models.comment import Comment
from ..auth import get_current_user_from_cookie
import uuid

router = APIRouter()


@router.post("/art/{username}/{slug}/spark")
async def toggle_spark(
    username: str,
    slug: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Toggle a spark (like) on an artwork."""
    current_user = get_current_user_from_cookie(request, db)
    
    # Get the artwork
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    artwork = db.query(Artwork).filter(
        Artwork.slug == slug,
        Artwork.artist_id == user.id
    ).first()
    
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # Check if user already sparked
    if current_user:
        existing_spark = db.query(Spark).filter(
            Spark.artwork_id == artwork.id,
            Spark.user_id == current_user.id
        ).first()
    else:
        # For anonymous users, use session ID
        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
        
        existing_spark = db.query(Spark).filter(
            Spark.artwork_id == artwork.id,
            Spark.session_id == session_id
        ).first()
    
    if existing_spark:
        # Remove spark (unlike)
        db.delete(existing_spark)
        db.commit()
        sparked = False
    else:
        # Add spark (like)
        new_spark = Spark(
            artwork_id=artwork.id,
            user_id=current_user.id if current_user else None,
            session_id=session_id if not current_user else None
        )
        db.add(new_spark)
        db.commit()
        sparked = True
    
    # Get updated count
    spark_count = db.query(Spark).filter(Spark.artwork_id == artwork.id).count()
    
    # Return JSON for AJAX or redirect for form submission
    if request.headers.get("accept") == "application/json":
        response = JSONResponse({
            "sparked": sparked,
            "spark_count": spark_count
        })
        if not current_user and not request.cookies.get("session_id"):
            response.set_cookie("session_id", session_id, max_age=31536000)  # 1 year
        return response
    else:
        response = RedirectResponse(url=f"/art/{username}/{slug}", status_code=302)
        if not current_user and not request.cookies.get("session_id"):
            response.set_cookie("session_id", session_id, max_age=31536000)
        return response


@router.post("/art/{username}/{slug}/comment")
async def add_comment(
    username: str,
    slug: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Add a comment to an artwork."""
    current_user = get_current_user_from_cookie(request, db)
    
    # Get the artwork
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    artwork = db.query(Artwork).filter(
        Artwork.slug == slug,
        Artwork.artist_id == user.id
    ).first()
    
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    if not artwork.allow_comments:
        raise HTTPException(status_code=403, detail="Comments are disabled for this artwork")
    
    # Get form data
    form = await request.form()
    content = form.get("content", "").strip()
    author_name = form.get("author_name", "").strip() if not current_user else None
    
    if not content:
        raise HTTPException(status_code=400, detail="Comment content is required")
    
    if not current_user and not author_name:
        raise HTTPException(status_code=400, detail="Name is required for anonymous comments")
    
    # Create comment
    new_comment = Comment(
        artwork_id=artwork.id,
        author_id=current_user.id if current_user else None,
        author_name=author_name,
        content=content
    )
    db.add(new_comment)
    db.commit()
    
    return RedirectResponse(url=f"/art/{username}/{slug}#comments", status_code=302)


@router.post("/art/{username}/{slug}/comment/{comment_id}/delete")
async def delete_comment(
    username: str,
    slug: str,
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a comment (owner or comment author only)."""
    current_user = get_current_user_from_cookie(request, db)
    
    if not current_user:
        raise HTTPException(status_code=403, detail="Must be logged in to delete comments")
    
    # Get the artwork
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    artwork = db.query(Artwork).filter(
        Artwork.slug == slug,
        Artwork.artist_id == user.id
    ).first()
    
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # Get the comment
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.artwork_id == artwork.id
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is comment author or artwork owner
    if current_user.id != comment.author_id and current_user.id != artwork.artist_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(comment)
    db.commit()
    
    return RedirectResponse(url=f"/art/{username}/{slug}#comments", status_code=302)

