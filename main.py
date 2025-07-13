from fastapi import FastAPI
from database import Base, engine
from routers import user, file

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(file.router)
