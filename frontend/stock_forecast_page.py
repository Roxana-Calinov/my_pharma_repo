import streamlit as st
import pandas as pd
import numpy as np
import requests
from utils import get_stock_forecast
import plotly.graph_objects as go


def show_stock_forecast_page():
    st.title("Optimal Stock Forecast")

    medication_name = st.text_input("Enter the medication name:")

    if st.button("Generate Forecast"):
        if medication_name:
            data = get_stock_forecast(medication_name)

            if data:
                #Display main information
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Stock", f"{data.get('total_current_stock', 'N/A')} units")
                col2.metric("Predicted Demand", f"{data.get('predicted_monthly_demand', 'N/A')} units")
                col3.metric("Recommended Order", f"{data.get('recommended_order_quantity', 'N/A')} units")

                #Historical comparison chart
                if 'historical_comparison' in data:
                    historical_data = data['historical_comparison']
                    years = list(historical_data.keys())
                    values = list(historical_data.values())

                    fig = go.Figure(data=[go.Bar(x=years, y=values)])
                    fig.update_layout(title="Historical Demand Comparison", xaxis_title="Year", yaxis_title="Units")
                    st.plotly_chart(fig)
                else:
                    st.info("Historical comparison data not available.")

                #Additional details table
                details = {
                    "Metric": ["Central Stock", "Pharmacy Stock", "Safety Stock"],
                    "Value": [
                        data.get('current_central_stock', 'N/A'),
                        data.get('current_pharmacy_stock', 'N/A'),
                        data.get('safety_stock', 'N/A')
                    ]
                }

                #Add RF and XGB predictions if available
                if 'rf_xgb_prediction' in data:
                    details["Metric"].append("RF/XGB Prediction")
                    details["Value"].append(data['rf_xgb_prediction'])

                st.table(pd.DataFrame(details))

                #Display model performance
                if 'model_performance' in data:
                    st.subheader("Model Performance")
                    for model, performance in data['model_performance'].items():
                        st.text(f"{model}: {performance:.4f}")
                else:
                    st.info("Model performance data not available.")

            else:
                st.error("Unable to retrieve data for this medication.")
        else:
            st.warning("Please enter a medication name.")


if __name__ == "__main__":
    show_stock_forecast_page()