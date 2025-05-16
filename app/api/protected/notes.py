from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.exceptions import NotFound
from app.db import crud
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.collection import Collection as DBCollection
from app.db.crud.user import get_user_by_firebase_uid
from app.schemas.note import Note, NoteCreate

router = APIRouter()

@router.post("/collections/{collection_id}/notes", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note_for_collection(
    collection_id: int,
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create a new note within a specific collection.
    """
    db_collection = crud.collection.get_collection(db, collection_id=collection_id)
    if not db_collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or you don't have permission to access it.",
        )
    return crud.note.create_collection_note(db=db, note=note, collection_id=collection_id)


@router.delete("/notes/{note_id}", response_model=Note)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    token_data: User = Depends(get_current_user),
) -> Any:
    """
    Delete a note.
    The note must belong to a collection owned by the current user.
    """
    db_note = crud.note.get_note(db=db, note_id=note_id)
    if not db_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    user = get_user_by_firebase_uid(db, token_data.uid)
    if not user:
        raise NotFound("User not found")

    db_collection = crud.collection.get_collection_by_id_and_author(db, collection_id=db_note.collection_id, author_id=user.id)
    if not db_collection:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this note.",
        )
    
    deleted_note = crud.note.delete_note(db=db, note_id=note_id)
    if not deleted_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found for deletion")
    return deleted_note


@router.delete("/notes")
def delete_notes_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
    token_data: User = Depends(get_current_user),
) -> Any:
    """
    Delete notes by UUID.
    The notes must belong to a collection owned by the current user.
    """
    db_notes = crud.note.get_notes_by_uuid(db=db, uuid=uuid)
    if not db_notes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notes not found")
    
    user = get_user_by_firebase_uid(db, token_data.uid)
    if not user:
        raise NotFound("User not found")

    for db_note in db_notes:
        db_collection = crud.collection.get_collection_by_id_and_author(db, collection_id=db_note.collection_id, author_id=user.id)
        if not db_collection:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this note.",
            )
    
    deleted_notes = crud.note.delete_notes_by_uuid(db=db, uuid=uuid)
    if not deleted_notes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notes not found for deletion")
    return None