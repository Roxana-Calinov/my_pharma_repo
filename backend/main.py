"""
To run the app, in terminal: uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from medications import MedicationRepository
from models import MedicationRequest, Medication


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
medication_repo = MedicationRepository()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Read all medications
@app.get("/medications", response_model=List[Medication])
async def get_medications(db: Session = Depends(get_db)):
    return medication_repo.get_all(db)


@app.get("/medications/{medication_id}", response_model=Medication)
async def get_medication(medication_id: int, db: Session = Depends(get_db)):
    medication = medication_repo.get_by_id(db, medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medication not found in our database!")
    return medication


@app.post("/medications", response_model=Medication)
async def create_medication(request: MedicationRequest, db: Session = Depends(get_db)):
    return medication_repo.add(db, request)


@app.put("/medications/{medication_id}", response_model=Medication)
async def update_medication(medication_id: int, request: MedicationRequest, db: Session = Depends(get_db)):
    medication = medication_repo.update(db, medication_id, request)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medication not found in our database!")
    return medication


@app.delete("/medications/{medication_id}", response_model=Medication)
async def delete_medication(medication_id: int, db: Session = Depends(get_db)):
    medication = medication_repo.delete(db, medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medication not found in our database!")
    return medication
