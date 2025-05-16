from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field, Json
from typing import List, Optional,Dict, Any

class NoteBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    node_uuid: Optional[str] = None
    created_at: Optional[datetime] = None

class NoteCreate(NoteBase):
    title: str
    content: str
    summary: str
    node_uuid: str

class NoteUpdate(NoteBase):
    pass

class NoteInDBBase(NoteBase):
    id: int
    collection_id: int

    class Config:
        from_attributes = True 

class Note(NoteInDBBase):
    pass

class NoteInDB(NoteInDBBase):
    pass



