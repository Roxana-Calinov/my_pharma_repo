from typing import List, Optional
from sqlalchemy.orm import Session
from models import MedicationRequest, Medication, MedicationDB


class MedicationRepository:

    def add(self, db: Session, medication_request: MedicationRequest) -> Medication:
        db_medication = MedicationDB(**medication_request.model_dump())  # medication_request.model_dump() = {"name": "x", "price":"y", ...}  => MedicationDB(name="x", price="y")
        db.add(db_medication)
        db.commit()
        db.refresh(db_medication)
        return Medication.model_validate(db_medication)

    def get_all(self, db: Session) -> List[Medication]:
        return [Medication.model_validate(medication) for medication in db.query(MedicationDB).all()]

    def get_by_id(self, db: Session, medication_id: int):
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()
        return Medication.model_validate(db_medication) if db_medication else None

    def update(self, db: Session, medication_id: int, medication_request: MedicationRequest):
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()
        if db_medication:
            for key, value in medication_request.model_dump().items():
                setattr(db_medication, key, value)
            db.commit()
            db.refresh(db_medication)
            return Medication.model_validate(db_medication)
        return None

    def delete(self, db: Session, medication_id: int) -> Optional[Medication]:
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()
        if db_medication:
            db.delete(db_medication)
            db.commit()
            return Medication.model_validate(db_medication)
        return None