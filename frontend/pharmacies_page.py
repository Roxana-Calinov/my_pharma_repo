import streamlit as st
import pandas as pd
from utils import get_all_pharmacies, get_pharmacy, create_pharmacy, update_pharmacy, delete_pharmacy
import re


def show_pharmacies_page():
    st.subheader("Pharmacy Management")

    #Menu for CRUD operations
    menu = ["View All Pharmacies", "View Specific Pharmacy", "Add New Pharmacy", "Update Pharmacy",
            "Delete Pharmacy"]
    choice = st.selectbox("Select an option", menu)

    if choice == "View All Pharmacies":
        view_all_pharmacies()
    elif choice == "View Specific Pharmacy":
        view_pharmacy()
    elif choice == "Add New Pharmacy":
        add_pharmacy()
    elif choice == "Update Pharmacy":
        init_update_pharmacy()
    elif choice == "Delete Pharmacy":
        init_delete_pharmacy()


#Display all pharmacies
def view_all_pharmacies():
    st.subheader("All Pharmacies")
    #Fetch pharmacies from backend
    with st.spinner("Loading pharmacies..."):
        pharmacies = get_all_pharmacies().json()

    if len(pharmacies) == 0:
        st.write("No pharmacies found.")
    else:
        df = pd.DataFrame(pharmacies)

        #Filtering
        search_query = st.text_input("Search", "", help="Search by pharmacy name, address or email.")
        if search_query:
            df = df[
                df['name'].str.contains(search_query, case=False) |
                df['address'].str.contains(search_query, case=False) |
                df['email'].str.contains(search_query, case=False)
            ]

        st.dataframe(df)


#Display a specific pharmacy
def view_pharmacy():
    st.subheader("View Pharmacy Details")
    st.write("Enter the id of the pharmacy to display its details.")

    #Input field for pharma ID
    pharmacy_id = st.number_input("Pharmacy ID",
                                  min_value=1,
                                  step=1,
                                  value=1,
                                  help="Enter the ID of the pharmacy you want to display."
                                  )

    #Submit button
    if st.button("View Pharmacy"):
        #Fetch pharmacy details based on it's ID
        pharmacy = get_pharmacy(pharmacy_id)
        pharmacy_json = pharmacy.json()

        if pharmacy.status_code == 200:
            #Display pharmacy details if found
            st.subheader(f"Pharmacy Name: {pharmacy_json['name']}")
            st.write(f"**Address**: {pharmacy_json['address']}")
            st.write(f"**Email**: {pharmacy_json['email']}")
            st.write(f"**Phone**: {pharmacy_json['contact_phone']}")
        else:
            #Display an error message if the pharmacy have not been found
            st.error(f"Pharmacy with ID {pharmacy_id} not found.")


#Add a new pharma
def add_pharmacy():
    st.subheader("Add New Pharmacy")
    st.write("Fill in the details below to add a new pharmacy to the system.")

    #Form for pharma input
    with st.form(key='add_pharmacy_form'):
        name = st.text_input("Pharmacy Name",
                             help="Enter the pharmacy name.",
                             placeholder="Pharmacy Name",
                             max_chars=255
                             )
        address = st.text_input("Pharmacy Address",
                                help="Enter the pharmacy address.",
                                placeholder="Str. Weiss Michael 13, BV",
                                max_chars=255
                                )
        email = st.text_input("Email Address",
                              help="Enter a valid email address.",
                              placeholder="example@yahoo.com"
                              )
        contact_phone = st.text_input("Contact Phone",
                                      help="Enter the contact phone number.",
                                      placeholder="+40 7XX XXX XXX",
                                      max_chars=15
                                      )
        submit_button = st.form_submit_button(label="Add Pharmacy", use_container_width=True)

    if submit_button:
        if all([name, address, contact_phone, email]):
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                st.error("Invalid email.")
                return

            if not re.match(r"^\+?(\d{1,3})?[-. ]?\(?\d{1,4}?\)?[-. ]?\d{1,4}[-. ]?\d{1,9}$", contact_phone):
                st.error("Invalid phone number.")
                return

            response = create_pharmacy(name, address, contact_phone, email)
            if response.status_code == 200:
                st.success(f"Pharmacy '{name}' added successfully.")
            else:
                st.error("Failed to add pharmacy.")
        else:
            st.error("All fields must be filled in.")

#Update pharma
def init_update_pharmacy():
    st.subheader("Update Pharmacy")
    st.write("Enter the pharmacy ID and update details below.")

    pharmacy_id = st.number_input("Pharmacy ID",
                                  min_value=1,
                                  help="Enter the ID of the pharmacy you want to update."
                                  )
    with st.form(key='update_pharmacy_form'):
        name = st.text_input("New Pharmacy Name",
                             help="Enter the new name for the pharmacy.",
                             placeholder="e.g.: RoxiPharm",
                             max_chars=255
                             )
        address = st.text_input("New Pharmacy Address",
                                help="Enter the new address of the pharmacy",
                                placeholder="Str. Republicii, BV",
                                max_chars=255
                                )
        contact_phone = st.text_input("New Contact Phone",
                                      help="Enter a new phone number",
                                      placeholder="+40 7XX XXX XXX",
                                      max_chars=15
                                      )
        email = st.text_input("New Email Address",
                              help="Enter the new email address.",
                              placeholder="new_pharma_name@yahoo.com"
                              )
        submit_button = st.form_submit_button(label="Update Pharmacy")

    if submit_button:
        if name and address and email and contact_phone:
            response = update_pharmacy(pharmacy_id, name, address, contact_phone, email)
            if response.status_code == 200:
                st.success(f"Pharmacy with ID {pharmacy_id} updated successfully.")
            else:
                st.error("Failed to update pharmacy.")
        else:
            st.error("All fields must be filled in.")

#Delete pharma
def init_delete_pharmacy():
    st.subheader("Delete Pharmacy")
    pharmacy_id = st.number_input("Pharmacy ID", min_value=1)
    if st.button("Delete Pharmacy"):
        response = delete_pharmacy(pharmacy_id)
        if response.status_code == 200:
            st.success(f"Pharmacy with ID {pharmacy_id} deleted successfully.")
        else:
            st.error("Failed to delete pharmacy.")
