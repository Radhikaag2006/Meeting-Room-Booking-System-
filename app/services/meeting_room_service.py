from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.meeting_room import MeetingRoom

from app.repositories.meeting_room_repository import MeetingRoomRepository

from app.schemas.meeting_room_schema import(MeetingRoomCreate,MeetingRoomUpdate)

class MeetingRoomService:

    #Create Meeting Room
    @staticmethod
    def create_room(db:Session, room_data: MeetingRoomCreate,current_user : User):

        #Duplicate room name check 
        existing_room = MeetingRoomRepository.get_room_by_name(db,current_user.office_id,room_data.room_name)
        if existing_room:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                                detail="Meeting room already exists.")
        
        # Capacity validation
        if room_data.capacity <= 0:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = "Capacity cannot be negative.")

         # Floor validation
        if room_data.floor < 0:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail = "Floor cannot be negative.")
        
        room = MeetingRoom(
            office_id =current_user.office_id,
            room_name = room_data.room_name,
            capacity = room_data.capacity,
            floor = room_data.floor
        )

        return MeetingRoomRepository.create_room(db,room)
    
    
    # Get All Rooms
    @staticmethod
    def get_all_rooms(
        db: Session,
        current_user: User,
    ):

        return MeetingRoomRepository.get_rooms_by_office(
            db,
            current_user.office_id,
        )

    
    # Get Room By ID
    @staticmethod
    def get_room_by_id(
        db: Session,
        room_id: int,
        current_user: User,
    ):

        room = MeetingRoomRepository.get_room_by_id(
            db,
            room_id,
        )

        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting room not found."
            )

        if room.office_id != current_user.office_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access rooms from another office."
            )

        return room

    
    # Update Room
    @staticmethod
    def update_room(
        db: Session,
        room_id: int,
        room_data: MeetingRoomUpdate,
        current_user: User,
    ):

        room = MeetingRoomService.get_room_by_id(
            db,
            room_id,
            current_user,
        )

        # Duplicate room name check
        if (
            room_data.room_name is not None
            and room_data.room_name != room.room_name
        ):

            existing_room = MeetingRoomRepository.get_room_by_name(
                db,
                current_user.office_id,
                room_data.room_name,
            )

            if existing_room:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Meeting room name already exists."
                )

            room.room_name = room_data.room_name

        if room_data.capacity is not None:

            if room_data.capacity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Capacity must be greater than zero."
                )

            room.capacity = room_data.capacity

        if room_data.floor is not None:

            if room_data.floor < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Floor cannot be negative."
                )

            room.floor = room_data.floor

        if room_data.status is not None:
            room.status = room_data.status

        return MeetingRoomRepository.update_room(
            db,
            room,
        )

    
    # Delete Room
    @staticmethod
    def delete_room(
        db: Session,
        room_id: int,
        current_user: User,
    ):

        room = MeetingRoomService.get_room_by_id(
            db,
            room_id,
            current_user,
        )

        MeetingRoomRepository.delete_room(
            db,
            room,
        )

        return {
            "message": "Meeting room deleted successfully."
        }
