"""Series model and association table."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Series(Base):
    """Series model for grouping related artworks."""
    
    __tablename__ = "series"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationships
    artwork_associations = relationship("ArtworkSeries", back_populates="series", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Series(name='{self.name}')>"


class ArtworkSeries(Base):
    """Association table for artworks in a series with position."""
    
    __tablename__ = "artwork_series"
    
    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False)
    position = Column(Integer, nullable=False)  # Position in the series
    
    # Relationships
    artwork = relationship("Artwork", back_populates="series_associations")
    series = relationship("Series", back_populates="artwork_associations")
    
    def __repr__(self):
        return f"<ArtworkSeries(artwork_id={self.artwork_id}, series_id={self.series_id}, position={self.position})>"

