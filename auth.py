from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict, expires_minutes=30):
    data.update({"exp": datetime.utcnow() + timedelta(minutes=expires_minutes)})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)