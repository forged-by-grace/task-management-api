from app.utils.init_db import SessionLocal, engine


# SQLALCHEMY dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
