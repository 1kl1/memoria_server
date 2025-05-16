from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.protected import collections, users, ai, nodes as protected_nodes_router, notes as protected_notes_router
from app.config import settings
from app.api import auth, nodes
from app.db.base import Base, engine, driver
import firebase_admin
from firebase_admin import credentials
import os

def startup_event():
    if not firebase_admin._apps:
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if not os.path.exists(cred_path):
            print(f"Firebase credentials file not found at {cred_path}")
        else:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully")
    else:
        print("Firebase already initialized")
    
def shutdown_event():
    driver.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_event()
    yield
    shutdown_event()

# SQLAlchemy 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(collections.router, prefix=settings.API_V1_STR)
app.include_router(nodes.router, prefix=settings.API_V1_STR)
app.include_router(protected_notes_router.router, prefix=settings.API_V1_STR, tags=["Protected Notes"]) 
app.include_router(ai.router, prefix=settings.API_V1_STR)
app.include_router(protected_nodes_router.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Firebase FastAPI Auth"}

@app.get("/health-check")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
