"""Tag model and association table."""

from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

# Association table for many-to-many relationship between artworks and tags
artwork_tags = Table(
    'artwork_tags',
    Base.metadata,
    Column('artwork_id', Integer, ForeignKey('artworks.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Tag(Base):
    """Tag model for categorizing artworks."""
    
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    
    # Relationships
    artworks = relationship("Artwork", secondary=artwork_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(name='{self.name}')>"

