from typing import List, Optional, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import MedicationRequest, MedicationResponse, MedicationDB, PharmacyDB
import base64


class MedicationRepository:
    """
    Repo for managing the medication data from DB.
    """
    def check_duplicate_medication(self, db: Session, medication_request: MedicationRequest) -> bool:
        """
        Check if a medication already exists.
        Return bool: True or False
        """
        existing_medication = db.query(MedicationDB).filter(
            MedicationDB.name == medication_request.name,
            MedicationDB.type == medication_request.type,
            MedicationDB.quantity == medication_request.quantity,
            MedicationDB.price == medication_request.price,
            MedicationDB.pharma_id == medication_request.pharma_id,
            MedicationDB.stock == medication_request.stock

        ).all()  #Get all records with coresponding criteria

        #Check for medications name duplicates (case insensitive)
        return any(med.name.lower() == medication_request.name.lower() for med in existing_medication)


    def add(self, db: Session, medication_request: MedicationRequest) -> MedicationResponse:
        """
        Add medication to DB
        """
        if self.check_duplicate_medication(db, medication_request):
            raise HTTPException(status_code=400, detail="Medication already exists.")


        medication_data = medication_request.model_dump(exclude_unset=True)

        if 'image' in medication_data and medication_data['image']:
            medication_data['image'] = self.encode_image(medication_data['image'])

        db_medication = MedicationDB(**medication_data)
        db.add(db_medication)
        db.commit()
        db.refresh(db_medication)

        return MedicationResponse.model_validate(db_medication)


    def get_all(self, db: Session) -> List[MedicationResponse]:
        """
        Retrieve all medications from DB
        """
        return [MedicationResponse.model_validate(medication) for medication in db.query(MedicationDB).all()]


    def get_by_id(self, db: Session, medication_id: int) -> Optional[MedicationResponse]:
        """
        Retrieve a medication by id.
        """
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()
        return MedicationResponse.model_validate(db_medication) if db_medication else None


    def update(self, db: Session, medication_id: int, medication_request: MedicationRequest):
        """
        Update a medication by id.
        """
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()

        #Check for duplicates before update
        if self.check_duplicate_medication(db, medication_request):
            raise HTTPException(status_code=400, detail="Medication already exists.")

        update_data = medication_request.model_dump(exclude_unset=True)

        if db_medication:
            if 'image' in update_data:
                if update_data['image'] is not None:
                    if isinstance(update_data['image'], str):
                        update_data['image'] = update_data['image']
                    elif isinstance(update_data['image'], bytes):
                        update_data['image'] = base64.b64encode(update_data['image']).decode('utf-8')
                else:
                    update_data.pop('image')

            for key, value in update_data.items():
                setattr(db_medication, key, value)
            db.commit()
            db.refresh(db_medication)
            return MedicationResponse.model_validate(db_medication)

        return HTTPException(status_code=404, detail="Medication not found.")


    def delete(self, db: Session, medication_id: int) -> Optional[MedicationResponse]:
        """
        Delete medication by id.
        """
        db_medication = db.query(MedicationDB).filter(MedicationDB.id == medication_id).first()
        if db_medication:
            db.delete(db_medication)
            db.commit()
            return MedicationResponse.model_validate(db_medication)
        return None


    @staticmethod
    def encode_image(image_data: Union[str, bytes]) -> Optional[str]:
        """
        Encode image to base64
        """
        if isinstance(image_data, str):
            return image_data
        elif isinstance(image_data, bytes):
            return base64.b64encode(image_data).decode('utf-8')


    @staticmethod
    def decode_image(base64_string: str) -> bytes:
        """
        Decode a base64 encoded string back to binary data
        """
        return base64.b64decode(base64_string)


    def get_medications_with_pharmacy(self, db: Session):
        """
        Returns a list of tuples with medications and pharmacy details (full join between medications table
        and pharmacies table)
        """
        return (
            db.query(MedicationDB, PharmacyDB)
            .join(PharmacyDB, MedicationDB.pharma_id == PharmacyDB.id)
            .all()
        )

