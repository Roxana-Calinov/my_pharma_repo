import requests
import streamlit as st
import os
from dotenv import load_dotenv
import logging
import base64
from io import BytesIO
from PIL import Image


load_dotenv()
API_URL = os.getenv("API_URL")


def convert_image_to_base64(uploaded_file):
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()                      #Read the uploaded file as bytes
        return base64.b64encode(image_bytes).decode('utf-8')    #Convert bytes to base64
    return None


def decode_base64_to_image(base64_string):
    """Convert a base64 string to a PIL Image."""
    try:
        image_data = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_data))
    except Exception as e:
        logging.error(f"Error decoding base64 string: {e}")
        return None


#functiile care fac call la FastAPI-ul meu
#MEDICATIONS
def get_all_medications():
    response = requests.get(f"{API_URL}/medications") #libraria requests returneaza inapoi un obiect
    return response

def get_medication(medication_id):
    response = requests.get(f"{API_URL}/medications/{medication_id}")
    return response


def create_medication(name, type, quantity, price, pharma_id, stock, uploaded_file):
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
        files["image"] = ("image.jpg", uploaded_file.getvalue(), uploaded_file.type)

    try:
        response = requests.post(f"{API_URL}/medications", data=medication_data, files=files)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()  # Return the response data if needed
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e.response.text}")  # Print server response for more context
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return None  # Or return a specific error message


def update_medication(medication_id, name, type, quantity, price, pharma_id, stock, uploaded_file):
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
        files["image"] = ("image.jpg", uploaded_file.getvalue(), uploaded_file.type)

    try:
        response = requests.put(f"{API_URL}/medications/{medication_id}", data=medication_data, files=files)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()  # Return the response data if needed
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e.response.text}")  # Print server response for more context
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return None  # Or return a specific error message

def delete_medication(medication_id):
    response = requests.delete(f"{API_URL}/medications/{medication_id}")
    return response


#PHARMACIES
def get_all_pharmacies():
    response = requests.get(f"{API_URL}/pharmacies")
    return response

def get_pharmacy(pharmacy_id):
    response = requests.get(f"{API_URL}/pharmacies/{pharmacy_id}")
    return response

def create_pharmacy(name, address, contact_phone, email):
    pharmacy_data = {
        "name": name,
        "address": address,
        "contact_phone": contact_phone,
        "email": email
    }

    response = requests.post(f"{API_URL}/pharmacies", json=pharmacy_data)
    return response

def update_pharmacy(pharmacy_id, name, address, contact_phone, email):
    pharmacy_data = {
        "name": name,
        "address": address,
        "contact_phone": contact_phone,
        "email": email
    }
    response = requests.put(f"{API_URL}/pharmacies/{pharmacy_id}", json=pharmacy_data)
    return response

def delete_pharmacy(pharmacy_id):
    response = requests.delete(f"{API_URL}/pharmacies/{pharmacy_id}")
    return response


#ORDERS
def get_all_orders():
    response = requests.get(f"{API_URL}/orders")
    return response

def get_order(order_id):
    response = requests.get(f"{API_URL}/orders/{order_id}")
    return response

def create_order(pharmacy_id, order_items, status):
    order_data = {
        "pharmacy_id": pharmacy_id,
        "order_items": order_items,
        "status": status
    }

    response = requests.post(f"{API_URL}/orders", json=order_data)
    if response.status_code != 200:
        st.write(f"API Response: {response.json()}")  # Print the error response for debugging
    return response

def update_order(order_id, pharmacy_id, order_items, status):
    order_data = {
        "pharmacy_id": pharmacy_id,
        "order_items": order_items,
        "status": status
    }

    response = requests.put(f"{API_URL}/orders/{order_id}/update", json=order_data)
    return response

def update_order_status(order_id, new_status):
    response = requests.put(f"{API_URL}/orders/{order_id}/status", params={"new_status": new_status})
    return response


def delete_order(order_id):
    response = requests.delete(f"{API_URL}/orders/{order_id}")
    return response


def get_medications_and_pharmacies():
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
                    item['medication']['image'] = None  # Set to None if decoding fails
    return response
