from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from app.db.base import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    node_uuid = Column(String, index = True)
    content = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=text("timezone('Asia/Seoul', now())"))
    collection_id = Column(Integer, ForeignKey("collections.id"))

    collection = relationship("Collection", back_populates="notes")
