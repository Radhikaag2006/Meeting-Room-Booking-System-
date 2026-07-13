from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.meeting_room import RoomStatus

#create meeting rooms

class MeetingRoomCreate(BaseModel):
    room_name : str
    capacity: int
    floor:int

#Update Meeting Rooms 
class MeetingRoomUpdate(BaseModel):
    room_name :Optional[str] = None
    capacity : Optional[int] = None
    floor : Optional[int] = None
    status : Optional[RoomStatus] = None

# Response Schema
class MeetingRoomResponse(BaseModel):
    room_id : int
    office_id: int
    room_name : str
    capacity : int
    floor : int
    status : RoomStatus

    model_config = ConfigDict(from_attributes=  True)
