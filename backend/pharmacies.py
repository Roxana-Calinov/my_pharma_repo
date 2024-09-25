from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import PharmacyRequest, Pharmacy, PharmacyDB

class PharmacyRepository:
    def check_duplicate_pharmacy(self, db: Session, pharmacy_request: PharmacyRequest) -> bool:
        existing_pharmacy = db.query(PharmacyDB).filter(
            PharmacyDB.name == pharmacy_request.name,
            PharmacyDB.address == pharmacy_request.address,
            PharmacyDB.email == pharmacy_request.email,
            PharmacyDB.contact_phone == pharmacy_request.contact_phone
        ).all() #Get all records with corresponding criteria

        #Check for pharma name duplicates
        for pharma in existing_pharmacy:
            if pharma.name.lower() == pharmacy_request.name.lower():
                return True

        return False #Return False if there is not any duplicates

    def add(self, db: Session, pharmacy_request: PharmacyRequest) -> Pharmacy:
        #Check if the pharma already exists
        if self.check_duplicate_pharmacy(db, pharmacy_request):
            raise HTTPException(status_code=400,
                                detail="Pharmacy already exists.")

        db_pharmacy = PharmacyDB(**pharmacy_request.model_dump())
        db.add(db_pharmacy)
        db.commit()
        db.refresh(db_pharmacy)
        return Pharmacy.model_validate(db_pharmacy)

    def get_all(self, db: Session) -> List[Pharmacy]:
        return [Pharmacy.model_validate(pharmacy) for pharmacy in db.query(PharmacyDB).all()]

    def get_by_id(self, db: Session, pharmacy_id: int) -> Optional[Pharmacy]:
        db_pharmacy = db.query(PharmacyDB).filter(PharmacyDB.id == pharmacy_id).first()
        return Pharmacy.model_validate(db_pharmacy) if db_pharmacy else None

    def update(self, db: Session, pharmacy_id: int, pharmacy_request: PharmacyRequest):
        db_pharmacy = db.query(PharmacyDB).filter(PharmacyDB.id == pharmacy_id).first()

        #Check duplicates
        if self.check_duplicate_pharmacy(db, pharmacy_request):
            raise HTTPException(status_code=400,
                                detail="Pharmacy already exists.")

        if db_pharmacy:
            for key, value in pharmacy_request.model_dump().items():
                setattr(db_pharmacy, key, value)
            db.commit()
            db.refresh(db_pharmacy)
            return Pharmacy.model_validate(db_pharmacy)
        return HTTPException(status_code=404, detail="Pharmacy not found.")

    def delete(self, db: Session, pharmacy_id: int) -> Optional[Pharmacy]:
        db_pharmacy = db.query(PharmacyDB).filter(PharmacyDB.id == pharmacy_id).first()
        if db_pharmacy:
            db.delete(db_pharmacy)
            db.commit()
            return Pharmacy.model_validate(db_pharmacy)
        return None
