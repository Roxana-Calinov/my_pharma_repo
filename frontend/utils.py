import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")


#functiile care fac call la FastAPI-ul meu
#MEDICATIONS
def get_all_medications():
    response = requests.get(f"{API_URL}/medications") #libraria requests returneaza inapoi un obiect
    return response

def get_medication(medication_id):
    response = requests.get(f"{API_URL}/medications/{medication_id}")
    return response

def create_medication(name, type, quantity, price, pharma_id, stock):
    medication_data = {
        "name": name,
        "type": type,
        "quantity": quantity,
        "price": price,
        "pharma_id": pharma_id,
        "stock": stock
    }

    response = requests.post(f"{API_URL}/medications", json=medication_data)
    return response

def update_medication(medication_id, name, type, quantity, price, pharma_id, stock):
    medication_data = {
        "name": name,
        "type": type,
        "quantity": quantity,
        "price": price,
        "pharma_id": pharma_id,
        "stock": stock
    }
    response = requests.put(f"{API_URL}/medications/{medication_id}", json=medication_data)
    return response

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
