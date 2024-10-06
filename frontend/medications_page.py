import streamlit as st
import pandas as pd
from utils import (get_all_medications, get_medication, create_medication, update_medication, delete_medication,
                   get_medications_and_pharmacies, convert_image_to_base64, decode_base64_to_image)


def show_medications_page():
    st.subheader("Medications: Stock & Details")
    menu = ["Medications and Pharmacies", "View All Medications", "View Specific Medication", "Add New Medication",
            "Update Medication", "Delete Medication"]
    choice = st.selectbox("Select an option", menu)

    if choice == "Medications and Pharmacies":
        view_pharma_and_med()
    elif choice == "View All Medications":
        view_all_medications()
    elif choice == "View Specific Medication":
        view_medication()
    elif choice == "Add New Medication":
        add_medication()
    elif choice == "Update Medication":
        init_update_medication()
    elif choice == "Delete Medication":
        init_delete_medication()


#Filter medications based on search query and stock level
def filter_medications(df, search_query, stock_level_filter):
    if search_query:
        df = df[
            df['name'].str.contains(search_query, case=False, na=False) |
            df['type'].str.contains(search_query, case=False, na=False) |
            df['stock_level'].str.contains(search_query, case=False, na=False)
            ]

    if stock_level_filter != "All":
        df = df[df['stock_level'] == stock_level_filter]

    return df


#Display all medications
def view_all_medications():
    st.subheader("All Medications")
    with st.spinner("Loading medications..."):
        medications = get_all_medications().json()

    if not medications:
        st.write("There are no medications.")
        return

    df_medication = pd.DataFrame(medications)

    #Filtering
    search_query = st.text_input("Search", placeholder="Type to search..." , help="Search by medication name, type or stock level.")
    stock_level_filter = st.selectbox("Filter by Stock Level", ["All", "low", "medium", "high"], index=0)

    df_medication = filter_medications(df_medication, search_query, stock_level_filter)

    #Sorting
    sort_medications = st.selectbox("Sort by", options=["Name", "Type"], index=0)
    sort_ascending = st.checkbox("Sort Ascending", value=True)

    if sort_medications:
        sort_column = sort_medications.lower()
        if sort_column in df_medication.columns:
            df_medication[sort_column] = df_medication[sort_column].astype(str)
            df_medication = df_medication.sort_values(by=sort_column, key=lambda x: x.str.lower(), ascending=sort_ascending)

    #Display the DF as a table
    st.dataframe(df_medication)


#Medications and Pharmacies joined
def view_pharma_and_med():
    IMAGE_WIDTH = 200
    IMAGE_HEIGHT = 150

    st.subheader("Medications With Images")
    with st.spinner("Loading medications..."):
        response = get_medications_and_pharmacies()

    if response.status_code == 200:
        data = response.json()
        all_medications = []
        valid_image_meds = []

        for item in data:
            medication = item['medication']
            pharmacy = item['pharmacy']

            med_data = {
                'id': medication['id'],
                'name': medication['name'],
                'type': medication['type'],
                'quantity': medication['quantity'],
                'price': medication['price'],
                'stock': medication['stock'],
                'stock_level': medication['stock_level'],
                'pharmacy_name': pharmacy['name'],
                'pharma_id': medication['pharma_id'],
                'pharmacy_address': pharmacy['address'],
                'pharmacy_contact_phone': pharmacy['contact_phone'],
                'pharmacy_email': pharmacy['email']
            }
            all_medications.append(med_data)

            if medication.get('image'):
                image = decode_base64_to_image(medication['image'])
                if image:
                    image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
                    med_data_with_image = med_data.copy()
                    med_data_with_image['image'] = image
                    valid_image_meds.append(med_data_with_image)

        #Display medications with images
        if valid_image_meds:
            num_cols = 3
            cols = st.columns(num_cols)

            for index, med_data in enumerate(valid_image_meds):
                col = cols[index % num_cols]
                with col:
                    st.write(f"**{med_data['name']}** ({med_data['type']})")
                    st.write(f"Price: {med_data['price']} RON")
                    st.write(f"Quantity: {med_data['quantity']}")
                    st.write(f"Pharmacy: {med_data['pharmacy_name']}")
                    st.write(f"Stock: {med_data['stock']} ({med_data['stock_level']})")
                    st.image(med_data['image'], caption=med_data['name'], use_column_width=True)
                    st.write("---")
        else:
            st.info("No medications with valid images found.")

        #All medications
        st.subheader("All Medications Information")
        df_all_medications = pd.DataFrame(all_medications)
        st.dataframe(df_all_medications)
    else:
        st.error("No valid data.")


#View a specific medication by its ID
def view_medication():
    st.subheader("View Medication Details")
    st.write("Enter the medication ID below to display its details.")

    #Input field for medication ID
    medication_id = st.number_input("Medication ID", min_value=1, step=1, value=1,
                                    help="Enter the ID of the medication you want to view.")

    #Submit button
    if st.button("View Medication"):
        #Fetch medication details based on ID
        medication = get_medication(medication_id)
        medication_json = medication.json()

        if medication.status_code == 200:
            #Display medication details
            st.subheader(f"Medication Name: {medication_json['name']}")
            st.write(f"**Type**: {medication_json['type']}")
            st.write(f"**Quantity**: {medication_json['quantity']}")
            st.write(f"**Price**: {medication_json['price']} RON")
            st.write(f"**Pharma ID**: {medication_json['pharma_id']}")
            st.write(f"**Stock**: {medication_json['stock']} RON")
            st.write(f"**Stock Level**: {medication_json['stock_level']}")
        else:
            #Display an error message if the medication is not found
            st.error(f"Medication with ID {medication_id} not found.")


#Add a new medication
def add_medication():
    st.subheader("Add New Medication")
    st.write("Fill in the details below to add a new medication to the system.")

    with st.form(key='add_medication_form'):
        name = st.text_input("Medication Name", help="Enter the name of the medication.", placeholder="Medication Name")
        type = st.selectbox("Type", ["RX", "OTC"], help="Enter the medication's type", placeholder="RX or OTC")
        quantity = st.number_input("Quantity", min_value=1, step=1, value=1,
                                   help="Enter the medication's quantity at the pharmacy.")
        price = st.number_input("Price (RON)", min_value=0.5, step=0.01, value=0.5,
                                help="Enter the price per unit of the medication.")
        pharma_id = st.number_input("Pharma ID", min_value=1, step=1,
                                    help="Enter the id of the pharmacy where the medication can be found")
        stock = st.number_input("Stock", min_value=1, step=1, help="Enter the available stock quantity.")
        image = st.file_uploader("Upload Image (only JPG/JPEG/PNG format) (Optional)", type=["jpg", "jpeg", "png"])

        submit_button = st.form_submit_button(label="Add Medication", use_container_width=True)

    if submit_button:
        valid, message = validate_medication_input(name, type, pharma_id, stock, quantity, price)

        if not valid:
            st.error(message)
        else:
            result = create_medication(name, type, quantity, price, pharma_id, stock, image)
            if result:
                st.success("Medication added successfully!")
                st.json(result)
            else:
                st.error("An error occurred while adding the medication.")



#Validate medication input
def validate_medication_input(name, type, pharma_id, stock, quantity, price):
    if not all([name, type, pharma_id]) or stock < 1 or quantity < 1 or price < 0.5:
        return False, "All fields must be filled in with valid data."
    return True, ""


#Update an existing medication
def init_update_medication():
    st.subheader("Update Medication")
    st.write("Enter the medication ID and updated details below.")

    #Form for updating medication
    with st.form(key='update_medication_form'):
        medication_id = st.number_input("Medication ID", min_value=1, step=1,
                                        help="Enter the ID of the medication you want to update.")
        name = st.text_input("Medication Name", key='update_medication_name',
                             help="Enter the updated name of the medication.", placeholder="Medication Name")
        type = st.selectbox("Type", ["RX", "OTC"], help="Enter the medication's type", placeholder="RX or OTC")
        quantity = st.number_input("Quantity", min_value=1, step=1, value=1,
                                   help="Enter the medication's quantity at the pharmacy.")
        price = st.number_input("Price (RON)", min_value=0.5, step=0.01, value=0.5,
                                help="Enter the price per unit of the medication.")
        pharma_id = st.number_input("Pharma ID", min_value=1, step=1,
                                    help="Enter the id of the pharmacy where the medication can be found")
        stock = st.number_input("Stock", min_value=1, step=1, help="Enter the available stock quantity.")
        image = st.file_uploader("Upload New Image (JPG/JPEG/PNG) (Optional)", type=["jpg", "jpeg", "png"])

        #Submit button
        submit_button = st.form_submit_button(label="Update Medication")

    #Action on form submission
    if submit_button:
        valid, message = validate_medication_input(name, type, pharma_id, stock, quantity, price)

        if not valid:
            st.error(message)
        else:
            result = update_medication(medication_id, name, type, quantity, price, pharma_id, stock, image)
            if result:
                st.success(f"Medication with ID {medication_id} updated successfully.")
            else:
                st.error("Medication not found or failed to update. Please try again.")


#Delete a medication by its ID
def init_delete_medication():
    st.subheader("Delete Medication")
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

