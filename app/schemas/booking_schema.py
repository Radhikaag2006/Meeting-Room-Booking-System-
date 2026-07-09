from datetime import date, time
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.booking import BookingStatus

class BookingCreate(BaseModel):
    meeting_title :str
    description : Optional[str] = None
    room_id : int
    meeting_date : date
    start_time : time
    end_time : time
    attendees : List[int]

class BookingUpdate(BaseModel):
    meeting_title : Optional[str] = None
    description : Optional[str] = None
    room_id : Optional[int] = None
    meeting_date : Optional[date] = None
    start_time : Optional[time] = None
    end_time : Optional[time] = None
    status : Optional[BookingStatus] = None

class BookingResponse(BaseModel):
    booking_id : int
    meeting_title : str
    description : Optional[str]
    room_id : int
    meeting_date : date
    organizer_id : int
    start_time : time
    end_time : time
    status : BookingStatus
    model_config = ConfigDict(from_attribbutes = True)

# Meeting attendee response 
class MeetingAttendeeResponse(BaseModel):
    employee_id : int
    attendance_status : str
    model_config = ConfigDict(from_attributes = True)
