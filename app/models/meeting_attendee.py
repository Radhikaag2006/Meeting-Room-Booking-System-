from sqlalchemy import (Column, Integer, Date, Time, Enum, ForeignKey,DateTime)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


from app.core.database import Base

class AttendanceStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"

class MeetingAttendee(Base):

    __tablename__ = "meeting_attendees"
    meeting_attendee_id = Column(Integer, primary_key = True, index = True)
    booking_id = Column( Integer,ForeignKey("bookings.booking_id"),nullable=False)
    employee_id = Column(Integer,ForeignKey("users.user_id"),nullable=False)
    attendance_status = Column(Enum(AttendanceStatus),default=AttendanceStatus.PENDING,nullable=False)
    created_at = Column(DateTime,default=datetime.utcnow)

    # ---------------- Relationships ----------------

    booking = relationship("Booking",back_populates="attendees")

    employee = relationship("User",back_populates="meeting_attendances")


