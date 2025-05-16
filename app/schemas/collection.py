from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.note import Note # Import Note schema

class CollectionBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
class CollectionCreate(CollectionBase):
    title: str
    description: str

class CollectionUpdate(CollectionBase):
    pass

class CollectionInDBBase(CollectionBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Collection(CollectionInDBBase):
    notes: List[Note] = [] 
