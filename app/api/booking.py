from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_employee

from app.models.user import User

from app.schemas.booking_schema import (BookingCreate, BookingUpdate, BookingResponse)

from app.services.BookingService import BookingService

router = APIRouter(prefix = "/bookings", tags=["Bookings"])


#create booking 
@router.post("",response_model = BookingResponse, status_code = status.HTTP_201_CREATED)
def create_booking(booking_data : BookingCreate,
                   db:Session = Depends(get_db),
                   current_user :User = Depends(get_current_employee)):
    
    return BookingService.create_booking(db,booking_data,current_user)

#get my bookings 
@router.get("/my-meetings",response_model = List[BookingResponse])
def get_my_bookings(db:Session=Depends(get_db), current_user : User = Depends(get_current_employee)):
    return BookingService.get_my_bookings(db,current_user)

#get booking by id 
@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_employee),
):
    return BookingService.get_booking_by_id(
        db,
        booking_id,
        current_user,
    )

# Update Booking

@router.put(
    "/{booking_id}",
    response_model=BookingResponse,
)
def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_employee),
):
    return BookingService.update_booking(
        db,
        booking_id,
        booking_data,
        current_user,
    )

# Cancel Booking

@router.patch(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_employee),
):
    return BookingService.cancel_booking(
        db,
        booking_id,
        current_user,
    )