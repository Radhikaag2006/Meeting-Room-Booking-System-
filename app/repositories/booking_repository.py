# it is used  to interact with the database 
# it does not perform busineess logic 

from datetime import date, time
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.meeting_attendee import MeetingAttendee
from app.models.meeting_attendee import MeetingAttendee



class BookingRepository:

    @staticmethod 
    def create_booking(db:Session, booking:Booking):
        db.add(booking)
        db.flush() #generates booking without commiting
        return booking
    
    @staticmethod
    def create_meeting_attendee(db:Session,meeting_attendee : MeetingAttendee):
        db.add(meeting_attendee)

    @staticmethod 
    def commit(db:Session):
        db.commit()

    @staticmethod
    def rollback(db:Session):
        db.rollback()
    
    @staticmethod 
    def refresh(db:Session, booking:Booking):
        db.refresh(booking)

    @staticmethod 
    def get_booking_by_id(db:Session, booking_id:int):
        return(db.query(Booking).filter(Booking.booking_id == booking_id).first())
    
    @staticmethod 
    def get_bookings_by_room_and_date(db:Session, room_id: int, meeting_date : date):
        return (db.query(Booking).filter(Booking.room_id == room_id, Booking.meeting_date == meeting_date).all())
    

    @staticmethod 
    def update_booking(db:Session,booking : Booking):
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod 
    def delete_booking(db:Session, booking: Booking):
        db.delete()
        db.commit()
    
    @staticmethod 
    def get_all_bookings(db:Session):
        return db.query(Booking).all()
    
    #Get all the bookings for current employee
    @staticmethod 
    def get_my_bookings(db:Session, employee_id : int):
        return (db.query(Booking).join(MeetingAttendee).filter(MeetingAttendee.employee_id == employee_id).all())