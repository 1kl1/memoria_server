from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from app.schemas.user import User, UserUpdate
from app.schemas.collection import Collection, CollectionCreate
from app.db.session import get_db
from app.db.crud.user import get_user_by_firebase_uid, update_user
from app.db.crud.collection import get_user_collections, create_collection
from app.dependencies import get_current_user
from app.schemas.auth import TokenData
from app.core.exceptions import NotFound, PermissionDenied
from firebase_admin import auth

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
async def read_current_user(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    현재 로그인한 사용자 정보 조회
    """
    user = get_user_by_firebase_uid(db, token_data.uid)
    if not user:
        raise NotFound("User not found")
    return user

@router.put("/me", response_model=User)
async def update_current_user(
    user_data: UserUpdate,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    현재 로그인한 사용자 정보 업데이트
    """
    user = get_user_by_firebase_uid(db, token_data.uid)
    if not user:
        raise NotFound("User not found")
    
    # Firebase에서도 사용자 정보 업데이트
    if user_data.display_name:
        auth.update_user(
            token_data.uid,
            display_name=user_data.display_name
        )
    
    # 데이터베이스 사용자 정보 업데이트
    updated_user = update_user(db, user, user_data)
    return updated_user
