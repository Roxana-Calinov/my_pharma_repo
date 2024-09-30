#Frontend for my project using Streamlit
#The script interacts with the backend APIs to display and manage the medications, allowing the users to perform
# CRUD operations in the system.
"""
To run the app, in terminal: streamlit run main.py
"""
import streamlit as st
from medications_page import show_medications_page
from pharmacies_page import show_pharmacies_page
from orders_page import show_orders_page
from datetime import datetime
from dotenv import load_dotenv
import os


#Load environment variables
load_dotenv()
image_path = os.getenv("IMAGE_PATH")

st.image(image_path, use_column_width=True)

#Sidebar for navigation
st.sidebar.title("🏥 SmartPharma Stock Dashboard")
st.title("🏥 SmartPharma Stock")


#Menu options for the user
menu = ["🏠 Main page", "💊 Medications", "⚕️ Pharmacies", "📋 Orders"]
choice = st.sidebar.selectbox("Choose an page:", menu)


if choice == "💊 Medications":
    show_medications_page()
elif choice == "⚕️ Pharmacies":
    show_pharmacies_page()
elif choice == "📋 Orders":
    show_orders_page()

calendar = st.sidebar.date_input("Select a date", datetime.now())
