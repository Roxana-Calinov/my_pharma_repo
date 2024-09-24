from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import MedicationRequest, Medication, MedicationDB

class MedicationRepository:
    def check_duplicate_medication(self, db: Session, medication_request: MedicationRequest) -> bool:
        existing_medication = db.query(MedicationDB).filter(
            MedicationDB.price == medication_request.price,
            MedicationDB.type == medication_request.type,
            MedicationDB.pharma_id == medication_request.pharma_id
        ).all()  #Get all records with coresponding criteria

        #Check for medications name duplicates
        for med in existing_medication:
            if med.name.lower() == medication_request.name.lower():
                return True

        return False  #Return false if there is not any exact duplicate

    def add(self, db: Session, medication_request: MedicationRequest) -> Medication:
        if self.check_duplicate_medication(db, medication_request):
            raise HTTPException(status_code=400,
                                detail="Medication already exists.")

        db_medication = MedicationDB(**medication_request.model_dump())
        db.add(db_medication)
        db.commit()
        db.refresh(db_medication)
        return Medication.model_validate(db_medication)


    def get_all(self, db: Session) -> List[Medication]:
        return [Medication.model_validate(medication) for medication in db.query(MedicationDB).all()]

    def get_by_id(self, db: Session, medication_id: int) -> Optional[Medication]:
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()
        return Medication.model_validate(db_medication) if db_medication else None

    def update(self, db: Session, medication_id: int, medication_request: MedicationRequest):
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()

        #Check duplicates
        if self.check_duplicate_medication(db, medication_request):
            raise HTTPException(status_code=400,
                                detail="Medication already exists.")

        if db_medication:
            for key, value in medication_request.model_dump().items():
                setattr(db_medication, key, value)
            db.commit()
            db.refresh(db_medication)
            return Medication.model_validate(db_medication)
        return HTTPException(status_code=404, detail="Medication not found.")

    def delete(self, db: Session, medication_id: int) -> Optional[Medication]:
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()
        if db_medication:
            db.delete(db_medication)
            db.commit()
            return Medication.model_validate(db_medication)
        return None

