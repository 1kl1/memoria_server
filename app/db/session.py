from app.db.base import SessionLocal, driver

def get_db():
    """
    데이터베이스 세션을 제공하는 의존성 함수
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_neo4j():
    """
    graph db 데이터베이스 세션을 제공하는 의존성 함수
    """
    neo4j = driver.session()
    try:
        yield neo4j
    finally:
        neo4j.close()