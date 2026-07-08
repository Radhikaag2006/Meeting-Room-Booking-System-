from sqlalchemy.orm import Session
from app.models.meeting_room import MeetingRoom

class MeetingRoomRepository:

    # create meeting room 
    @staticmethod 
    def create_room(db:Session,room:MeetingRoom):
        db.add(room)
        db.commit()
        db.refresh(room)

        return room
    
    # get room by id
    @staticmethod 
    def get_room_by_id(db:Session, room_id: int):
        return (db.query(MeetingRoom).filter(MeetingRoom.room_id == room_id).first())
    
    # get room by name (within the office)
    @staticmethod 
    def get_room_by_name(db:Session, office_id: int, room_name : str):
        return (db.query(MeetingRoom).filter(MeetingRoom.office_id == office_id, MeetingRoom.room_name == room_name).first())
    
    #get all rooms of an office 
    @staticmethod
    def get_rooms_by_office(db:Session,office_id: int):
        return (db.query(MeetingRoom).filter(MeetingRoom.office_id ==  office_id).all())
    
    #Update Room
    @staticmethod
    def update_room(db:Session, room: MeetingRoom):
        db.commit()
        db.refresh(room)

        return room
    
    # Delete Room
    @staticmethod
    def delete_room(db:Session, room:MeetingRoom):
        db.delete(room)
        db.commit()
        

        