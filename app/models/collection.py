from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql import text
from app.db.base import Base


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=text("timezone('Asia/Seoul', now())"))
    updated_at = Column(DateTime(timezone=True), server_default=text("timezone('Asia/Seoul', now())"))

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="collections")

    notes = relationship("Note", back_populates="collection", cascade="all, delete-orphan")
