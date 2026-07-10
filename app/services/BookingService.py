# most importat business module - contains all the core logic 
# this will check whether the 
#  meeting overlap or not 
# is room available 
# who is the attendee 

from datetime import date 
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserStatus
from app.models.booking import Booking, BookingStatus
from app.models.meeting_attendee import(MeetingAttendee, AttendanceStatus)
from app.models.meeting_room import RoomStatus
from app.schemas.booking_schema import BookingCreate
from app.repositories.booking_repository import BookingRepository
from app.repositories.meeting_room_repository import  MeetingRoomRepository
from app.repositories.user_repository import UserRepository


class BookingService:

    @staticmethod
    def create_booking(db:Session, booking_data: BookingCreate, current_user: User):

        # validating meeting date

        if booking_data.meeting_date < date.today():
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                 detail = "Meeting date cannot be in the past.")
        
        if len(booking_data.attendees) != len(set(booking_data.attendees)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate attendees are not allowed.",
    )
        #validate time
        if booking_data.start_time >= booking_data.end_time:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST, detail ="End time must be after the start time.")
        
        #validate meeting room 
        room = MeetingRoomRepository.get_room_by_id(db,booking_data.room_id)
        if room  is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail = "Meeting room not found.")
        
        if room.status != RoomStatus.ACTIVE:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Meeting room is inactive.")
        

        # room must belong to the same office 
        if room.office_id != current_user.office_id:
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
                                detail = "You cannot book room from another office.")
        
    
        #validate employees
        employees = UserRepository.get_user_by_ids(db,booking_data.attendees)
        if len(employees) != len(booking_data.attendees):
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail = "One or more employees do not exist.")
        
        for employee in employees:

            if employee.role.value != "EMPLOYEE":
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"{employee.first_name} is not an employee.")
        

            if employee.status != UserStatus.ACTIVE:
                raise  HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                     detail = f"{employee.first_name} is inactive.")
            
            if employee.office_id != current_user.office_id:
                raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Employees from another office  cannot be invited.")

        # validate capacity 
        attendee_count = len(booking_data.attendees)

        #organizer should occupy one seat 
        if current_user.user_id not in booking_data.attendees:
            attendee_count += 1
        
        if attendee_count > room.capacity :
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = "Room capaccity exceeded.")
        
        # Overlap Validation 
        existing_booking = (BookingRepository.get_bookings_by_room_and_date(db, room.room_id, booking_data.meeting_date))

        for existing_booking in existing_booking:
            
            if existing_booking.status == BookingStatus.CANCELLED:
                continue
            overlap =(booking_data.start_time < existing_booking.end_time and booking_data.end_time > existing_booking.start_time)

            if overlap :
                raise HTTPException(status_code = status.HTTP_409_CONFLICT,
                                    detail = "Meeting room is already booked for this time slot.")
        
        # Create Booking 
        booking = Booking(meeting_title= booking_data.meeting_title, 
                          description = booking_data.description,
                          room_id = booking_data.room_id,
                          organizer_id = current_user.user_id,
                          meeting_date = booking_data.meeting_date,
                          start_time = booking_data.start_time,
                          end_time = booking_data.end_time)
        
        try:

             BookingRepository.create_booking(db,booking)

             # organizer automatically becomes the attendee
             organizer = MeetingAttendee(
                 booking_id = booking.booking_id,
                 employee_id = current_user.user_id,
                 attendance_status = AttendanceStatus.ACCEPTED)
             
             BookingRepository.create_meeting_attendee(db,organizer)

             #Add invited employees
             for employee_id in booking_data.attendees: 
                 
                 if employee_id == current_user.user_id:
                     continue
                 
                 attendee = MeetingAttendee(
                     booking_id = booking.booking_id,
                     employee_id = employee_id, 
                     attendance_status =AttendanceStatus.PENDING
                 )

                 BookingRepository.create_meeting_attendee(db,attendee)
             BookingRepository.commit(db)
             BookingRepository.refresh(db,booking)
             return booking
        
        except Exception:
            BookingRepository.rollback(db)
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail = "Unable to create booking.")
    @staticmethod
    def get_my_bookings(db:Session, current_user : User):
        return BookingRepository.get_my_bookings(db, current_user.user_id)
    
    #Get Booking by ID
    @staticmethod
    def get_booking_by_id(db:Session, booking_id: int, current_user : User):
        booking = BookingRepository.get_booking_by_id(db, booking_id)
        if booking is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail = "Booking not found")
         
    
        #Organizer can view 
        if booking.organizer_id == current_user.user_id:
                                return booking
        
        #Checkk whether employee is an attendee
        for attendee in booking.attendees:
             
             if attendee.employee_id == current_user.user_id:
                  return booking
        
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You are not authorized to view this booking.")
        
        #Update Booking
    @staticmethod
    def update_booking(
        db: Session,
        booking_id: int,
        booking_data,
        current_user: User,
    ):

            booking = BookingRepository.get_booking_by_id(
                db,
                booking_id,
            )

            if booking is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Booking not found.",
                )

            if booking.organizer_id != current_user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the organizer can update the booking.",
                )

            if booking_data.meeting_title is not None:
                booking.meeting_title = booking_data.meeting_title

            if booking_data.description is not None:
                booking.description = booking_data.description

            if booking_data.meeting_date is not None:
                booking.meeting_date = booking_data.meeting_date

            if booking_data.start_time is not None:
                booking.start_time = booking_data.start_time

            if booking_data.end_time is not None:
                booking.end_time = booking_data.end_time

            if booking_data.status is not None:
                booking.status = booking_data.status

            if booking_data.room_id is not None:
                room = MeetingRoomRepository.get_room_by_id(
                    db,
                    booking_data.room_id,
                )

                if room is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Meeting room not found.",
                    )

                booking.room_id = booking_data.room_id

            return BookingRepository.update_booking(
                db,
                booking,
            )

    #cancel bookings 
    @staticmethod
    def cancel_booking(
        db: Session,
        booking_id: int,
        current_user: User,
    ):

        booking = BookingRepository.get_booking_by_id(
            db,
            booking_id,
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if booking.organizer_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the organizer can cancel the booking.",
            )

        booking.status = BookingStatus.CANCELLED

        return BookingRepository.update_booking(
            db,
            booking,
        )