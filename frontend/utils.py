import requests
import os
from dotenv import load_dotenv

load_dotenv()

#API_URL se considera normal secret si trebuie pus intr-un venv file sau config.yaml file si nu se urca pe github
#utils.py citeste dintr-un .venv si .venv nu este pe github, iar .venv il injectam in machine
API_URL = os.getenv("API_URL")


#functiile care fac call la fastAPI-ul meu
def get_all_medications():
    response = requests.get(f"{API_URL}/medications") #libraria requests returneaza inapoi un obiect
    return response


def get_medication(medication_id):
    response = requests.get(f"{API_URL}/medications/{medication_id}")
    return response


def create_medication(name, quantity, price, description=None):
    medication_data = {
        "name": name,
        "quantity": quantity,
        "price": price,
    }
    if description:
        medication_data["description"] = description

    response = requests.post(f"{API_URL}/medications", json=medication_data)
    return response


def update_medication(medication_id, name, quantity, price, description):
    medication_data = {
        "name": name,
        "quantity": quantity,
        "price": price,
        "description": description
    }
    response = requests.put(f"{API_URL}/medications/{medication_id}", json=medication_data)
    return response


def delete_medication(medication_id):
    response = requests.delete(f"{API_URL}/medications/{medication_id}")
    return response
