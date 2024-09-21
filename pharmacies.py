from typing import List, Optional
from sqlalchemy.orm import Session
from models import PharmacyRequest, Pharmacy, PharmacyDB

class PharmacyRepository:
    def add(self, db: Session, pharmacy_request: PharmacyRequest) -> Pharmacy:
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

    def update(self, db: Session, pharmacy_id: int, pharmacy_request: PharmacyRequest) -> Optional[Pharmacy]:
        db_pharmacy = db.query(PharmacyDB).filter(PharmacyDB.id == pharmacy_id).first()
        if db_pharmacy:
            for key, value in pharmacy_request.model_dump().items():
                setattr(db_pharmacy, key, value)
            db.commit()
            db.refresh(db_pharmacy)
            return Pharmacy.model_validate(db_pharmacy)
        return None

    def delete(self, db: Session, pharmacy_id: int) -> Optional[Pharmacy]:
        db_pharmacy = db.query(PharmacyDB).filter(PharmacyDB.id == pharmacy_id).first()
        if db_pharmacy:
            db.delete(db_pharmacy)
            db.commit()
            return Pharmacy.model_validate(db_pharmacy)
        return None