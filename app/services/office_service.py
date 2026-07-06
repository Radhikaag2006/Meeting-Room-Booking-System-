from fastapi import HTTPException , status
from sqlalchemy.orm import Session 

from app.models.office import Office
from app.repositories.office_repository import OfficeRepository
from app.schemas.office_schema import OfficeCreate
from app.schemas.office_schema import OfficeUpdate

class OfficeService:

    @staticmethod 
    def create_office(db:Session, office_data: OfficeCreate):
        existing_office = OfficeRepository.get_office_by_name(db,office_data.office_name)
        if existing_office:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT, 
                detail = "Office already exists.")
        
        office = Office(
            office_name = office_data.office_name,
            address = office_data.address,
            city = office_data.city,
            state = office_data.state,
            country = office_data.country

        )

        return OfficeRepository.create_office(db,office)
    
    @staticmethod
    def get_all_offices(db:Session):
        return OfficeRepository.get_all_offices(db)
    
    @staticmethod
    def get_office_by_id(db:Session, office_id:int):

        office = OfficeRepository.get_office_by_id(db, office_id)

        if office is None:
             raise HTTPException(
                 status_code = status.HTTP_404_NOT_FOUND,
                 detail = "Office not found.")
        return office
    
    # office update 
    @staticmethod
    def update_office(
        db: Session,
        office_id: int,
        office_data: OfficeUpdate
    ):

        office = OfficeRepository.get_office_by_id(db, office_id)

        if office is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Office not found."
            )

        # Check duplicate office name
        if office_data.office_name is not None:

            existing_office = OfficeRepository.get_office_by_name(
                db,
                office_data.office_name
            )

            if (
                existing_office
                and existing_office.office_id != office_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Office name already exists."
                )

            office.office_name = office_data.office_name

        if office_data.address is not None:
            office.address = office_data.address

        if office_data.city is not None:
            office.city = office_data.city

        if office_data.state is not None:
            office.state = office_data.state

        if office_data.country is not None:
            office.country = office_data.country

        return OfficeRepository.update_office(db, office)
    
    # delete operation 
    @staticmethod
    def delete_office(db:Session, office_id: int):
        office = OfficeRepository.get_office_by_id(db,office_id)

        if office is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = "Office not found")
        
        OfficeRepository.delete_office(db,office)

        return{
            "message":f"Office '{office.office_name}' deleted successfully."
        }