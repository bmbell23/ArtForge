"""Spark model - for likes/kudos on artworks and images."""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Spark(Base):
    """Spark model - represents a like/kudos on an artwork or specific image."""
    
    __tablename__ = "sparks"
    
    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("artwork_images.id"), nullable=True)  # Optional: spark on specific image
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for anonymous
    session_id = Column(String, nullable=True)  # For anonymous sparks (track by session)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    artwork = relationship("Artwork", back_populates="sparks")
    image = relationship("ArtworkImage", back_populates="sparks")
    user = relationship("User", back_populates="sparks")
    
    # Ensure one spark per user/session per artwork/image
    __table_args__ = (
        UniqueConstraint('artwork_id', 'user_id', name='unique_user_artwork_spark'),
        UniqueConstraint('artwork_id', 'session_id', name='unique_session_artwork_spark'),
    )
    
    def __repr__(self):
        return f"<Spark(artwork_id={self.artwork_id}, user_id={self.user_id})>"

