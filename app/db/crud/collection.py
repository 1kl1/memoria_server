from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.crud.base import CRUDBase
from app.models.collection import Collection
from app.schemas.collection import CollectionCreate, CollectionUpdate

class CRUDPost(CRUDBase[Collection, CollectionCreate, CollectionUpdate]):
    def create_with_author(
        self, db: Session, *, obj_in: CollectionCreate, author_id: int
    ) -> Collection:
        """
        작성자 ID와 함께 게시물 생성
        """
        post_data = obj_in.dict()
        db_obj = Collection(**post_data, author_id=author_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_author(
        self, db: Session, author_id: int, skip: int = 0, limit: int = 100
    ) -> List[Collection]:
        """
        작성자별 게시물 조회
        """
        return (
            db.query(Collection)
            .filter(Collection.author_id == author_id)
            .offset(skip)
            .limit(limit)
            .all()
        )



collection_crud = CRUDPost(Collection)

def get_collection(db: Session, collection_id: int) -> Optional[Collection]:
    """
    ID로 게시물 조회
    """
    return collection_crud.get(db, collection_id)

def get_collections(db: Session, skip: int = 0, limit: int = 100) -> List[Collection]:
    """
    게시물 목록 조회
    """
    return collection_crud.get_multi(db, skip=skip, limit=limit)

def create_collection(db: Session, post_data: CollectionCreate, author_id: int) -> Collection:
    """
    게시물 생성
    """
    return collection_crud.create_with_author(db, obj_in=post_data, author_id=author_id)

def update_collection(db: Session, post: Collection, post_data: CollectionUpdate) -> Collection:
    """
    게시물 업데이트
    """
    return collection_crud.update(db, db_obj=post, obj_in=post_data)

def delete_collection(db: Session, post_id: int) -> Collection:
    """
    게시물 삭제
    """
    return collection_crud.remove(db, id=post_id)

def get_user_collections(db: Session, author_id: int, skip: int = 0, limit: int = 100) -> List[Collection]:
    """
    사용자별 게시물 조회
    """
    return collection_crud.get_by_author(db, author_id, skip=skip, limit=limit)

def get_collection_by_id_and_author(db: Session, collection_id: int, author_id: int) -> Optional[Collection]:
    """
    ID와 작성자 ID로 게시물 조회
    """
    return db.query(Collection).filter(Collection.id == collection_id, Collection.author_id == author_id).first()