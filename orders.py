from typing import List, Optional
from sqlalchemy.orm import Session
from models import OrderRequest, OrderResponse, OrderDB, OrderItemDB, OrderItemRequest

class OrderRepository:
    def check_duplicate_order(self, db: Session, order_request: OrderRequest) -> bool:
        existing_orders = db.query(OrderDB).filter(
            OrderDB.pharmacy_id == order_request.pharmacy_id,
            OrderDB.status == order_request.status
        ).all()

        #check duplicates
        for order in existing_orders:
            #Compare orders items
            if len(order.order_items) == len(order_request.order_items):
                same_items = all(
                    item.medication_id == req_item.medication_id and
                    item.quantity == req_item.quantity and
                    item.price == req_item.price
                    for item, req_item in zip(order.order_items, order_request.order_items)
                )
                if same_items:
                    return True

        return False

    def add(self, db: Session, order_request: OrderRequest) -> OrderResponse:
        #Check if an order is duplicated
        if self.check_duplicate_order(db, order_request):
            raise ValueError("An order with the same pharmacy and date already exists.")

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
            order_items=[
                OrderItemRequest(
                    medication_id=item.medication_id,
                    quantity=item.quantity,
                    price=item.price
                ) for item in db_order.order_items
            ]
        )

    def update(self, db: Session, order_id: int, order_request: OrderRequest) -> Optional[OrderResponse]:
        db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if not db_order:
            return None  #Return None if the order does not exist

        # Check duplicates, excluding the current order
        if self.check_duplicate_order(db, order_request):
            raise ValueError("An order with the same pharmacy and date already exists.")

        # Update order's data
        db_order.pharmacy_id = order_request.pharmacy_id
        db_order.status = order_request.status
        db_order.total_amount = sum(item.price * item.quantity for item in order_request.order_items)

        db.query(OrderItemDB).filter(OrderItemDB.order_id == order_id).delete()

        for item in order_request.order_items:
            db_order_item = OrderItemDB(order_id=db_order.id, **item.model_dump())
            db.add(db_order_item)

        db.commit()
        db.refresh(db_order)

        return OrderResponse(
            id=db_order.id,
            pharmacy_id=db_order.pharmacy_id,
            order_date=db_order.order_date,
            status=db_order.status,
            total_amount=db_order.total_amount,
            order_items=[
                OrderItemRequest(
                    medication_id=item.medication_id,
                    quantity=item.quantity,
                    price=item.price
                ) for item in order_request.order_items
            ]
        )

    def get_all(self, db: Session) -> List[OrderResponse]:
        orders = db.query(OrderDB).all()
        return [OrderResponse(
            id=order.id,
            pharmacy_id=order.pharmacy_id,
            order_date=order.order_date,
            status=order.status,
            total_amount=order.total_amount,
            order_items=[
                OrderItemRequest(
                    medication_id=item.medication_id,
                    quantity=item.quantity,
                    price=item.price
                ) for item in order.order_items
            ]
        ) for order in orders]

    def get_by_id(self, db: Session, order_id: int) -> Optional[OrderResponse]:
        db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if db_order:
            return OrderResponse(
                id=db_order.id,
                pharmacy_id=db_order.pharmacy_id,
                order_date=db_order.order_date,
                status=db_order.status,
                total_amount=db_order.total_amount,
                order_items=[
                    OrderItemRequest(
                        medication_id=item.medication_id,
                        quantity=item.quantity,
                        price=item.price
                    ) for item in db_order.order_items
                ]
            )
        return None

    def update_status(self, db: Session, order_id: int, new_status: str) -> Optional[OrderResponse]:
        db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if db_order:
            db_order.status = new_status
            db.commit()
            db.refresh(db_order)
            #Map OrderItemDB to OrderItemRequest
            return OrderResponse(
                id=db_order.id,
                pharmacy_id=db_order.pharmacy_id,
                order_date=db_order.order_date,
                status=db_order.status,
                total_amount=db_order.total_amount,
                order_items=[
                            OrderItemRequest(
                                medication_id=item.medication_id,
                                quantity=item.quantity,
                                price=item.price
                            ) for item in db_order.order_items
                ]
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
                order_items=[
                            OrderItemRequest(
                                medication_id=item.medication_id,
                                quantity=item.quantity,
                                price=item.price
                            ) for item in db_order.order_items
                ]
            )
            db.delete(db_order)
            db.commit()
            return response
        return None