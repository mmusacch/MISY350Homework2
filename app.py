import streamlit as st

st.set_page_config(page_title="Smart Coffee Kiosk Application")
st.title("Smart Coffee Kiosk Application")

import json
from pathlib import Path

json_file = Path("inventory.json")

if json_file.exists():
    with open(json_file, "r") as f:
        inventory = json.load(f)
else:
    # Default data if file doesn't exist
    inventory = [] 

if "orders" not in st.session_state:
    st.session_state["orders"] = []
###Section 1

tab1, tab2, tab3, tab4 = st.tabs(["Place Order", "View Inventory", "Restock", "Manage Orders"])

with tab1: 
    st.header("Place Order")

    with st.container(border=True):
        item_names = []
        for item in inventory:
            item_names.append(item["name"])
    selected_item=st.selectbox("Select Item", item_names)
    quantity = st.number_input("Quantity")
    customer_name = st.text_input("Customer Name")

    if st.button("Place Order"):
        found_item = None

        for item in inventory: 
            if item["name"] ==selected_item:
                found_item = item
                break
        if found_item:
            #check back again
            if found_item["stock"] >= quantity:
                found_item["stock"] = found_item["stock"] - quantity
                total_price = found_item["price"] * quantity

                order = {
                    "order_id": len(st.session_state["orders"]) + 1,
                    "customer": customer_name,
                    "item": selected_item,
                    "quantity":quantity,
                    "total": total_price,
                    "status":"Placed"
                }

#Section 2
with tab2: 
    st.subheader("View & Search Inventory")
    search_query = st.text_input("Search items by name", placeholder="Latte, Espresso...",
                                  key="search_bar")
    filtered_inventory = []

    for item in inventory: 
        if search_query in item["name"]: 
            filtered_inventory.append(item)

            total_stock = item["stock"] 
            st.metric("Total Items in Stock", total_stock) 

    for item in filtered_inventory:
        if item["stock"] < 10:
            st.warning("Low Stock")

    with st.container(border=True):
        st.markdown("## Inventory")
        st.dataframe(inventory)
            

#Section 3

with tab3:
    st.header("Restock Inventory")

    item_names = item["name"]
    restock_item = st.selectbox("Select Item", item_names)
    restock_amount = st.number_input("Add Stock Amount")
    restock_button = st.button("Restock Item")
    if restock_button: 
        for item in inventory: 
            if item["name"] == restock_item: 
                item["stock"] += restock_amount 
                break 
        with inventory.open("W",encoding="utf-8") as f: 
            json.dump(inventory, f) 
        st.success("Inventory updated successfully!")


#Section 4

with tab4:
    st.header("Manage Orders")
    if len(st.session_state["orders"]) == 0: 
        st.info("No orders placed yet")
    else:
        st.subheader("Active Orders")
        st.dataframe(st.session_state["orders"])
        order_ids = order["order_id"]
        selected_order_id = st.selectbox( "Select Order to Cancel", order_ids, key="cancel_order" )
        cancel_order = st.button("Cancel Order")
        if cancel_order:
            selected_order = None
            for order in st.session_state["orders"]:
                if order["order_id"] == selected_order_id: 
                    selected_order = order 
                    break

        if selected_order and selected_order["status"] == "Placed":
            # return stock
            for item in inventory:
                if item["name"] == selected_order["item"]: 
                    item["stock"] += selected_order["quantity"] 
            selected_order["status"] = "Cancelled"
            with json_file.open("w", encoding="utf-8") as f:
                json.dump(inventory, f)
            st.success("Order Cancelled and Stock Refunded")    