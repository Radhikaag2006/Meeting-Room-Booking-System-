# this contains the databse schema for the user tabloe 

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
import enum
from sqlalchemy import Enum
from sqlalchemy.orm import relationship


from app.core.database import Base

class UserRole(enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    OFFICE_ADMIN = "OFFICE_ADMIN"
    EMPLOYEE = "EMPLOYEE"

class UserStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class User(Base):

    __tablename__ = "users"

    user_id= Column(Integer , primary_key = True, index = True)
    first_name = Column(String(200), nullable = False, unique = False)
    last_name = Column(String(200), nullable=False)
    office_id = Column(Integer , ForeignKey("offices.office_id"),
                       nullable = True)
    email = Column(String(100), nullable = False, unique = True, index = True)
    password_hash = Column(String(255),nullable=False) # this stores the hashed password of user
    role = Column(Enum(UserRole), nullable = False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(DateTime, default = datetime.utcnow)
    updated_at = Column(DateTime, default = datetime.utcnow, onupdate = datetime.utcnow)
    must_change_password = Column(Boolean, default = True)  # so that user can change his password later on



    # creating many to one relationship between office and users because one office can have many users
    office = relationship("Office", back_populates="users")
