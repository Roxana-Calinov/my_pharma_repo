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
from about_medication import main as about_medications_main
from stock_forecast_page import show_stock_forecast_page
from dashboard import quantity_vs_stock_level_chart
from announcements import main_announcements
from datetime import datetime
from dotenv import load_dotenv
import os


#Menu options
menu_pages = [
    "🏠 Main page",
    "💊 Medications",
    "⚕️ Pharmacies",
    "📋 Orders",
    "🤖 Medication Info",
    "📈 Stock Forecast",
    "📢 ANMDMR Announcements"
]


def load_env_variables():
    """
    Load environment variables from .env file
    """
    load_dotenv()

def display_logo():
    logo_url = os.getenv("LOGO_PATH")
    st.sidebar.image(logo_url, use_column_width=True)


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
    display_logo()

    st.sidebar.title("🏥 SmartPharma Dashboard")
    return st.sidebar.selectbox("Select the page below:", menu_pages)


def show_main_page():
    """
    Display main page content
    """
    st.header("Welcome to SmartPharma!")
    st.write("This application allows you to manage medications, pharmacies, and orders")
    st.write("Use the sidebar to navigate to different sections.")

    #Display the quantity vs stock level chart
    quantity_vs_stock_level_chart()


def main():
    image_path = cover_image()
    st.image(image_path, use_column_width=True)

    st.title("🏥 SmartPharma")

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
    elif choice == "🤖 Medication Info":
        about_medications_main()
    elif choice == "📈 Stock Forecast":
        show_stock_forecast_page()
    elif choice == "📢 ANMDMR Announcements":
        main_announcements()


    calendar = st.sidebar.date_input("Select a date", datetime.now())


if __name__ == "__main__":
    main()
