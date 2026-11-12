import threading
import time
import streamlit as st

# Set page configuration for a responsive dashboard
st.set_page_config(
    page_title="Warehouse / Store Inventory and Order System",
    page_icon="📦",
    layout="wide",
)

# Initialize Session State for Inventory & Logs
if "inventory" not in st.session_state:
    st.session_state.inventory = {
        "Wireless Gaming Mouse": {"stock": 5, "price": 49.99, "threshold": 2},
        "Mechanical Keyboard": {"stock": 1, "price": 89.99, "threshold": 2},  # Ideal for race condition stress testing!
        "USB-C Hub": {"stock": 10, "price": 25.50, "threshold": 3},
        "HD Monitor": {"stock": 2, "price": 199.99, "threshold": 1},
    }

if "logs" not in st.session_state:
    st.session_state.logs = []

# Global Mutex Lock for Thread Synchronization (OS Concept)
inventory_lock = threading.Lock()

# App Header matching Project Scope
st.title("📦 Warehouse / Store Inventory and Order System")
st.markdown(
    "**Product 7 | OS Project Demonstration:** Preventing race conditions and overselling during concurrent user checkouts using **Mutex Locks (`threading.Lock`)**."
)
st.markdown("---")

# --- SIDEBAR: CONCURRENT ORDER SIMULATOR ---
st.sidebar.header("⚙️ Concurrent Order Simulator")
st.sidebar.markdown(
    "Simulate multiple customers trying to purchase the last units of a product simultaneously to test race conditions."
)

selected_product = st.sidebar.selectbox(
    "Select Product to Stress Test:", list(st.session_state.inventory.keys())
)
num_threads = st.sidebar.slider("Number of Concurrent Customer Threads", min_value=2, max_value=5, value=3)
use_mutex = st.sidebar.checkbox("Enable Mutex Protection (Safe Mode)", value=True)

def simulate_purchase(product_name, customer_id, use_lock):
    """Critical section handling stock check and deduction under a mutex lock"""
    if use_lock:
        inventory_lock.acquire()
    
    try:
        # Simulate slight network/processing delay to expose potential race conditions when unlocked
        time.sleep(0.1)
        
        current_stock = st.session_state.inventory[product_name]["stock"]
        
        if current_stock > 0:
            # Critical Section: Deduct stock
            st.session_state.inventory[product_name]["stock"] -= 1
            msg = f"✅ [{customer_id}] Successfully purchased **{product_name}**. Remaining Stock: {st.session_state.inventory[product_name]['stock']}"
        else:
            msg = f"❌ [{customer_id}] Failed to purchase **{product_name}** - Out of Stock (Overselling Prevented!)"
            
        st.session_state.logs.insert(0, msg)
    
    finally:
        if use_lock:
            inventory_lock.release()

if st.sidebar.button("🚀 Run Concurrent Purchase Simulation", type="primary"):
    mode_text = "Safe (Mutex Protected)" if use_mutex else "Unsafe (Race Condition Vulnerable)"
    st.session_state.logs.insert(
        0, f"--- Simulation started for '{selected_product}' with {num_threads} threads | Mode: {mode_text} ---"
    )
    st.toast(f"{mode_text} mode activated.", icon="✅" if use_mutex else "⚠️")
    
    threads = []
    for i in range(1, num_threads + 1):
        customer_name = f"Customer-{i}"
        t = threading.Thread(
            target=simulate_purchase, 
            args=(selected_product, customer_name, use_mutex)
        )
        threads.append(t)
        t.start()
        
    # Wait for all threads to complete join()
    for t in threads:
        t.join()

    final_status = "Simulation completed safely with mutex protection." if use_mutex else "Simulation completed in unsafe mode; race-condition risk is active."
    st.toast(final_status, icon="🔒" if use_mutex else "⚠️")
        
    st.rerun()

if st.sidebar.button("🔄 Reset Inventory"):
    st.session_state.inventory = {
        "Wireless Gaming Mouse": {"stock": 5, "price": 49.99, "threshold": 2},
        "Mechanical Keyboard": {"stock": 1, "price": 89.99, "threshold": 2},
        "USB-C Hub": {"stock": 10, "price": 25.50, "threshold": 3},
        "HD Monitor": {"stock": 2, "price": 199.99, "threshold": 1},
    }
    st.session_state.logs = ["Inventory reset to default values."]
    st.rerun()

# --- MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Unique Implementation Feature: Product Catalogue & Low-Stock Display")
    st.markdown("Browse catalog items, view live inventory metrics, check low-stock alerts, or restock items dynamically.")
    
    # Display products in responsive cards with low-stock logic
    for prod, details in st.session_state.inventory.items():
        with st.container(border=True):
            cols = st.columns([3, 1, 1, 1])
            cols[0].markdown(f"### {prod}")
            cols[1].metric("Price", f"${details['price']:.2f}")
            
            stock_val = details['stock']
            threshold = details['threshold']
            
            # Low-stock display feature implementation
            if stock_val == 0:
                cols[2].error("Out of Stock")
            elif stock_val <= threshold:
                cols[2].warning(f"Low Stock: {stock_val}")
            else:
                cols[2].success(f"In Stock: {stock_val}")
                
            # Restocking feature implementation
            if cols[3].button(f"Restock", key=f"restock_{prod}"):
                st.session_state.inventory[prod]["stock"] += 5
                st.session_state.logs.insert(0, f"📦 Admin restocked '{prod}' (+5 units added).")
                st.rerun()

with col2:
    st.subheader("📊 Live Transaction & OS Logs")
    log_box = st.container(height=420, border=True)
    with log_box:
        if not st.session_state.logs:
            st.info("No transaction logs yet. Run a simulation from the sidebar.")
        else:
            for log in st.session_state.logs:
                st.markdown(log)

# Footer Information mapping directly to project specifications
st.markdown("---")
st.markdown("### 🔍 OS Rubric Mapping Summary")
info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.info("**Main OS Concept:**\n\nRace conditions and `threading.Lock()` mutex synchronization.")
with info_col2:
    st.warning("**Main Problem Being Solved:**\n\nPreventing concurrent orders from incorrectly reducing stock or causing overselling.")
with info_col3:
    st.success("**Unique Implementation Features:**\n\nProduct catalogue, purchase execution, stock deduction, restocking, and dynamic low-stock warnings.")