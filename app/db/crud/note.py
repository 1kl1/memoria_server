from sqlalchemy.orm import Session
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate

def get_note(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()

def get_notes_by_collection(db: Session, collection_id: int, skip: int = 0, limit: int = 100):
    return db.query(Note).filter(Note.collection_id == collection_id).offset(skip).limit(limit).all()

def create_collection_note(db: Session, note: NoteCreate, collection_id: int):
    db_note = Note(**note.model_dump(), collection_id=collection_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(db: Session, db_note: Note, note_in: NoteUpdate):
    note_data = note_in.model_dump(exclude_unset=True) 
    for key, value in note_data.items():
        setattr(db_note, key, value)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note:
        db.delete(db_note)
        db.commit()
    return db_note

def get_notes_by_uuid(db: Session, uuid: str):
    return db.query(Note).filter(Note.node_uuid == uuid).all()

def delete_notes_by_uuid(db: Session, uuid: str):
    db_notes = db.query(Note).filter(Note.node_uuid == uuid).all()
    for db_note in db_notes:
        db.delete(db_note)
    db.commit()
    return db_notes