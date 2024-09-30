from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import MedicationRequest, MedicationResponse, MedicationDB
import base64


class MedicationRepository:
    def check_duplicate_medication(self, db: Session, medication_request: MedicationRequest) -> bool:
        existing_medication = db.query(MedicationDB).filter(
            MedicationDB.name == medication_request.name,
            MedicationDB.type == medication_request.type,
            MedicationDB.quantity == medication_request.quantity,
            MedicationDB.price == medication_request.price,
            MedicationDB.pharma_id == medication_request.pharma_id,
            MedicationDB.stock == medication_request.stock

        ).all()  #Get all records with coresponding criteria

        #Check for medications name duplicates
        for med in existing_medication:
            if med.name.lower() == medication_request.name.lower():
                return True

        return False  #Return false if there is not any exact duplicate

    def add(self, db: Session, medication_request: MedicationRequest) -> MedicationResponse:
        if self.check_duplicate_medication(db, medication_request):
            raise HTTPException(status_code=400, detail="Medication already exists.")

        db_medication = MedicationDB(**medication_request.model_dump())
        db.add(db_medication)
        db.commit()
        db.refresh(db_medication)
        return MedicationResponse.model_validate(db_medication)


    def get_all(self, db: Session) -> List[MedicationResponse]:
        return [MedicationResponse.model_validate(medication) for medication in db.query(MedicationDB).all()]

    def get_by_id(self, db: Session, medication_id: int) -> Optional[MedicationResponse]:
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()
        return MedicationResponse.model_validate(db_medication) if db_medication else None

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
            return MedicationResponse.model_validate(db_medication)
        return HTTPException(status_code=404, detail="Medication not found.")

    def delete(self, db: Session, medication_id: int) -> Optional[MedicationResponse]:
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()
        if db_medication:
            db.delete(db_medication)
            db.commit()
            return MedicationResponse.model_validate(db_medication)
        return None

    #Get binary data of the image, convert the binary data to base64, convert the base64 output to a string
    @staticmethod
    def encode_image(image_data: bytes) -> str:
        return base64.b64encode(image_data).decode('utf-8')

    @staticmethod
    def decode_image(base64_string: str) -> bytes:
        return base64.b64decode(base64_string)

