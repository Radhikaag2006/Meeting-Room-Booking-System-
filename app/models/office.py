from sqlalchemy import Column, Integer,String, DateTime,  ForeignKey
from datetime import datetime

from app.core.database import Base
from sqlalchemy.orm import relationship

class Office(Base):
    __tablename__ = "offices"

    office_id = Column(Integer, primary_key=True, index = True)
    office_name = Column(String(200), nullable = False, unique = True)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable = False)
    state = Column(String(100), nullable = False)
    country = Column(String(200), nullable = False)
    status = Column(String(20), default="Active") # this means whether the office is functional or not 
    created_at = Column(DateTime, default = datetime.utcnow)
    updated_at = Column(DateTime,default = datetime.utcnow, onupdate = datetime.utcnow)


    # creating relaionship vetween office and users 
    users = relationship("User",back_populates = "office")

    # one to many relationship with meeting rooms 
    meeting_rooms = relationship("MeetingRoom",back_populates = "office", cascade = "all, delete-orphan")
