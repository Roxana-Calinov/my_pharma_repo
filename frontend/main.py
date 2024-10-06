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


#Menu options
menu_pages = [
    "🏠 Main page",
    "💊 Medications",
    "⚕️ Pharmacies",
    "📋 Orders"
]


def load_env_variables():
    """
    Load environment variables from .env file
    """
    load_dotenv()


def cover_image():
    """
    Set cover image
    """
    image_path = os.getenv("IMAGE_PATH")
    return image_path

def display_sidebar():
    """
    Display sidebar
    """
    st.sidebar.title("🏥 SmartPharma Stock Dashboard")
    return st.sidebar.selectbox("Select the page below:", menu_pages)


def show_main_page():
    """
    Display main page content
    """
    st.header("Welcome to SmartPharma Stock!")
    st.write("This application allows you to manage medications, pharmacies, and orders")
    st.write("Use the sidebar to navigate to different sections.")


def main():
    image_path = cover_image()
    st.image(image_path, use_column_width=True)

    st.title("🏥 SmartPharma Stock")

    #Display sidebar
    choice = display_sidebar()

    #Go to choosen page
    if (choice == "🏠 Main page"):
        show_main_page()
    elif (choice == "💊 Medications"):
        show_medications_page()
    elif choice == "⚕️ Pharmacies":
        show_pharmacies_page()
    elif choice == "📋 Orders":
        show_orders_page()

    calendar = st.sidebar.date_input("Select a date", datetime.now())


if __name__ == "__main__":
    main()
