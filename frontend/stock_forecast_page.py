"""
Medication stock forecast page
"""
import streamlit as st
import pandas as pd   #data manipulation & visualization
import altair as alt  #statistical visualization lib -> interactive charts
from utils import get_stock_forecast
import time


def create_metric_columns(data):
    """
    #Display main informations (three columns of key metrics)

    Args:
    data (dict): Dictionary containing forecast data for medication

    -> Current Stock: Total stock currently available
    -> Predicted Demand: Demand forecast for next month
    -> Recommended Order: Suggested quantity to order (from suppliers) based on forecast
    """
    st.subheader("Main info")
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Stock", f"{data['total_current_stock']} units")
    col2.metric("Predicted Demand", f"{data['predicted_monthly_demand']} units")
    col3.metric("Recommended Order", f"{data['recommended_order_quantity']} units")


def stock_details_table(data):
    """
    Table contained detailed stock information.
    """
    st.subheader("Stock Details")
    details = pd.DataFrame({
        "Metric": ["Central Stock", "Pharmacies Stock", "Safety Stock", "Predicted Monthly Demand"],
        "Value": [
            data['current_central_stock'],
            data['current_pharmacy_stock'],
            data['safety_stock'],
            data['predicted_monthly_demand']
        ]
    })
    st.table(details)


def model_performance_table(data):
    """
    Model performance metrics
    """
    st.subheader("Model Performance")
    performance_data = pd.DataFrame({
        "Metric": list(data['model_performance'].keys()),
        "Value": list(data['model_performance'].values())
    })
    st.table(performance_data)


def stock_distribution_chart(data):
    """
    Bar chart with distribution of stock (central vs. pharmacies)
    """
    st.subheader("Current Stock Distribution")
    stock_data = pd.DataFrame({
        "Location": ["Central Stock", "Pharmacies Stock"],
        "Stock": [data['current_central_stock'], data['current_pharmacy_stock']]
    })
    chart = alt.Chart(stock_data).mark_bar().encode(
        x='Location:O',
        y='Stock:Q',
        color='Location:N'
    ).properties(
        title='Current Stock Distribution',
        width=400,
        height=300
    )
    st.altair_chart(chart, use_container_width=True)


def prediction_overview_chart(data):
    """
    Bar chart comparing current stock vs. predicted demand vs. recommended order quantity
    """
    st.subheader("Prediction vs Current Stock")
    prediction_data = pd.DataFrame({
        "Category": ["Current Stock", "Predicted Demand", "Recommended Order"],
        "Value": [data['total_current_stock'], data['predicted_monthly_demand'], data['recommended_order_quantity']]
    })
    chart = alt.Chart(prediction_data).mark_bar().encode(
        x='Category:O',
        y='Value:Q',
        color='Category:N'
    ).properties(
        title='Stock Prediction Overview',
        width=600,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)


def radial_historical_chart(data):
    """
    Radical chart comparing historical demand
    """
    st.subheader("Historical Demand Comparison (Radial)")
    hist_data = pd.DataFrame({
        "Year": ["One year ago", "Two years ago", "Three years ago"],
        "Demand": [
            data['historical_comparison']['one_year_ago'],
            data['historical_comparison']['two_years_ago'],
            data['historical_comparison']['three_years_ago']
        ]
    })
    chart = alt.Chart(hist_data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Demand", type="quantitative"),
        color=alt.Color(field="Year", type="nominal"),
        radius=alt.Radius(field="Demand", scale=alt.Scale(type="sqrt", zero=True, rangeMin=20)),
    ).properties(
        title='Historical Demand Comparison (Radial)',
        width=400,
        height=400
    )
    return chart


def model_performance_heatmap(data):
    """
    Heatmap chart displaying model performance metrics
    """
    st.subheader("Model Performance Heatmap")
    performance_data = pd.DataFrame(data['model_performance'].items(), columns=['Metric', 'Value'])
    performance_data['Model'] = performance_data['Metric'].apply(lambda x: x.split('_')[0])
    performance_data['Metric'] = performance_data['Metric'].apply(lambda x: x.split('_')[-1])

    chart = alt.Chart(performance_data).mark_rect().encode(
        x='Metric:O',
        y='Model:O',
        color='Value:Q',
        tooltip=['Model', 'Metric', 'Value']
    ).properties(
        title='Model Performance Heatmap',
        width=300,
        height=200
    )
    return chart


def progress_bar():
    """
    Progress bar
    """
    progress_text = "Please wait..."
    progress_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1, text=progress_text)


def show_stock_forecast_page():
    """
    Main function to display the stock forecast and charts visualization
    """
    st.title("Optimal Stock Forecast")

    #User's input for medication name
    medication_name = st.text_input("Enter the medication name:")

    if st.button("Generate Forecast"):
        if medication_name:
            progress_bar()   #Call the progress bar

            #Fetch stock forecast data
            stock_forecast_data = get_stock_forecast(medication_name)

            if stock_forecast_data:
                #Display charts & tables with forecast data
                create_metric_columns(stock_forecast_data)
                model_performance_table(stock_forecast_data)
                heatmap_chart = model_performance_heatmap(stock_forecast_data)
                st.altair_chart(heatmap_chart, use_container_width=True)
                radial_chart = radial_historical_chart(stock_forecast_data)
                st.altair_chart(radial_chart, use_container_width=True)
                stock_details_table(stock_forecast_data)
                stock_distribution_chart(stock_forecast_data)
                prediction_overview_chart(stock_forecast_data)

            else:
                st.error("Unable to retrieve data for this medication.")
        else:
            st.warning("Please enter a medication name.")


if __name__ == "__main__":
    show_stock_forecast_page()