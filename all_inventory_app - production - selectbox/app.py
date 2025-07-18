import streamlit as st
import pandas as pd
import os
import altair as alt
from datetime import datetime
import sys

# Konfigurasi halaman utama
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Pastikan folder data ada
if not os.path.exists('data'):
    os.makedirs('data')
    
# Pastikan folder untuk gambar ada
if not os.path.exists('item_images'):
    os.makedirs('item_images')
if not os.path.exists('barcode_images'):
    os.makedirs('barcode_images')

# Tambahkan CSS untuk styling
css = """
<style>
/* CSS Anda tetap sama */
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Sidebar setup

st.sidebar.markdown("<h1 style='text-align: center; color: #055bb4;'>Inventory Management</h1>", unsafe_allow_html=True)

# Menu selectbox di sidebar
menu_options = ["Home", "Production Inventory", "Monthly Report"]
selected_menu = st.sidebar.selectbox("Select Menu", menu_options, key="main_menu_sidebar")

# Inisialisasi data global
@st.cache_data
def load_data():
    try:
        stock_data = pd.read_csv('data/tbl_stock_prod.csv', dtype={'item no': str})
    except FileNotFoundError:
        # Buat file stock kosong jika belum ada
        stock_data = pd.DataFrame({
            'no': [],
            'item no': [],
            'item name': [],
            'type': [],
            'quantity': [],
            'place': []
        })
        stock_data.to_csv('data/tbl_stock_prod.csv', index=False)
    
    try:
        transaction_data = pd.read_csv('data/tbl_transaction_prod.csv')
    except FileNotFoundError:
        transaction_data = pd.DataFrame({
            'date': [],
            'item no': [],
            'item name': [],
            'type': [],
            'place': [],
            'purpose': [],
            'status': [],
            'received qty': [],
            'issued qty': [],
            'person in charge': []
        })
        transaction_data.to_csv('data/tbl_transaction_prod.csv', index=False)
    
    try:
        rfid_data = pd.read_csv('data/rfid_user.csv', dtype={'rfid_id': str})
    except FileNotFoundError:
        # Buat file RFID kosong jika belum ada
        rfid_data = pd.DataFrame({
            'rfid_id': [],
            'nama': []
        })
        rfid_data.to_csv('data/rfid_user.csv', index=False)
    
    try:
        place_data = pd.read_excel('data/tempat_stock.xlsx')
    except FileNotFoundError:
        # Buat file tempat stock kosong jika belum ada
        place_data = pd.DataFrame({
            'DAFTAR TEMPAT': ['LEMARI MERAH', 'LEMARI HITAM', 'LEMARI MS', 'RAK 1', 'RAK 2']
        })
        place_data.to_excel('data/tempat_stock.xlsx', index=False)
    
    return stock_data, transaction_data, rfid_data, place_data

# Initialize session state dengan data yang dimuat
stock_data, transaction_data, rfid_data, place_data = load_data()

if 'transaction' not in st.session_state:
    st.session_state.transaction = transaction_data.copy()

if 'stocklist_prod' not in st.session_state:
    st.session_state.stocklist_prod = stock_data.copy()

# Menampilkan konten berdasarkan menu
if selected_menu == "Home":
    from Home import render_home_page
    render_home_page(st.session_state.stocklist_prod)

elif selected_menu == "Production Inventory":
    st.empty()
    
    exec(open("Inventory.py").read())

elif selected_menu == "Monthly Report":
    from Monthly_Report import calculate_monthly_report
   
    st.title('Monthly Report')
    
    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 1))
    months = list(range(1, 13))
    month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 
                  6: 'June', 7: 'July', 8: 'August', 9: 'September', 
                  10: 'October', 11: 'November', 12: 'December'}
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_year = st.selectbox("Select Year", years, index=len(years)-1)
    
    with col2:
        selected_month = st.selectbox("Select Month", months, index=datetime.now().month-1, format_func=lambda x: month_names[x])
    
    if selected_year and selected_month:
        report_data = calculate_monthly_report(st.session_state.transaction, selected_year, selected_month, st.session_state.stocklist_prod)
        
        st.subheader(f"Monthly Report for {month_names[selected_month]} {selected_year}")
        
        if not report_data.empty:
            report_data['year'] = report_data['year'].astype(str)
            report_data['Item No'] = report_data['Item No'].astype(str)
            numeric_columns = ['Beginning Qty', 'Received Qty', 'Issued Qty', 'End Qty']
            for col in numeric_columns:
                report_data[col] = pd.to_numeric(report_data[col], errors='coerce')
                report_data[col] = report_data[col].astype('Int64')
            
            st.dataframe(report_data, use_container_width=True, height=500)
            
            # Download CSV
            csv = report_data.to_csv(index=False)
            st.download_button(
                label="**Download Report as CSV**",
                data=csv,
                file_name=f"Monthly_Report_{month_names[selected_month]}_{selected_year}.csv",
                mime="text/csv",
                type ="secondary",
                icon=":material/download:"
            )
        
        st.markdown("---")
        st.markdown("Inventory Management System © 2025")