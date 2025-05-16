from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any, List
from app.schemas.collection import Collection, CollectionCreate
from app.db.session import get_db
from app.db.crud.collection import create_collection, get_collection, get_user_collections
from app.dependencies import get_current_user
from app.db.crud.user import get_user_by_firebase_uid
from app.schemas.auth import TokenData
from app.core.exceptions import NotFound

router = APIRouter(prefix="/collection", tags=["collection"])

@router.get("/", response_model=List[Collection])
async def read_current_user_collections(
    skip: int = 0,
    limit: int = 100,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    현재 로그인한 사용자의 collection 목록 조회 (인증 필요)
    """
    user = get_user_by_firebase_uid(db, token_data.uid)
    if not user:
        raise NotFound("User not found")
    
    return get_user_collections(db, user.id, skip=skip, limit=limit)


@router.post("/create", response_model=Collection)
async def create_current_user_collection(
    post_data: CollectionCreate,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    현재 로그인한 사용자의 collection 생성
    """
    user = get_user_by_firebase_uid(db, token_data.uid)
    if not user:
        raise NotFound("User not found")
    
    post = create_collection(db, post_data, user.id)
    return post




# @router.get("/collections/{collection_id}", response_model=Collection)
# async def read_post(
#     collection_id: int,
#     token_data: TokenData = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ) -> Any:
#     """
#     특정 collection 조회 (인증 필요)
#     """
#     post = get_collection(db, collection_id)
#     if not post:
#         raise NotFound(f"Post with ID {collection_id} not found")
#     return post