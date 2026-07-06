from sqlalchemy.orm import Session
from app.models.office import Office

class OfficeRepository:
    @staticmethod 
    def create_office(db:Session, office:Office):
        db.add(office)
        db.commit()
        db.refresh(office)
        return office
    
    @staticmethod 
    def get_office_by_id(db:Session, office_id: int):
        return (
            db.query(Office).filter(Office.office_id == office_id).first()
        )
    
    @staticmethod 
    def get_office_by_name(db:Session, office_name:str):
        return (db.query(Office).filter(Office.office_name == office_name)).first()
    
    @staticmethod 
    def get_all_offices(db:Session):
        return db.query(Office).all()
    
    @ staticmethod 
    def delete_office(db:Session, office:Office):
        db.delete(office)
        db.commit()
