"""
Pharmacy page - manage pharma data

Main components:
-> CRUD (Create, Read, Update, Delete) for pharma data
-> A map with the pharma location
-> Input validation for email and phone number fields
"""
import streamlit as st
import pandas as pd    #data manipulation & visualization
from utils import get_all_pharmacies, get_pharmacy, create_pharmacy, update_pharmacy, delete_pharmacy
import re              #Python build-in regex module, used for input validation
import pydeck as pdk   #interactive map


def show_pharmacies_page():
    """
    Main function for displaying the pharmacy management interface.

    Menu for the CRUD operations and calls functions based on user's selection.
    """
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

    display_locations()


#Display all pharmacies
def view_all_pharmacies():
    """
    Display all available pharmacies in a table (including search functionality).

    This function fetch all the pharma data, creates a Pandas DB, and display the data.
    It also includes search functionality.
    """
    st.subheader("All Pharmacies")
    #Fetch pharmacies from backend
    with st.spinner("Loading pharmacies..."):
        pharmacies = get_all_pharmacies().json()

    if not pharmacies:
        st.warning("The pharmacy has not been found.")
        return

    df = pd.DataFrame(pharmacies)

    #Filtering
    search_query = st.text_input("Search", "", help="Search by pharmacy name, address or email.")
    if search_query:
        df = df[
            df['name'].str.contains(search_query, case=False) |
            df['address'].str.contains(search_query, case=False) |
            df['email'].str.contains(search_query, case=False)
        ]
        if df.empty:
            st.warning("The pharmacy has not been found.")
            return
    st.dataframe(df)


#Display a specific pharmacy
def view_pharmacy():
    """
    Display a specific pharmacy based on the user's input
    """
    st.subheader("View Specific Pharmacy Details")
    st.write("Enter the pharmacy id to view pharmacy information.")

    #Input field for pharma ID
    pharmacy_id = st.number_input("Pharmacy ID",
                                  min_value=1,
                                  step=1,
                                  value=1,
                                  help="Enter the ID of the pharmacy you want to view."
                                  )

    #Submit button
    if st.button("View Pharmacy"):
        #Fetch pharmacy details based on it's ID
        pharmacy = get_pharmacy(pharmacy_id)

        if pharmacy.status_code == 200:
            pharmacy_json = pharmacy.json()

            #Display pharmacy details if found
            st.subheader(f"Pharmacy Name: {pharmacy_json['name']}")
            st.write(f"**Address**: {pharmacy_json['address']}")
            st.write(f"**Email**: {pharmacy_json['email']}")
            st.write(f"**Phone**: {pharmacy_json['contact_phone']}")
        else:
            #Display an error message if the pharmacy have not been found
            st.error(f"Pharmacy with ID {pharmacy_id} has not been found.")


#Add a new pharma
def add_pharmacy():
    """
    Form for adding a new pharmacy
    """
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
    """
    Form for update an existing pharmacy
    """
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
    """
    Form for deleting a pharmacy
    """
    st.subheader("Delete Pharmacy")
    pharmacy_id = st.number_input("Pharmacy ID", min_value=1)
    if st.button("Delete Pharmacy"):
        response = delete_pharmacy(pharmacy_id)
        if response.status_code == 200:
            st.success(f"Pharmacy with ID {pharmacy_id} deleted successfully.")
        else:
            st.error("Failed to delete pharmacy.")


#MAP
def display_locations():
    """
    Display a map with the pharma's locations using Pydeck
    """
    #Create DF with geographical coordinates, location labels and colors
    pharma_locations = pd.DataFrame({
        'lat': [45.6428, 45.6551, 45.6469],                                 #Latitude
        'lon': [25.5893, 25.5963, 25.5884],                                 #Longitude
        'location': ['Str. Republicii', 'Str. Lunga', 'Piata Teatrului'],   #Locations
        'color': [[0,153,153], [0,153,0], [153, 0,76]]
    })

    layer = pdk.Layer(
        'ScatterplotLayer',
        pharma_locations,
        get_position='[lon, lat]',
        get_radius=100,
        get_fill_color='color',
        pickable=True
    )

    #Add text for every location
    text_layer = pdk.Layer(
        "TextLayer",
        pharma_locations,
        get_position='[lon, lat]',
        get_text="location",
        get_size=16,
        get_color=[255, 255, 255],
        get_alignment_baseline="'bottom'"
    )

    #Map configuration
    view_state = pdk.ViewState(
        latitude=45.648,   #Centered on Brasov
        longitude=25.593,
        zoom=13.5,
        pitch=45
    )

    #Display map with layers
    r = pdk.Deck(
        layers=[layer, text_layer],
        initial_view_state=view_state,
        tooltip={"text": "{location}"}
    )

    #Display the map
    st.pydeck_chart(r)

