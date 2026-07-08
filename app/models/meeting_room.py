from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base

class RoomStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class MeetingRoom(Base):

    __tablename__ = "meeting_rooms"

    room_id = Column(Integer, primary_key=True,index = True)
    office_id = Column(Integer, ForeignKey("offices.office_id"),nullable = False)
    room_name = Column(String(100),nullable=False)
    capacity = Column(Integer,nullable=False)
    floor = Column(Integer, nullable=False)
    status = Column(Enum(RoomStatus), default = RoomStatus.ACTIVE, nullable = False)
    created_at = Column(DateTime, default = datetime.utcnow)
    updated_at = Column(DateTime, default = datetime.utcnow, onupdate =datetime.utcnow)

    # relationship between offices and rooms 
    office = relationship("Office",back_populates="meeting_rooms")