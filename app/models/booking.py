from sqlalchemy import(Column, String, Date, Integer, Time, DateTime, ForeignKey, Enum)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base

class BookingStatus(enum.Enum):
    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class Booking(Base):

    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index = True)
    meeting_title = Column(String(200), nullable = False)
    description = Column(String(500), nullable = True)
    room_id = Column(Integer, ForeignKey("meeting_rooms.room_id"), nullable = False)
    organizer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    meeting_date = Column(Date,nullable=False)
    start_time= Column(Time,nullable=False)
    end_time = Column(Time,nullable=False)
    status = Column(Enum(BookingStatus), default = BookingStatus.SCHEDULED, nullable = False)
    created_at = Column(DateTime, default = datetime.utcnow)
    updated_at = Column(DateTime, default =  datetime.utcnow, onupdate = datetime.utcnow)

    # defining the relationships 
    room = relationship("MeetingRoom", back_populates = "bookings")
    organizer = relationship("User", back_populates="organized_bookings")
    attendees = relationship("MeetingAttendee", back_populates="booking", cascade="all,delete-orphan")
    
