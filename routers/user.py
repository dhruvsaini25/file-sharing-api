from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas, utils

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email exists")
    db_user = models.User(
        email=user.email,
        hashed_password=utils.hash_password(user.password),
        is_ops=user.is_ops,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Signup successful. Please verify email (mocked)", "verification_link": f"/verify/{db_user.id}"}

@router.get("/verify/{user_id}")
def verify_email(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.commit()
    return {"message": "Email verified!"}

@router.post("/login")
def login(creds: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == creds.email).first()
    if not user or not utils.verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid creds")
    return {"token": utils.create_token({"user_id": user.id, "is_ops": user.is_ops})}
