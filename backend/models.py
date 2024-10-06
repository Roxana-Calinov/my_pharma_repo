"""
# pip install pydantic
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.event import listens_for
from database import Base
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional
from enum import Enum


#Using Enum for order status
class OrderStatus(str, Enum):
    processed = "processed"
    pending = "pending"
    delivered = "delivered"


#Database models
class MedicationDB(Base):
    """
    DB model for medication
    """
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)
    quantity = Column(Integer, index=True)
    price = Column(Float, index=True)
    pharma_id = Column(Integer, ForeignKey("pharmacies.id"), index=True)
    stock = Column(Integer, index=True)
    stock_level = Column(String, index=True)
    image = Column(Text, nullable=True)

    #Relationships
    pharmacy = relationship("PharmacyDB", back_populates="medications")
    order_items = relationship("OrderItemDB", back_populates="medication")


    #Stock level update
    def update_stock_level(self):
        """
        Update automatically the stock level based on current stock.
        Low: 0-100
        Medium: 101 - 350
        High: >= 351
        """
        if self.stock <= 100:
            self.stock_level = 'low'
        elif 101 <= self.stock <= 350:
            self.stock_level = 'medium'
        else:
            self.stock_level = 'high'


#Listen for automatic update of the stock_level
@listens_for(MedicationDB, 'before_update')
def before_update(mapper, connection, target):
    """
    SQLAlchemy listener that updates stock level before update operation.
    """
    target.update_stock_level()

@listens_for(MedicationDB, 'before_insert')
def before_insert(mapper, connection, target):
    """
    SQLAlchemy listener that updates stock level before insert operation.
    """
    target.update_stock_level()


class PharmacyDB(Base):
    """
    DB model for pharmacy
    """
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    contact_phone = Column(String)
    email = Column(String)

    #Relationships
    medications = relationship("MedicationDB", back_populates="pharmacy")
    orders = relationship("OrderDB", back_populates="pharmacy")


class OrderDB(Base):
    """
    DB model for order
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id"), index=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLAlchemyEnum(OrderStatus))
    total_amount = Column(Float)

    #Relationships
    pharmacy = relationship("PharmacyDB", back_populates="orders")
    order_items = relationship("OrderItemDB", back_populates="order")


class OrderItemDB(Base):
    """
    DB model for order item
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), index=True)
    quantity = Column(Integer)
    price = Column(Float)

    #Relationships
    order = relationship("OrderDB", back_populates="order_items")
    medication = relationship("MedicationDB", back_populates="order_items")


### Pydantic models ###
#POST, PUT (exclude stock_level)
class MedicationRequest(BaseModel):
    """
    Pydantic model for adding or updating medication
    """
    name: str = Field(min_length=3, max_length=50)
    type: str = Field(..., description="Medication type: RX or OTC")
    quantity: int = Field(ge=0, description="Available medications in the pharmacy")
    price: float = Field(gt=0)
    pharma_id: int = Field(..., description="Pharma where the medication can be found")
    stock: int = Field(ge=0, description="The number of medications in stock in the warehouse")
    image: Optional[bytes] = None

    @field_validator('type')
    def validate_type(cls, v):
        """
        Validator to ensure that the medication type is RX or OTC.
        """
        allowed_types = ["RX", "OTC"]
        if v not in allowed_types:
            raise ValueError(f"Invalid medication type {v}. See allowed types: {allowed_types}.")
        return v

    class Config:
        from_attributes = True


#GET operations (include stock_level)
class MedicationResponse(BaseModel):
    """
    Pydantic model for returning medication data, the stock level is included.
    """
    id: int
    name: str
    type: str
    quantity: int
    price: float
    pharma_id: int
    stock: int
    stock_level: str
    image: Optional[bytes] = None

    class Config:
        from_attributes = True


class PharmacyRequest(BaseModel):
    """
    Pydantic model for adding or updating pharmacy
    Validations for phone and email
    """
    name: str = Field(min_length=3, max_length=100)
    address: str
    contact_phone: str = Field(..., description="Phone")
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Email")

    class Config:
        from_attributes = True


class PharmacyResponse(BaseModel):
    """
    Pydantic model for returning pharmacy data
    """
    id: int
    name: str
    address: str
    contact_phone: str
    email: str

    class Config:
        from_attributes = True


class Pharmacy(PharmacyRequest):
    id: int

    class Config:
        from_attributes = True


class OrderItemRequest(BaseModel):
    """
    Pydantic model for creating order
    """
    medication_id: int = Field(..., description="Medication ID")
    quantity: int = Field(gt=0)

    class Config:
        from_attributes = True

class OrderItemResponse(BaseModel):
    """
    Pydantic model for returning order item data (including the price).
    """
    medication_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderRequest(BaseModel):
    """
    Pydantic model for adding and updating orders.
    """
    pharmacy_id: int = Field(..., description="Pharmacy ID")
    order_items: List[OrderItemRequest]
    status: OrderStatus

    class Config:
        use_enum_value = True
        from_attributes = True


class OrderResponse(BaseModel):
    """
    Pydantic model for returning order data (including total amount & order items).
    """
    id: int
    pharmacy_id: int
    order_date: datetime
    status: OrderStatus
    total_amount: float
    order_items: List[OrderItemResponse]

    class Config:
        use_enum_value = True
        from_attributes = True


class MedicationWithPharmacyResponse(BaseModel):
    """
    Pydantic model that return data from medications table and pharmacies table (full join)
    """
    medication: MedicationResponse
    pharmacy: Pharmacy

    class Config:
        from_attributes = True

