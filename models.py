"""
# pip install pydantic
"""
from sqlalchemy import Column, Integer, String, Float
from database import Base
from pydantic import BaseModel, Field
from typing import Optional


class MedicationDB(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)  # RX or OTC
    quantity = Column(Integer, index=True) # Available medications in the pharmacy
    price = Column(Float, index=True)
    pharmacy = Column(String, index=True)  # Pharma where the medication can be found
    stock = Column(Integer, index=True)    # The number of medications in stock in the warehouse
    stock_level = Column(String, index=True)  # Stock level: low, medium, high


class MedicationRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    type: str = Field(..., description="Medication type: RX or OTC")
    quantity: int = Field(ge=0, description="Available medications in the pharmacy")
    price: float = Field(gt=0)
    pharmacy: str = Field(..., description="Pharma where the medication can be found")
    stock: int = Field(ge=0, description="The number of medications in stock in the warehouse")
    stock_level: str = Field(..., description="Stock level: low, medium, high")


class Medication(MedicationRequest):
    id: int

    class Config:
        from_attributes = True