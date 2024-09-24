"""
To run the app, in terminal: uvicorn main:app --reload
"""
from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from models import MedicationRequest, Medication, PharmacyRequest, Pharmacy, OrderRequest, OrderResponse
from medications import MedicationRepository
from pharmacies import PharmacyRepository
from orders import OrderRepository

models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True, title="Pharma Stock API", version="1.0")
medication_repo = MedicationRepository()
pharmacy_repo = PharmacyRepository()
order_repo = OrderRepository()
#print(dir(order_repo))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Medication endpoints
@app.get("/medications", response_model=List[Medication])
async def get_medications(db: Session = Depends(get_db)):
    return medication_repo.get_all(db)

@app.get("/medications/{medication_id}", response_model=Medication)
async def get_medication(medication_id: int, db: Session = Depends(get_db)):
    medication = medication_repo.get_by_id(db, medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    return medication

@app.post("/medications", response_model=Medication)
async def create_medication(request: MedicationRequest, db: Session = Depends(get_db)):
    return medication_repo.add(db, request)

@app.put("/medications/{medication_id}", response_model=Medication)
async def update_medication(medication_id: int, request: MedicationRequest, db: Session = Depends(get_db)):
    medication = medication_repo.update(db, medication_id, request)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    return medication

@app.delete("/medications/{medication_id}", response_model=Medication)
async def delete_medication(medication_id: int, db: Session = Depends(get_db)):
    medication = medication_repo.delete(db, medication_id)
    if medication is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    return medication


# Pharmacy endpoints
@app.post("/pharmacies", response_model=Pharmacy)
async def create_pharmacy(request: PharmacyRequest, db: Session = Depends(get_db)):
    return pharmacy_repo.add(db, request)

@app.get("/pharmacies", response_model=List[Pharmacy])
async def get_pharmacies(db: Session = Depends(get_db)):
    return pharmacy_repo.get_all(db)

@app.get("/pharmacies/{pharmacy_id}", response_model=Pharmacy)
async def get_pharmacy(pharmacy_id: int, db: Session = Depends(get_db)):
    pharmacy = pharmacy_repo.get_by_id(db, pharmacy_id)
    if pharmacy is None:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    return pharmacy

@app.put("/pharmacies/{pharmacy_id}", response_model=Pharmacy)
async def update_pharmacy(pharmacy_id: int, request: PharmacyRequest, db: Session = Depends(get_db)):
    pharmacy = pharmacy_repo.update(db, pharmacy_id, request)
    if pharmacy is None:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    return pharmacy

@app.delete("/pharmacies/{pharmacy_id}", response_model=Pharmacy)
async def delete_pharmacy(pharmacy_id: int, db: Session = Depends(get_db)):
    pharmacy = pharmacy_repo.delete(db, pharmacy_id)
    if pharmacy is None:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    return pharmacy


# Order endpoints
@app.post("/orders", response_model=OrderResponse)
async def create_order(request: OrderRequest, db: Session = Depends(get_db)):
    return order_repo.add(db, request)

@app.get("/orders", response_model=List[OrderResponse])
async def get_orders(db: Session = Depends(get_db)):
    return order_repo.get_all(db)

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = order_repo.get_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}/update", response_model=OrderResponse)
async def update_order(order_id: int, request: OrderRequest, db: Session = Depends(get_db)):
    order = order_repo.update(db, order_id, request)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: int, new_status: str, db: Session = Depends(get_db)):
    order = order_repo.update_status(db, order_id, new_status)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.delete("/orders/{order_id}", response_model=OrderResponse)
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = order_repo.delete(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

