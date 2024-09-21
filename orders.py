from typing import List, Optional
from sqlalchemy.orm import Session
from models import OrderRequest, OrderResponse, OrderDB, OrderItemDB, OrderItemRequest

class OrderRepository:
    def add(self, db: Session, order_request: OrderRequest) -> OrderResponse:
        db_order = OrderDB(pharmacy_id=order_request.pharmacy_id, status="pending")
        db.add(db_order)
        db.flush()  # This assigns an id to db_order

        total_amount = 0
        for item in order_request.order_items:
            db_order_item = OrderItemDB(order_id=db_order.id, **item.model_dump())
            db.add(db_order_item)
            total_amount += item.price * item.quantity

        db_order.total_amount = total_amount
        db.commit()
        db.refresh(db_order)

        return OrderResponse(
            id=db_order.id,
            pharmacy_id=db_order.pharmacy_id,
            order_date=db_order.order_date,
            status=db_order.status,
            total_amount=db_order.total_amount,
            order_items=[OrderItemRequest.model_validate(item) for item in db_order.order_items]
        )

    def get_all(self, db: Session) -> List[OrderResponse]:
        return [OrderResponse(
            id=order.id,
            pharmacy_id=order.pharmacy_id,
            order_date=order.order_date,
            status=order.status,
            total_amount=order.total_amount,
            order_items=[OrderItemRequest.model_validate(item) for item in order.order_items]
        ) for order in db.query(OrderDB).all()]

    def get_by_id(self, db: Session, order_id: int) -> Optional[OrderResponse]:
        db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if db_order:
            return OrderResponse(
                id=db_order.id,
                pharmacy_id=db_order.pharmacy_id,
                order_date=db_order.order_date,
                status=db_order.status,
                total_amount=db_order.total_amount,
                order_items=[OrderItemRequest.model_validate(item) for item in db_order.order_items]
            )
        return None

    def update_status(self, db: Session, order_id: int, new_status: str) -> Optional[OrderResponse]:
        db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if db_order:
            db_order.status = new_status
            db.commit()
            db.refresh(db_order)
            return OrderResponse(
                id=db_order.id,
                pharmacy_id=db_order.pharmacy_id,
                order_date=db_order.order_date,
                status=db_order.status,
                total_amount=db_order.total_amount,
                order_items=[OrderItemRequest.model_validate(item) for item in db_order.order_items]
            )
        return None

    def delete(self, db: Session, order_id: int) -> Optional[OrderResponse]:
        db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if db_order:
            response = OrderResponse(
                id=db_order.id,
                pharmacy_id=db_order.pharmacy_id,
                order_date=db_order.order_date,
                status=db_order.status,
                total_amount=db_order.total_amount,
                order_items=[OrderItemRequest.model_validate(item) for item in db_order.order_items]
            )
            db.delete(db_order)
            db.commit()
            return response
        return None