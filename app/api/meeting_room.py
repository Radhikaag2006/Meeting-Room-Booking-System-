from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_office_admin, get_current_employee

from app.models.user import User

from app.schemas.meeting_room_schema import ( MeetingRoomCreate, MeetingRoomUpdate, MeetingRoomResponse)

from app.services.meeting_room_service import MeetingRoomService

router = APIRouter(
    prefix="/meeting-rooms",
    tags=["Meeting Room Management"]
)

# Create meeting room 
@router.post("", response_model = MeetingRoomResponse, status_code = status.HTTP_201_CREATED)
def create_room(room_data : MeetingRoomCreate,
                db:Session = Depends(get_db),
                current_user: User = Depends(get_current_office_admin)):
    return MeetingRoomService.create_room(db, room_data, current_user)

#  get all meeting rooms 
@router.get("",response_model = list[MeetingRoomResponse])
def get_all_rooms(db:Session = Depends(get_db), current_user :User = Depends(get_current_office_admin)):
    return MeetingRoomService.get_all_rooms(db, current_user)

# get bookable rooms in the caller's own office (employee-facing; must be
# declared before "/{room_id}" so it isn't swallowed by that route)
@router.get("/available", response_model = list[MeetingRoomResponse])
def get_available_rooms(db:Session = Depends(get_db), current_user :User = Depends(get_current_employee)):
    return MeetingRoomService.get_available_rooms(db, current_user)

# getting meeting room by ID
@router.get("/{room_id}", response_model = MeetingRoomResponse)
def get_room_by_id(room_id: int,
                   db:Session = Depends(get_db), current_user : User = Depends(get_current_office_admin)):
    return MeetingRoomService.get_room_by_id(db,room_id,current_user)

#Update Meeting Rooms 
@router.put("/{room_id}", response_model = MeetingRoomResponse)
def update_room(room_id: int,room_data : MeetingRoomUpdate,
                db:Session=Depends(get_db), current_user : User = Depends(get_current_office_admin)):
    
    return MeetingRoomService.update_room(db, room_id, room_data, current_user)

# Deleteing Meeting Room 
@router.delete("/{room_id}")
def delete_room(room_id : int, db:Session = Depends(get_db), current_user  : User = Depends(get_current_office_admin)):
    return MeetingRoomService.delete_room(db, room_id, current_user)