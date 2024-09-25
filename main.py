#Frontend for my project using Streamlit
#The script interacts with the backend APIs to display and manage the medications, allowing the users to perform
# CRUD operations in the system.
"""
To run the app, in terminal: streamlit run main.py
"""


import json
import streamlit as st
from utils import get_all_medications, get_medication, create_medication, update_medication, delete_medication
import pandas as pd
from dotenv import load_dotenv
import os

#Load environment variables
load_dotenv()
image_path = os.getenv("IMAGE_PATH")
st.image(image_path, use_column_width=True)

#Function to display all medications
def view_all_medications():
    st.title("All Medications")
    #Fetch medications from the backend
    medications = get_all_medications().json()
    if len(medications) == 0:
        st.write("There are no medications.")
    else:
        #Convert the list of medications (which is a list of dictionaries) to a pandas DataFrame
        df = pd.DataFrame(medications)

        #Display the DataFrame as a table
        st.dataframe(df)


#Function to view a specific medication by its ID
def view_medication():
    st.title("View Medication Details")
    st.write("Enter the medication ID below to display its details.")

    #Input field for medication ID
    medication_id = st.number_input("Medication ID", min_value=1, step=1, value=1,
                                    help="Enter the ID of the medication you want to view.")
    #Submit button
    if st.button("View Medication"):
        #Fetch medication details based on the ID
        medication = get_medication(medication_id)
        medication_json = medication.json()

        if medication.status_code == 200:
            # Display medication details if found
            st.subheader(f"Medication Name: {medication_json['name']}")
            st.write(f"**Description**: {medication_json['description']}")
            st.write(f"**Quantity**: {medication_json['quantity']}")
            st.write(f"**Price**: {medication_json['price']} RON")
        else:
            #Display an error message if the medication is not found
            st.error(f"Medication with ID {medication_id} not found.")


#Function to add a new medication
def add_medication():
    st.title("Add New Medication")
    #Instruction for the user
    st.write("Fill in the details below to add a new medication to the system.")

    #Form for medication input
    with st.form(key='add_medication_form'):
        name = st.text_input("Medication Name", help="Enter the name of the medication.",
                             placeholder="e.g.: Paracetamol")
        quantity = st.number_input("Quantity", min_value=1, step=1, help="Enter the available stock quantity.", value=1)
        price = st.number_input("Price RON", min_value=0.5, step=0.01,
                                help="Enter the price per unit of the medication.", value=0.5)
        description = st.text_area("Description", help="Provide a brief description of the medication.",
                                   placeholder="e.g.: Raceala")

        #Submit button
        submit_button = st.form_submit_button(label="Add Medication")

    #Action on form submission
    if submit_button:
        if not name or quantity < 1 or price < 0.5:
            st.error("All fields must be filled in with valid data.")
        else:
            result = create_medication(name, quantity, price, description)
            if result.status_code == 200:
                st.success(f"Medication '{name}' added successfully with ID: {result.json()['id']}")
            else:
                st.error("Failed to add medication. Please try again.")


#Function to update an existing medication
def init_update_medication():
    st.title("Update Medication")
    st.write("Enter the medication ID and updated details below.")

    #Form for updating medication details
    with st.form(key='update_medication_form'):
        medication_id = st.number_input("Medication ID", min_value=1, step=1,
                                        help="Enter the ID of the medication you want to update.")
        name = st.text_input("Medication Name", key='update_medication_name',
                             help="Enter the updated name of the medication.",
                             placeholder="e.g.: Parasinus")
        quantity = st.number_input("Quantity", key='update_medication_quantity',
                                   min_value=1, step=1, help="Enter the updated stock quantity.",
                                   value=1)
        price = st.number_input("Price RON", key='update_medication_price',
                                min_value=0.5, step=0.01,
                                help="Enter the updated price per unit of the medication.", value=0.5)
        description = st.text_area("Description", key='update_medication_description',
                                   help="Provide the updated description of the medication.",
                                   placeholder="e.g.: Raceala")

        #Submit button
        submit_button = st.form_submit_button(label="Update Medication")

    # Action on form submission
    if submit_button:
        if medication_id <= 0 or not name or quantity < 1 or price < 0.5:
            st.error("All fields must be filled in with valid data.")
        else:
            result = update_medication(medication_id, name, quantity, price, description)
            if result.status_code == 200:
                st.success(f"Medication with ID {medication_id} updated successfully.")
            else:
                st.error("Medication not found or failed to update. Please try again.")


#Function to delete a medication by its ID
def init_delete_medication():
    st.title("Delete Medication")
    st.write("Enter the medication ID to delete.")

    #Form for deleting medication
    with st.form(key='delete_medication_form'):
        medication_id = st.number_input("Medication ID", min_value=1, step=1,
                                        help="Enter the ID of the medication you want to delete.")

        #Submit button
        submit_button = st.form_submit_button(label="Delete Medication")

    #Action on form submission
    if submit_button:
        if medication_id <= 0:
            st.error("Please enter a valid medication ID.")
        else:
            result = delete_medication(medication_id)
            if result.status_code == 200:
                st.success(f"Medication with ID {medication_id} deleted successfully.")
            else:
                st.error("Medication not found or failed to delete. Please try again.")


#Sidebar for navigation
st.sidebar.title("Pharma Warehouse Dashboard")
st.title("☻ SmartPharma Stock ☻")


#Menu options for the user
menu = ["View All Medications", "View Specific Medication", "Add New Medication", "Update Medication", "Delete Medication"]
choice = st.sidebar.selectbox("Choose an option from the list below:", menu)


#Conditional rendering based on the selected menu option
if choice == "View All Medications":
    view_all_medications()
elif choice == "View Specific Medication":
    view_medication()
elif choice == "Add New Medication":
    add_medication()
elif choice == "Update Medication":
    init_update_medication()
elif choice == "Delete Medication":
    init_delete_medication()