import streamlit as st
import pandas as pd
from utils import get_all_orders, get_order, create_order, update_order, update_order_status, delete_order, OrderStatus


def show_orders_page():
    st.subheader("Orders: Stock & Details")
    menu = ["View All Orders", "View Specific Order", "Add New Order", "Update Order", "Update Order Status",
            "Delete Order"]
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


#Display all orders
def view_all_orders():
    st.subheader("All Orders")
    with st.spinner("Loading orders..."):
        orders = get_all_orders().json()

    if not orders:
        st.write("There are no orders.")
        return

    #Convert orders to DF
    df_order = pd.DataFrame(orders)

    #Convert order_items to string representation
    df_order['order_items'] = df_order['order_items'].apply(lambda items: ', '.join(
        [f"Medication ID: {item['medication_id']}, Quantity: {item['quantity']}, Price: {item['price']}" for item in items]
    ))

    #Display the DF as a table
    st.dataframe(df_order)


#View a specific order by its ID
def view_order():
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
                st.session_state['order_items'] = []  # Clear the items after a successful order
            else:
                st.error("Failed to add order. Please try again.")

#Validate order input
def validate_order_input(pharmacy_id, order_items, status):
    if not all([pharmacy_id, order_items, status]) or len(order_items) == 0:
        return False, "Invalid data."
    else:
        return True, ""

#Update an existing order
def init_update_order():
    st.subheader("Update Order")
    st.write("Enter the order ID and updated details below.")

    if 'order_items' not in st.session_state:
        st.session_state['order_items'] = []

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

    #Collect order items (outside the form)
    with st.expander("Update Medication Quantity"):
        medication_id = st.number_input("Medication ID", min_value=1, step=1, help="Enter the medication ID.")
        quantity = st.number_input("Medication order quantity", min_value=1, step=1,
                                   help="Enter the quantity of medication")
        if st.button("Add Item"):
            st.session_state['order_items'].append({"medication_id": medication_id, "quantity": quantity})
            st.success(f"Updated medication {medication_id} with quantity {quantity}")

    #Action on form submission
    if submit_button:
        valid, message = validate_order_input(pharmacy_id, st.session_state['order_items'], status)
        if not valid:
            st.error(message)
        else:
            #Update the order instead of creating a new one
            result = update_order(order_id, pharmacy_id, st.session_state['order_items'], status)
            if result.status_code == 200:
                st.success(f"Order updated successfully with ID: {order_id}")
                st.session_state['order_items'] = []  #Clear the items after a successful update
            else:
                st.error("Failed to update order. Please try again.")


#Update order status
def init_update_order_status():
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
            st.json(result.json())
        else:
            st.error(f"Failed to update order. Status code: {result.status_code}")
            st.error(f"Error message: {result.text}")


#Delete an order by its ID
def init_delete_order():
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


