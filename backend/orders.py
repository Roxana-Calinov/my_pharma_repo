from typing import List, Optional
from sqlalchemy.orm import Session
from models import (OrderRequest, OrderResponse, OrderDB, OrderItemDB, OrderItemResponse, OrderStatus,
                    MedicationDB, MedicationResponse, PharmacyResponse)
import logging


class OrderRepository:
    """
    Repo for managing the order data from DB.
    """
    def check_duplicate_order(self, db: Session, order_request: OrderRequest) -> bool:
        """
        Check if an order already exists.
        Return bool: True or False
        """
        existing_orders = db.query(OrderDB).filter(
            OrderDB.pharmacy_id == order_request.pharmacy_id,
            OrderDB.status == order_request.status
        ).all()

        #Check for duplicates
        for order in existing_orders:
            #Compare orders items
            if len(order.order_items) == len(order_request.order_items):
                same_items = all(
                    item.medication_id == req_item.medication_id and
                    item.quantity == req_item.quantity
                    for item, req_item in zip(order.order_items, order_request.order_items)
                )
                if same_items:
                    return True

        return False

    def add(self, db: Session, order_request: OrderRequest) -> OrderResponse:
        """
        Add order to DB
        """
        #Check if an order is duplicated
        if self.check_duplicate_order(db, order_request):
            raise ValueError("An order with the same pharmacy and data already exists.")

        logging.info(f"OrderRequest status: {order_request.status}")

        db_order = OrderDB(pharmacy_id=order_request.pharmacy_id, status=order_request.status)

        logging.info(f"Created OrderDB object with status: {db_order.status}")

        db.add(db_order)
        logging.info(f"Order status before flush: {db_order.status}")

        db.flush()  #Forces generation of an order id

        total_amount = 0
        for item in order_request.order_items:
            #Access the medication from DB by medication_id to get its name
            medication = db.query(MedicationDB).filter_by(id=item.medication_id).first()

            if not medication:
                raise ValueError(f"Medication with id {item.medication_id} not found.")

            #Get all medications with the same name
            medications_with_same_name = db.query(MedicationDB).filter_by(name=medication.name).all()

            #Check stock availability across all pharmacies with the same medication name
            if medication.stock < item.quantity:
                raise ValueError(f"Not enough stock for medication {medication.name}.")

            for med in medications_with_same_name:
                med.stock -= item.quantity

            #Increase quantity in the pharmacy that made the order
            medication_in_order_pharmacy = db.query(MedicationDB).filter_by(id=item.medication_id,
                                                                            pharma_id=order_request.pharmacy_id).first()
            if medication_in_order_pharmacy:
                medication_in_order_pharmacy.quantity += item.quantity

            #Medication price remains the same
            medication_price = medication.price

            #Add order item
            db_order_item = OrderItemDB(
                order_id=db_order.id,
                medication_id=item.medication_id,
                quantity=item.quantity,
                price=medication_price
            )
            db.add(db_order_item)

            #Total order amount
            total_amount += medication_price * item.quantity

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
                    price=item.price
                ) for item in db_order.order_items
            ]
        )

    def update(self, db: Session, order_id: int, order_request: OrderRequest) -> Optional[OrderResponse]:
        """
        Update order by id
        """
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

        #Update order's data
        db_order.pharmacy_id = order_request.pharmacy_id
        db_order.status = order_request.status

        total_amount = 0

        #Iterate through the new order items
        for item in order_request.order_items:
            medication = db.query(MedicationDB).filter_by(id=item.medication_id).first()
            if not medication:
                raise ValueError(f"Medication with id {item.medication_id} not found.")

            #Get all instances of this medication across all pharmacies
            all_medication_instances = db.query(MedicationDB).filter_by(name=medication.name).all()

            #Update quantity in the pharmacy that made the order and update stock for all pharmacies
            medication_in_order_pharmacy = db.query(MedicationDB).filter_by(id=item.medication_id,
                                                                            pharma_id=order_request.pharmacy_id).first()
            if not medication_in_order_pharmacy:
                raise ValueError(f"Medication with id {item.medication_id} not found in the specified pharmacy.")

            if item.medication_id in existing_items_by_medication:
                existing_item = existing_items_by_medication[item.medication_id]
                quantity_diff = item.quantity - existing_item.quantity
                medication_in_order_pharmacy.quantity += quantity_diff
                #Update stock in all pharmacies
                for med_instance in all_medication_instances:
                    med_instance.stock -= quantity_diff
                existing_item.quantity = item.quantity
            else:
                if medication.stock < item.quantity:
                    raise ValueError(f"Not enough stock for medication {medication.name}.")
                medication_in_order_pharmacy.quantity += item.quantity
                #Update stock in all pharmacies
                for med_instance in all_medication_instances:
                    med_instance.stock -= item.quantity
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
                all_medication_instances = db.query(MedicationDB).filter_by(name=medication.name).all()
                medication_in_order_pharmacy = db.query(MedicationDB).filter_by(id=existing_item.medication_id,
                                                                                pharma_id=order_request.pharmacy_id).first()
                if medication_in_order_pharmacy:
                    medication_in_order_pharmacy.quantity -= existing_item.quantity
                #Restore stock in all pharmacies
                for med_instance in all_medication_instances:
                    med_instance.stock += existing_item.quantity
                db.delete(existing_item)  #Delete the item from the order

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
        """
        Retrieve all orders from DB
        """
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
        """
        Retrieve a specific order by its id.
        """
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
        """
        Update the status of a specific order
        """
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
        """
        Delete a specific order by id.
        """
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
