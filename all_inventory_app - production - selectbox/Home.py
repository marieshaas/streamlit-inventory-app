import streamlit as st
import pandas as pd
from datetime import datetime

def render_home_page(stocklist):
    """
    Fungsi untuk merender halaman home
    """
    st.header("Selamat datang di Inventory Management System!")

    # Informasi sistem
    st.markdown("""
    Gunakan menu di sidebar sistem untuk mengakses:
    - **Production Inventory**
    - **Monthly Report**
    """)

    st.divider()
    final_display = stocklist.copy()
    final_display = final_display.set_index('No')
    
    # Peringatan jumlah item dengan stock minimum
    if 'Minimum Stock Qty' in final_display.columns:
        low_stock_items = final_display[(final_display['Minimum Stock Qty'] > 0) & (final_display['Quantity'] <= final_display['Minimum Stock Qty'])]
        if not low_stock_items.empty:
            st.warning(f"**⚠️ ({len(low_stock_items)}) barang sudah mencapai batas minimum stock!**")

    # highlight pada stock yang rendah
    display_copy = final_display.copy()
    if 'Minimum Stock Qty' in display_copy.columns:
        # Add low_stock column to flag items where quantity <= minimum stock qty
        display_copy['low_stock'] = display_copy.apply(
            lambda row: row['Quantity'] <= row['Minimum Stock Qty'] if row['Minimum Stock Qty'] > 0 else False, axis=1)
        
        # Filter for items where quantity <= minimum stock qty (low stock)
        display_view = display_copy[display_copy['low_stock'] == True].copy()
        
        # Hide 'low_stock' and 'minimum stock qty' columns from the view
        display_view = display_view.drop(columns=['low_stock'], errors='ignore')
        
        # Define styling function to highlight low stock items
        def highlight_low_stock(df):
            # Apply red background to all low stock items
            return pd.DataFrame(
                'background-color: #ffeded',
                index=df.index,
                columns=df.columns
            )
        
        # Display the DataFrame with Streamlit, applying the highlight
        st.dataframe(
            display_view.style.apply(
                highlight_low_stock,
                axis=None,
                subset=['Quantity', 'Item Name', 'Type', 'Unit', 'No HRI', 'Item No','Minimum Stock Qty']
            ),
            use_container_width=True,
            height=350
        )
    else:
        st.dataframe(final_display, use_container_width=True, height=350)

    st.divider()


    with st.expander("Tutorial Penggunaan Sistem Inventory", icon=":material/help:"):
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.subheader(":blue[1.] :grey[Ambil Barang]")
            try:
                st.image("take_item.jpeg", caption="Tombol Take Item", width=350)
            except:
                st.warning("Gambar take_item.jpeg tidak ditemukan")
            st.markdown("""
            Untuk mengambil barang dari inventory:
            1. Klik tombol **Take Item** di bawah tabel stock
            2. Scan atau masukkan nomor item
            3. Masukkan jumlah yang diambil
            4. Isi tujuan penggunaan
            5. Konfirmasi dengan tap ID card
            """)
            
            st.subheader(":blue[3.] :grey[Tambah Barang Baru]")
            try:
                st.image("addnew_item.jpeg", caption="Tombol Add New Item", width=370)
            except:
                st.warning("Gambar addnew_item.jpeg tidak ditemukan")
            st.markdown("""
            Untuk menambahkan barang baru ke sistem:
            1. Klik tombol **Add New Item** di bawah tabel stock
            2. Isi detail barang (nama, tipe, jumlah awal)
            3. Pilih lokasi penyimpanan
            4. Upload gambar produk jika tersedia
            5. Konfirmasi dengan tap ID card
            """)

            st.subheader(":blue[5.] :grey[Menghapus Data Barang]")
            try:
                st.image("delete_item.jpeg", caption="Tombol untuk Delete Item", width=200)
            except:
                st.warning("Gambar delete_item.jpeg tidak ditemukan")
            st.markdown("""
            Untuk menghapus barang di sistem:
            1. Klik tombol **Delete** di bawah tabel stock
            2. Isi nomor barang yang ingin dihapus
            """)

        with col2:
            st.subheader(":blue[2.] :grey[Tambah Stok Barang]")
            try:
                st.image("add_item.jpeg", caption="Tombol Add Item", width=350) 
            except:
                st.warning("Gambar add_item.jpeg tidak ditemukan")
            st.markdown("""
            Untuk menambah stok barang yang sudah ada:
            1. Klik tombol **Add Item** di bawah tabel stock
            2. Scan atau masukkan nomor item
            3. Masukkan jumlah tambahan
            4. Konfirmasi dengan tap ID card
            """)

            st.subheader(":blue[4.] :grey[Edit Data Barang]")
            try:
                st.image("edit_item.jpeg", caption="Tombol Edit Item", width=200)
            except:
                st.warning("Gambar edit_item.jpeg tidak ditemukan")
            st.markdown("""
            Untuk mengedit informasi barang:
            1. Klik tombol **Edit** di bawah tabel stock
            2. Pilih item yang akan diedit
            3. Ubah informasi yang diperlukan
            4. Update gambar produk jika perlu
            5. Simpan perubahan
            """)
            
    st.markdown("---")
    st.markdown("Inventory Management System © 2025")