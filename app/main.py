from fastapi import FastAPI

from app.core.database import Base
from app.core.database import engine

from app.models.office import Office
from app.models.user import User
from app.api.auth import router as auth_router


app = FastAPI(title = "Meeting Room Booking System", version = "1.0.0")

Base.metadata.create_all(bind = engine)

@app.get("/")
def home():
    return {
        "message" : "Meeting Room Booking System API"
    }


