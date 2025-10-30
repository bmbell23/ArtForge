"""Comment model."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Comment(Base):
    """Comment model - for feedback on artworks."""
    
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for anonymous
    author_name = Column(String, nullable=True)  # For anonymous comments
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    artwork = relationship("Artwork", back_populates="comments")
    author = relationship("User", back_populates="comments")
    
    def __repr__(self):
        return f"<Comment(artwork_id={self.artwork_id}, author_name='{self.author_name}')>"

