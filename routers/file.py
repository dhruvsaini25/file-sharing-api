from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Header
import models, utils
from sqlalchemy.orm import Session
from database import SessionLocal
import shutil, os
from jose import jwt, JWTError

router = APIRouter()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Header(...)):
    try:
        data = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        return data
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/upload")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user["is_ops"]:
        raise HTTPException(status_code=403, detail="Only Ops can upload")
    ext = file.filename.split(".")[-1]
    if ext not in ["docx", "xlsx", "pptx"]:
        raise HTTPException(status_code=400, detail="File type not allowed")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    db_file = models.File(filename=file.filename, uploader_id=user["user_id"])
    db.add(db_file)
    db.commit()
    return {"message": "Upload successful"}

@router.get("/files")
def list_files(db: Session = Depends(get_db), user=Depends(get_current_user)):
    files = db.query(models.File).all()
    return files

@router.get("/download-file/{file_id}")
def get_download_link(file_id: int, user=Depends(get_current_user)):
    if user["is_ops"]:
        raise HTTPException(status_code=403, detail="Only clients allowed")
    token = utils.create_token({"file_id": file_id, "user_id": user["user_id"]}, expires_minutes=10)
    return {"download_link": f"/secure-download/{token}"}

@router.get("/secure-download/{token}")
def secure_download(token: str):
    try:
        data = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        file_id = data["file_id"]
        filename = f"./uploads/{file_id}.docx"  # for now assume docx
        return {"message": f"Would download file {file_id}"}
    except:
        raise HTTPException(status_code=403, detail="Invalid or expired link")
