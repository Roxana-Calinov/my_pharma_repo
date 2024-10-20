"""
Orders page - manage orders data

Main components:
-> CRUD (Create, Read, Update, Delete for orders data
-> Display analytics on best-selling medications (per pharmacy)
-> Order status management
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go           #Used for creating interactive plots
from plotly.subplots import make_subplots   #Used for creating subplots
from utils import (get_all_orders, get_order, create_order, update_order, update_order_status, delete_order, OrderStatus,
                   get_all_medications)


def show_best_selling_medication():
    """
    Best-selling medications per pharmacy

    The function retrieves all orders & medications and processes the data to determine the best-selling medication for
    each pharmacy.
    Plot a pie chart using Plotly showing the percentage comparison between the best-selling medication and other
    medications per each pharmacy.
    """
    st.subheader("Best-Selling Medication per Pharmacy")

    #Fetch all orders
    with st.spinner("Loading order..."):
        orders = get_all_orders().json()

    if not orders:
        st.write("There are no orders.")
        return

    #Convert orders to DataFrame
    df_orders = pd.DataFrame(orders)

    #Expand the order_items column
    df_items = df_orders.explode('order_items')
    df_items['medication_id'] = df_items['order_items'].apply(lambda x: x['medication_id'])
    df_items['quantity'] = df_items['order_items'].apply(lambda x: x['quantity'])

    #Group by pharmacy_id and medication_id, sum the quantities
    df_grouped = df_items.groupby(['pharmacy_id', 'medication_id'])['quantity'].sum().reset_index()

    #Fetch all medications
    with st.spinner("Loading medication..."):
        medications = get_all_medications().json()

    #Create a dictionary by mapping medication's ID to medication's name
    medication_names = {med['id']: med['name'] for med in medications}

    #Add medication names to DataFrame
    df_grouped['medication_name'] = df_grouped['medication_id'].map(medication_names)

    #Create subplots for each pharmacy
    fig = make_subplots(rows=1, cols=3, specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]],
                        subplot_titles=("Pharma A", "Pharma B", "Pharma C"))

    colors = ['#00CED1', '#FFA500', '#8B0000', '#00008B', '#FF99CC', '#00CED1']

    for i, pharmacy_id in enumerate([1, 2, 3], start=1):
        pharmacy_data = df_grouped[df_grouped['pharmacy_id'] == pharmacy_id]

        #Best-selling medication
        best_selling = pharmacy_data.loc[pharmacy_data['quantity'].idxmax()]

        #Total quantity per pharmacy
        total_quantity = pharmacy_data['quantity'].sum()

        #Quantity for "Other medications"
        other_quantity = total_quantity - best_selling['quantity']

        labels = [best_selling['medication_name'], 'Other medications']
        values = [best_selling['quantity'], other_quantity]

        fig.add_trace(go.Pie(labels=labels, values=values, name=f"Pharma {pharmacy_id}",
                             marker_colors=colors), 1, i)

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title_text="Best-Selling Medication vs. Other Medications",
        height=500,
        width=900,
    )

    st.plotly_chart(fig)


def show_orders_page():
    """
    Main function to display the orders management

    Menu for order's management
    """
    st.subheader("Orders: Stock & Details")
    menu = ["View All Orders", "View Specific Order", "Add New Order", "Update Order", "Update Order Status",
            "Delete Order", "Best Selling Medication"]
    choice = st.selectbox("Select an option", menu)

    if choice == "View All Orders":
        view_all_orders()
    elif choice == "View Specific Order":
        view_order()
    elif choice == "Add New Order":
        add_order()
    elif choice == "Update Order":
        init_update_order()
    elif choice == "Update Order Status":
        init_update_order_status()
    elif choice == "Delete Order":
        init_delete_order()
    elif choice == "Best Selling Medication":
        show_best_selling_medication()


#Display all orders
def view_all_orders():
    """
    Display all available orders
    """
    st.subheader("All Orders")
    with st.spinner("Loading orders..."):
        orders = get_all_orders().json()

    if not orders:
        st.write("There are no orders.")
        return

    #Convert orders to DF
    df_order = pd.DataFrame(orders)

    #Convert order_items to string
    df_order['order_items'] = df_order['order_items'].apply(lambda items: ', '.join(
        [f"Medication ID: {item['medication_id']}, Quantity: {item['quantity']}, Price: {item['price']}" for item in items]
    ))

    #Create a new column for pharmacy name
    pharmacy_names = {1: "Pharma A", 2: "Pharma B", 3: "Pharma C"}
    df_order['pharmacy_name'] = df_order['pharmacy_id'].map(pharmacy_names)

    #Reorder columns for adding pharmacy_name after pharmacy_id
    columns = df_order.columns.tolist()
    columns.insert(columns.index('pharmacy_id') + 1, columns.pop(columns.index('pharmacy_name')))
    df_order = df_order[columns]

    #Display the DF as a table
    st.dataframe(df_order)


#View a specific order by its ID
def view_order():
    """
    Display details about a specific order based on the user's input
    """
    st.subheader("View Order Details")
    st.write("Enter the order ID below to display its details.")

    #Input field for order ID
    order_id = st.number_input("Order ID", min_value=1, step=1, value=1,
                                    help="Enter the ID of the order you want to view.")

    #Submit button
    if st.button("View Order"):
        #Fetch order details based on ID
        order = get_order(order_id)
        order_json = order.json()

        if order.status_code == 200:
            #Display order details
            st.subheader(f"Order ID: {order_json['id']}")
            st.write(f"**Pharmacy ID**: {order_json['pharmacy_id']}")
            st.write(f"**Order Date**: {order_json['order_date']}")
            st.write(f"**Status**: {order_json['status']}")
            st.write(f"**Total Amount**: {order_json['total_amount']}")

            #Extract and display order items
            order_items = order_json['order_items']  # Extract order_items
            st.write("**Order Items:**")
            for item in order_items:
                st.write(
                    f"- Medication ID: {item['medication_id']}, Quantity: {item['quantity']}, Price: {item['price']}"
                )
        else:
            #Display an error if the order is not found
            st.error(f"Order with ID {order_id} not found.")


#Add a new order
def add_order():
    """
    Form for adding order
    """
    st.subheader("Add New Order")
    st.write("Fill in the details below to add a new order to the system.")

    if 'order_items' not in st.session_state:
        st.session_state['order_items'] = []

    #Collect order items (outside the form)
    with st.expander("Add Medication"):
        medication_id = st.number_input("Medication ID", min_value=1, step=1, help="Enter the medication ID.")
        quantity = st.number_input("Medication order quantity", min_value=1, step=1,
                                   help="Enter the quantity of medication")
        if st.button("Add Item"):
            st.session_state['order_items'].append({"medication_id": medication_id, "quantity": quantity})
            st.success(f"Added medication {medication_id} with quantity {quantity}")

    #Display current order items
    if st.session_state['order_items']:
        st.write("Current Order Items:")
        for item in st.session_state['order_items']:
            st.write(f"Medication ID: {item['medication_id']}, Quantity: {item['quantity']}")

    with st.form(key='add_order_form'):
        pharmacy_id = st.number_input("Pharmacy ID", min_value=1, step=1)
        status = st.selectbox("Order Status", options=[status.value for status in OrderStatus],
                              help="Choose the status of the order",
                              placeholder="pending")
        #Submit button
        submit_button = st.form_submit_button(label="Add Order", use_container_width=True)

    if submit_button:
        valid, message = validate_order_input(pharmacy_id, st.session_state['order_items'], status)
        if not valid:
            st.error(message)
        else:
            result = create_order(pharmacy_id, st.session_state['order_items'], status)
            if result.status_code == 200:
                st.success(f"Order added successfully with ID: {result.json()['id']}")
                st.session_state['order_items'] = []   #Clear the items after a successful order
            else:
                st.error("Failed to add order. Please try again.")

#Validate order input
def validate_order_input(pharmacy_id, order_items, status):
    """
    Validate input for creating/updating an order
    """
    if not all([pharmacy_id, order_items, status]) or len(order_items) == 0:
        return False, "Invalid data."
    else:
        return True, ""


#Update an existing order
def init_update_order():
    """
    Form for order update
    """
    st.subheader("Update Order")
    st.write("Enter the order ID and updated details below.")

    if 'order_items' not in st.session_state:
        st.session_state['order_items'] = []

    #Collect order items (outside the form)
    with st.expander("Update Medication Quantity"):
        medication_id = st.number_input("Medication ID", min_value=1, step=1, help="Enter the medication ID.")
        quantity = st.number_input("Medication order quantity", min_value=1, step=1,
                                   help="Enter the quantity of medication")
        if st.button("Add Item"):
            st.session_state['order_items'].append({"medication_id": medication_id, "quantity": quantity})
            st.success(f"Updated medication {medication_id} with quantity {quantity}")

    #Form for updating order details
    with st.form(key='update_order_form'):
        order_id = st.number_input("Order ID", min_value=1, step=1, help="Enter the order ID you want to update.")
        pharmacy_id = st.number_input("Pharmacy ID", min_value=1, step=1, help="Enter the pharmacy ID.")

        #Display current order items
        st.write("Order Items to Update:")
        for item in st.session_state['order_items']:
            st.write(f"Medication ID: {item['medication_id']}, Quantity: {item['quantity']}")

        status = st.selectbox("Order Status", ["pending", "loading", "delivered"],
                              help="Choose the status of the order")
        #Submit button
        submit_button = st.form_submit_button(label="Update Order")

    #Action on form submission
    if submit_button:
        valid, message = validate_order_input(pharmacy_id, st.session_state['order_items'], status)
        if not valid:
            st.error(message)
        else:
            #Update the order
            result = update_order(order_id, pharmacy_id, st.session_state['order_items'], status)
            if result.status_code == 200:
                st.success(f"Order updated successfully with ID: {order_id}")
                st.session_state['order_items'] = []   #Clear items after a successful update
            else:
                st.error("Failed to update order. Please try again.")


#Update order status
def init_update_order_status():
    """
    Form for update order's status
    """
    st.subheader("Update Order Status")
    st.write("Enter the order ID and the new status below.")

    with st.form(key='update_order_status_form'):
        order_id = st.number_input("Order ID", min_value=1, step=1)
        new_status = st.selectbox("Order Status", ["pending", "processed", "delivered"],
                              help="Choose the order status")
        submit_button = st.form_submit_button("Update Status")

    if submit_button:
        if not new_status:
            st.warning("Please enter a new status.")
            return

        result = update_order_status(order_id=order_id, new_status=new_status)

        if result is None:
            st.error("Unexpected error.")
        elif result.status_code == 200:
            st.success(f"Order updated successfully with ID: {order_id}")
        else:
            st.error(f"Failed to update order. Status code: {result.status_code}")
            st.error(f"Error message: {result.text}")


#Delete an order by its ID
def init_delete_order():
    """
    Form for deleting an order
    """
    st.subheader("Delete Order")
    st.write("Enter the order ID you want to delete below.")

    #Form for deleting an order
    with st.form(key='delete_order_form'):
        order_id = st.number_input("Order ID", min_value=1, step=1,
                                   help="Enter the ID of the order you want to delete.")

        #Submit button
        submit_button = st.form_submit_button(label="Delete Order")

    #Action on form submission
    if submit_button:
        result = delete_order(order_id)
        if result.status_code == 200:
            st.success(f"Order with ID {order_id} deleted successfully.")
        else:
            st.error(f"Failed to delete order with ID {order_id}. Please try again.")

