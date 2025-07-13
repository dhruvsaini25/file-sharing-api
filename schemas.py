from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_ops: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class FileOut(BaseModel):
    id: int
    filename: str

    class Config:
        from_attributes = True

