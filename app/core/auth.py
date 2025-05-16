from firebase_admin import auth
from app.db.crud.user import get_user_by_firebase_uid, create_user
from app.schemas.user import UserCreate, User
from app.core.security import create_access_token, create_refresh_token
from app.schemas.auth import Token
from datetime import timedelta
from sqlalchemy.orm import Session
from app.config import settings
from typing import Tuple, Dict, Any, Optional
import requests
import json



async def authenticate_firebase_user(
    db: Session, email: str, password: str
) -> Tuple[User, Token]:
    """
    Firebase Authentication REST API를 사용하여 이메일/비밀번호 인증 후
    데이터베이스에서 사용자 정보를 조회하고 토큰 생성
    """
    try:
        
        auth_data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(settings.FIREBASE_AUTH_URL, json=auth_data)
        response.raise_for_status()  
        
        firebase_response = response.json()
        firebase_uid = firebase_response.get("localId")
        
        if not firebase_uid:
            raise Exception("Firebase 인증 실패")
        
        
        user = get_user_by_firebase_uid(db, firebase_uid)
        
        # 데이터베이스에 사용자 정보가 없으면 생성
        if not user:
            user_data = UserCreate(
                email=email,
                firebase_uid=firebase_uid
            )
            user = create_user(db, user_data)
        
        # JWT 토큰 생성
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        tokens = create_tokens(user.email, firebase_uid, access_token_expires)
        
        return user, tokens
    except requests.exceptions.RequestException as e:
        raise Exception(f"Firebase 인증 요청 실패: {str(e)}")
    except Exception as e:
        raise Exception(f"인증 처리 중 오류 발생: {str(e)}")

def create_tokens(email: str, uid: str, access_token_expires: Optional[timedelta] = None) -> Token:
    """
    액세스 토큰과 리프레시 토큰 생성
    """
    access_token = create_access_token(
        data={"sub": email, "uid": uid},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": email, "uid": uid}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
