"""
Interact with the Pharma Stock API
Contains functions for CRUD operations on medications, pharmacies, and orders
"""
import requests
import os
import logging
from dotenv import load_dotenv
import base64
from io import BytesIO
from PIL import Image
from enum import Enum


#Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL")


def convert_image_to_base64(uploaded_file):
    if uploaded_file is not None:
        #Take file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        #Check img extension
        if file_extension not in ['jpg', 'jpeg', 'png']:
            raise ValueError("Unsupported file type. Only JPG, JPEG and PNG are considerate valid.")

        #Read the uploaded file as bytes
        file_bytes = uploaded_file.read()

        #Open the image using PIL
        img = Image.open(BytesIO(file_bytes))

        #Save the image to a BytesIO object
        buffered = BytesIO()
        img.save(buffered, format="PNG")   #Convert all to PNG for consistency

        #Encode the BytesIO to base64
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    return None


def decode_base64_to_image(base64_string):
    """
    Convert a base64 string to a PIL Image.
    """
    try:
        #Remove the data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]

        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))

        return image
    except Exception as e:
        logging.error(f"Error decoding base64 string: {e}")
        return None


class OrderStatus(str, Enum):
    """
    Order status options
    """
    pending = "pending"
    processed = "processed"
    delivered = "delivered"


#API requests for MEDICATIONS
def get_all_medications():
    """
    Fetch all medications from API.
    """
    response = requests.get(f"{API_URL}/medications")   #The requests library return an object
    return response if response.ok else None


def get_medication(medication_id):
    """
    Fetch a medication by medication ID.
    """
    response = requests.get(f"{API_URL}/medications/{medication_id}")
    return response if response.ok else None


def create_medication(name, type, quantity, price, pharma_id, stock, uploaded_file):
    """
    Create medication.

    name: the medication's name
    type: the type of the medication (RX or OTC)
    quantity: the available quantity of the medication in a certain pharmacy
    price: the medication's price
    pharma_id: the id of the pharmacy where the medication can be found
    stock: the available quantity of medication in the central warehouse
    uploaded_file: the medication's image
    """
    medication_data = {
        "name": name,
        "type": type,
        "quantity": quantity,
        "price": price,
        "pharma_id": pharma_id,
        "stock": stock
    }

    files = {}
    if uploaded_file is not None:
        files["image"] = (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)

    response = requests.post(f"{API_URL}/medications", data=medication_data, files=files)

    if response.ok:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def update_medication(medication_id, name, type, quantity, price, pharma_id, stock, uploaded_file):
    """
    Update a specific medication by ID.

    medication_id: the id of the medication
    name: the medication's name
    type: the type of the medication (RX or OTC)
    quantity: the available quantity of the medication in a certain pharmacy
    price: the medication's price
    pharma_id: the id of the pharmacy where the medication can be found
    stock: the available quantity of medication in the central warehouse
    uploaded_file: the medication's image
    """
    medication_data = {
        "name": name,
        "type": type,
        "quantity": quantity,
        "price": price,
        "pharma_id": pharma_id,
        "stock": stock
    }

    files = {}
    if uploaded_file is not None:
        files["image"] = (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)

    response = requests.put(f"{API_URL}/medications/{medication_id}", data=medication_data, files=files)
    return response.json() if response.ok else None


def delete_medication(medication_id):
    """
    Delete a medication by medication ID.
    """
    response = requests.delete(f"{API_URL}/medications/{medication_id}")
    return response


#API requests for PHARMACIES
def get_all_pharmacies():
    """
    Fetch all pharmacies from API.
    """
    response = requests.get(f"{API_URL}/pharmacies")
    return response


def get_pharmacy(pharmacy_id):
    """
    Fetch a specific pharmacy from API.
    """
    response = requests.get(f"{API_URL}/pharmacies/{pharmacy_id}")
    return response


def create_pharmacy(name, address, contact_phone, email):
    """
    Create a new pharmacy.

    name: the pharmacy name
    address: the address of the pharmacy
    contact_phone: the pharmacy phone
    email: the pharmacy email
    """
    pharmacy_data = {
        "name": name,
        "address": address,
        "contact_phone": contact_phone,
        "email": email
    }

    response = requests.post(f"{API_URL}/pharmacies", json=pharmacy_data)
    return response


def update_pharmacy(pharmacy_id, name, address, contact_phone, email):
    """
    Update a pharmacy by ID.

    name: the pharmacy name
    address: the address of the pharmacy
    contact_phone: the pharmacy phone
    email: the pharmacy email
    """
    pharmacy_data = {
        "name": name,
        "address": address,
        "contact_phone": contact_phone,
        "email": email
    }
    response = requests.put(f"{API_URL}/pharmacies/{pharmacy_id}", json=pharmacy_data)
    return response


def delete_pharmacy(pharmacy_id):
    """
    Delete a pharmacy by ID.
    """
    response = requests.delete(f"{API_URL}/pharmacies/{pharmacy_id}")
    return response


#API requests for ORDERS
def get_all_orders():
    """
    Fetch all orders from API.
    """
    response = requests.get(f"{API_URL}/orders")
    return response


def get_order(order_id):
    """
    Fetch a specific order from API.
    """
    response = requests.get(f"{API_URL}/orders/{order_id}")
    return response


def create_order(pharmacy_id, order_items, status):
    """
    Create a new order.

    pharmacy_id: the id of the pharmacy that placed the order
    order_items: the ordered items
    status: the order status (OrderStatus enum -> pending, processed, delivered)
    """
    order_data = {
        "pharmacy_id": pharmacy_id,
        "order_items": order_items,
        "status": status
    }

    response = requests.post(f"{API_URL}/orders", json=order_data)
    return response if response.ok else None


def update_order(order_id, pharmacy_id, order_items, status):
    """
    Update an order by ID.

    order_id: the order id
    pharmacy_id: the id of the pharmacy that placed the order
    order_items: the ordered items
    status: the order status (OrderStatus enum -> pending, processed, delivered)
    """
    order_data = {
        "pharmacy_id": pharmacy_id,
        "order_items": order_items,
        "status": status.value if isinstance(status, OrderStatus) else status
    }

    response = requests.put(f"{API_URL}/orders/{order_id}/update", json=order_data)
    return response


def update_order_status(order_id, new_status):
    """
    Update the status of the order.
    """
    status = new_status.value if isinstance(new_status, OrderStatus) else new_status
    response = requests.put(f"{API_URL}/orders/{order_id}/status", params={"new_status": new_status})
    return response


def delete_order(order_id):
    """
    Delete an order by ID.
    """
    response = requests.delete(f"{API_URL}/orders/{order_id}")
    return response


#API requests for fetching the Medications & Pharmacies data
def get_medications_and_pharmacies():
    """
    Full join between the medications and pharmacies tables/ all available data from medications and pharmacies
    """
    response = requests.get(f"{API_URL}/medications_with_pharmacies")
    if response.status_code == 200:
        data = response.json()
        for item in data:
            if 'image' in item['medication'] and item['medication']['image']:
                # Convert base64 image to PIL Image
                decoded_image = decode_base64_to_image(item['medication']['image'])
                if decoded_image:
                    item['medication']['image'] = decoded_image
                else:
                    item['medication']['image'] = None      #Set to None if decoding fails
    return response


