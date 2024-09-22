"""
# pip install pydantic
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum as PyEnum

# Database models
class MedicationDB(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(Enum("RX", "OTC", name="medication_type"), index=True)
    quantity = Column(Integer, index=True)
    price = Column(Float, index=True)
    pharma_id = Column(Integer, ForeignKey("pharmacies.id"), index=True)
    stock = Column(Integer, index=True)
    stock_level = Column(Enum("low", "medium", "high", name="stock_level"), index=True)

    pharmacy = relationship("PharmacyDB", back_populates="medications")
    order_items = relationship("OrderItemDB", back_populates="medication")

class PharmacyDB(Base):
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    contact_phone = Column(String)
    email = Column(String)

    medications = relationship("MedicationDB", back_populates="pharmacy")
    orders = relationship("OrderDB", back_populates="pharmacy")

class OrderDB(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id"), index=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum("pending", "processed", "delivered", "canceled", name="order_status"))
    total_amount = Column(Float)
    pharmacy = relationship("PharmacyDB", back_populates="orders")
    order_items = relationship("OrderItemDB", back_populates="order")

class OrderItemDB(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), index=True)
    quantity = Column(Integer)
    price = Column(Float)
    order = relationship("OrderDB", back_populates="order_items")
    medication = relationship("MedicationDB", back_populates="order_items")

# Pydantic models
class MedicationType(PyEnum):
    RX = "RX"
    OTC = "OTC"

class StockLevel(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class MedicationRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    type: MedicationType  # Enum corresponding to SQLAlchemy Enum
    quantity: int = Field(ge=0, description="Available medications in the pharmacy")
    price: float = Field(gt=0)
    pharma_id: int = Field(..., description="Pharma where the medication can be found")
    stock: int = Field(ge=0, description="The number of medications in stock in the warehouse")
    stock_level: StockLevel  # Enum corresponding to SQLAlchemy Enum

class Medication(MedicationRequest):
    id: int

    class Config:
        from_attributes = True

class PharmacyRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    address: str
    contact_phone: str
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

class Pharmacy(PharmacyRequest):
    id: int

    class Config:
        from_attributes = True

class OrderItemRequest(BaseModel):
    medication_id: int
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)

class OrderRequest(BaseModel):
    pharmacy_id: int
    order_items: list[OrderItemRequest]

class OrderResponse(BaseModel):
    id: int
    pharmacy_id: int
    order_date: datetime
    status: str
    total_amount: float
    order_items: list[OrderItemRequest]

    class Config:
        from_attributes = True