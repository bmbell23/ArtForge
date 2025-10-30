"""Artwork and ArtworkImage models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Artwork(Base):
    """Artwork model - represents an art project."""
    
    __tablename__ = "artworks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    artist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=True)
    allow_comments = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    artist = relationship("User", back_populates="artworks")
    images = relationship("ArtworkImage", back_populates="artwork", cascade="all, delete-orphan", order_by="ArtworkImage.order")
    comments = relationship("Comment", back_populates="artwork", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="artwork_tags", back_populates="artworks")
    series_associations = relationship("ArtworkSeries", back_populates="artwork", cascade="all, delete-orphan")
    sparks = relationship("Spark", back_populates="artwork", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Artwork(title='{self.title}', artist_id={self.artist_id})>"


class ArtworkImage(Base):
    """ArtworkImage model - represents individual images in an artwork."""
    
    __tablename__ = "artwork_images"
    
    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    filename = Column(String, nullable=False)  # Stored filename
    original_filename = Column(String, nullable=True)  # Original upload filename
    caption = Column(Text, nullable=True)
    order = Column(Integer, default=0)  # Order in the artwork (0 = main image)
    is_primary = Column(Boolean, default=False)  # Main display image
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    artwork = relationship("Artwork", back_populates="images")
    sparks = relationship("Spark", back_populates="image", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ArtworkImage(artwork_id={self.artwork_id}, filename='{self.filename}')>"

