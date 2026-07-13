from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base
from app.core.database import engine

from app.models.office import Office
from app.models.user import User
from app.models import booking
from app.models.meeting_attendee import MeetingAttendee
from app.models.meeting_room import MeetingRoom
from app.api.auth import router as auth_router
from app.api.offices import router as office_router 
from app.api.office_admin import router as office_admin_router
from app.api.employee import router as employee_router
from app.api.meeting_room import router as meeting_room_router
from app.api.booking import router as booking_router




app = FastAPI(title = "Meeting Room Booking System", version = "1.0.0")

#CORS middleware added
# allows the static frontend (served from a different origin/port) to call this API with fetch()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind = engine)
app.include_router(auth_router)
app.include_router(office_router)
app.include_router(office_admin_router)
app.include_router(employee_router)
app.include_router(meeting_room_router)
app.include_router(booking_router)

@app.get("/")
def home():
    return {
        "message" : "Meeting Room Booking System API"
    }





