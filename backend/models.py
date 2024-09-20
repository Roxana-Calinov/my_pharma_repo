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
    description = Column(String, index=True)
    quantity = Column(Integer, index=True)
    price = Column(Float, index=True)


class MedicationRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    description: Optional[str] = None
    quantity: int = Field(ge=1)
    price: float = Field(gt=0)


class Medication(MedicationRequest):
    id: int

    class Config:
        from_attributes = True