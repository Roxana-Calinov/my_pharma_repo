"""
The relationship between the medication stock quantity and the stock level throw scatter plot and bar chart visualization
"""
from utils import get_medications_and_pharmacies
import pandas as pd      #data manipulation & visualization
import streamlit as st
import altair as alt     #data visualization


def quantity_vs_stock_level_chart():
    """
    Quantity vs. stock level
    """
    st.subheader("Stock Quantity vs. Stock Level Overview")

    #Fetch medications and pharmacies data
    response = get_medications_and_pharmacies()

    if response.status_code == 200:
        data = response.json()
        all_medications = []

        #Extract informations from response
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
            }
            all_medications.append(med_data)

        #Convert medications list to DataFrame
        df_all_medications = pd.DataFrame(all_medications)

        #Check if the DataFrame is not empty
        if not df_all_medications.empty:
            source = df_all_medications.copy()

            #Map stock levels to categories
            source['stock_level'] = source['stock_level'].astype('category')
            brush = alt.selection_interval()

            #Create a scatter plot with brush interaction
            points = alt.Chart(source).mark_circle(opacity=0.5).encode(
                x=alt.X('name:N', title='Medication'),
                y=alt.Y('stock:Q', title='Stock'),
                color=alt.Color('stock_level:N', title="Stock Level",
                                scale=alt.Scale(domain=["low", "medium", "high"],
                                                range=["red", "orange", "green"])),
                tooltip=['name:N', 'stock:Q', 'stock_level:N']
            ).add_params(brush)

            #Create a bar chart to display count of stock levels filtered by brush
            bars = alt.Chart(source).mark_bar().encode(
                x=alt.Y('stock_level:N', title='Stock Level'),
                y=alt.X('count():Q', title='Number of Medications'),
                color='stock_level:N'
            ).transform_filter(brush)

            #Combine both charts
            chart = points & bars

            #Create Streamlit tabs with different themes
            tab1, tab2 = st.tabs(["Streamlit theme (default)", "Altair native theme"])

            with tab1:
                st.altair_chart(chart, theme="streamlit", use_container_width=True)
            with tab2:
                st.altair_chart(chart, theme=None, use_container_width=True)

            #Stock level threshold
            st.markdown("### Stock Level Threshold:")
            st.markdown("- **Low**: 0-100 units")
            st.markdown("- **Medium**: 101-350 units")
            st.markdown("- **High**: 351 and above")
        else:
            st.error("No data available to generate the chart.")
    else:
        st.error("Error fetching data.")


if __name__ == "__main__":
    quantity_vs_stock_level_chart()
