from typing import List, Optional
from sqlalchemy.orm import Session
from models import OrderRequest, OrderResponse, OrderDB, OrderItemDB, OrderItemResponse, MedicationDB

class OrderRepository:
    def check_duplicate_order(self, db: Session, order_request: OrderRequest) -> bool:
        existing_orders = db.query(OrderDB).filter(
            OrderDB.pharmacy_id == order_request.pharmacy_id,
            OrderDB.status == order_request.status
        ).all()

        #Check duplicates
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
            raise ValueError("An order with the same pharmacy and data already exists.")

        db_order = OrderDB(pharmacy_id=order_request.pharmacy_id, status="pending")
        db.add(db_order)
        db.flush()  #Forces generation of an order id

        total_amount = 0
        for item in order_request.order_items:
            #Access the medication from DB
            medication = db.query(MedicationDB).filter_by(id=item.medication_id).first()

            if not medication:
                raise ValueError(f"Medication with id {item.medication_id} not found.")

            #Check the stock avalability
            if medication.stock < item.quantity:
                raise ValueError(f"Not enough stock for medication {medication.name}.")

            #Stock & quantity update
            medication.stock -= item.quantity
            medication.quantity += item.quantity

            medication_price = medication.price

            db_order_item = OrderItemDB(order_id=db_order.id, medication_id=item.medication_id, quantity=item.quantity,
                                        price=medication_price)
            db.add(db_order_item)

            #Total order amount
            total_amount += medication.price * item.quantity

        #Set the total amount in the order
        db_order.total_amount = total_amount

        #Commit the updates
        db.commit()
        db.refresh(db_order)

        #Return the order response
        return OrderResponse(
            id=db_order.id,
            pharmacy_id=db_order.pharmacy_id,
            order_date=db_order.order_date,
            status=db_order.status,
            total_amount=db_order.total_amount,
            order_items=[
                OrderItemResponse(
                    medication_id=item.medication_id,
                    quantity=item.quantity,
                    price = medication_price
                ) for item in db_order.order_items
            ]
        )

    def update(self, db: Session, order_id: int, order_request: OrderRequest) -> Optional[OrderResponse]:
        #Current order
        db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if not db_order:
            return None  #Return None if the order does not exist

        #Check if an order is duplicated
        if self.check_duplicate_order(db, order_request):
            raise ValueError("An order with the same pharmacy and data already exists.")

        #Get the existing order items
        existing_order_items = db.query(OrderItemDB).filter(OrderItemDB.order_id == order_id).all()
        existing_items_by_medication = {item.medication_id: item for item in existing_order_items}

        #Update order's basic data
        db_order.pharmacy_id = order_request.pharmacy_id
        db_order.status = order_request.status

        total_amount = 0

        #Iterate through the new order items
        for item in order_request.order_items:
            medication = db.query(MedicationDB).filter_by(id=item.medication_id).first()
            if not medication:
                raise ValueError(f"Medication with id {item.medication_id} not found.")

            #Check if the item already exists in the order
            if item.medication_id in existing_items_by_medication:
                existing_item = existing_items_by_medication[item.medication_id]

                #Calculate stock changes based on quantity difference
                quantity_diff = item.quantity - existing_item.quantity

                if quantity_diff > 0:                   #If quantity increased, decrease stock
                    if medication.stock < quantity_diff:
                        raise ValueError(f"Not enough stock for medication {medication.name}.")
                    medication.stock -= quantity_diff   #Decrease stock for new quantity
                    medication.quantity +=quantity_diff #Increase quantity in medications table

                elif quantity_diff < 0:                        #If quantity decreased, increase stock
                    medication.quantity -= abs(quantity_diff)  #Decrease quantity in medications table
                    medication.stock += abs(quantity_diff)     #Increase stock for reduced quantity

                #Update the existing item in the order
                existing_item.quantity = item.quantity
                existing_item.price = medication.price
            else:
                #If item is new, add it to the order and adjust the stock
                if medication.stock < item.quantity:
                    raise ValueError(f"Not enough stock for medication {medication.name}.")
                medication.stock -= item.quantity     #Decrease stock for new item
                medication.quantity += item.quantity  #Increase quantity in medications table

                new_order_item = OrderItemDB(
                    order_id=db_order.id,
                    medication_id=item.medication_id,
                    quantity=item.quantity,
                    price=medication.price
                )
                db.add(new_order_item)

            #Calculate total order amount
            total_amount += medication.price * item.quantity

        #Remove items that are no longer in the updated order
        for existing_item in existing_order_items:
            if existing_item.medication_id not in {item.medication_id for item in order_request.order_items}:
                medication = db.query(MedicationDB).filter_by(id=existing_item.medication_id).first()
                medication.stock += existing_item.quantity     #Restore stock
                medication.quantity -= existing_item.quantity  #Decrease quantity
                db.delete(existing_item)                       #Delete the item from the order

        #Update the total amount
        db_order.total_amount = total_amount

        #Commit and refresh
        db.commit()
        db.refresh(db_order)

        return OrderResponse(
            id=db_order.id,
            pharmacy_id=db_order.pharmacy_id,
            order_date=db_order.order_date,
            status=db_order.status,
            total_amount=db_order.total_amount,
            order_items=[
                OrderItemDB(
                    medication_id=item.medication_id,
                    quantity=item.quantity,
                    price=medication.price
                ) for item in db_order.order_items
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
                OrderItemResponse(
                    medication_id=item.medication_id,
                    quantity=item.quantity,
                    price=db.query(MedicationDB).filter_by(id=item.medication_id).first().price
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
                    OrderItemResponse(
                        medication_id=item.medication_id,
                        quantity=item.quantity,
                        price=db.query(MedicationDB).filter_by(id=item.medication_id).first().price
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
                            OrderItemResponse(
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
                            OrderItemResponse(
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

