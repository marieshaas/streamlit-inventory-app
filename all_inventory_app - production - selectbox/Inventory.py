import streamlit as st
import os
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
from barcode import Code128
from barcode.writer import ImageWriter
import time
import re

# Load data
@st.cache_data
def load_data():
    stocklist_prod = pd.read_csv('data/tbl_stock_prod.csv', dtype={'Item No': str})
    transaction = pd.read_csv('data/tbl_transaction_prod.csv', dtype={'Item No': str})
    rfid_scan = pd.read_csv('data/rfid_user.csv', dtype={'rfid_id': str})
    authorized_user =pd.read_csv('data/authorized_user.csv', dtype={'rfid id': str})
    unit_list = pd.read_excel("data/tempat_stock.xlsx")
    return stocklist_prod, transaction, rfid_scan, authorized_user, unit_list

stocklist_prod, transaction, rfid_scan, authorized_user, unit_list = load_data()

# Load CSS
def load_css(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('style.css')

#if 'last_global_refresh' not in st.session_state:
#   st.session_state.last_global_refresh = time.time()


#def check_global_refresh():
 #   current_time = time.time()
  #  refresh_interval = 15 * 60  # 15 menit 
    
   # if current_time - st.session_state.last_global_refresh > refresh_interval:
    #    st.session_state.last_global_refresh = current_time
     #   st.rerun()


#check_global_refresh()

# Inisialisasi session state
if 'dialog_shown' not in st.session_state:
    st.session_state.dialog_shown = False
if 'rfid_input' not in st.session_state:
    st.session_state.rfid_input = ''
if 'last_processed_id' not in st.session_state:
    st.session_state.last_processed_id = None
if 'selected_item' not in st.session_state:
    st.session_state.selected_item = None
if 'item_name' not in st.session_state:
    st.session_state.item_name = None
if 'qty' not in st.session_state:
    st.session_state.qty = None
if 'purpose' not in st.session_state:
    st.session_state.purpose = None
if 'waiting_for_scan' not in st.session_state:
    st.session_state.waiting_for_scan = False
if 'person_in_charge' not in st.session_state:
    st.session_state.person_in_charge = None
if 'transaction' not in st.session_state:
    st.session_state.transaction = transaction.copy()
if 'stocklist_prod' not in st.session_state:
    st.session_state.stocklist_prod = stocklist_prod.copy()
if 'pending_transaction_index' not in st.session_state:
    st.session_state.pending_transaction_index = None
if 'pending_stock_index' not in st.session_state:
    st.session_state.pending_stock_index = None
if 'scan_result' not in st.session_state:
    st.session_state.scan_result = None
if 'input_value' not in st.session_state:
    st.session_state.input_value = ""
if 'page' not in st.session_state:
    st.session_state.page = "Main Page"
if 'transaction_type' not in st.session_state:
    st.session_state.transaction_type = None
if 'dialog_active' not in st.session_state:
    st.session_state.dialog_active = False
if 'scan' not in st.session_state:
    st.session_state.scan = False
if 'unit' not in st.session_state:
    st.session_state.unit = False
if 'confirm' not in st.session_state:
    st.session_state.confirm = False
if 'type' not in st.session_state:
    st.session_state.type = None
if 'machine' not in st.session_state:
    st.session_state.machine = None
if 'price' not in st.session_state:
    st.session_state.price = None
if 'no_hri' not in st.session_state:
    st.session_state.no_hri = False
if 'scan_authorized' not in st.session_state:
    st.session_state.scan_authorized = False
if 'scan_authorized_purpose' not in st.session_state:
    st.session_state.scan_authorized_purpose = None


# Header 
st.title('Production Inventory')

# Functions for barcode and image handling
def generate_code128_barcode(next_item_number):
    buffer = io.BytesIO()
    
    writer = ImageWriter()
    
    options = {
        'module_width': 0.8,
        'module_height': 2.0,
        'font_size': 0,
        'text_distance': 5.0,
        'write_text': False,
        'quiet_zone': 6.0
    }
    
    Code128(next_item_number, writer=writer).write(buffer, options=options)
    
    buffer.seek(0)
    image = Image.open(buffer)
    
    width = 40 * 30
    height = 15 * 30
    image = image.resize((width, height))
    
    return image

def add_text_to_code128_barcode(barcode_image, next_item_number, new_item_type):
    width, height = barcode_image.size

    padding_top = 200
    padding_bottom = 120
    new_height = height + padding_top + padding_bottom
    new_image = Image.new("RGB", (width, new_height), (255, 255, 255))
    new_image.paste(barcode_image, (0, padding_top))
    draw = ImageDraw.Draw(new_image)
    
    try:
        name_font = ImageFont.truetype("arialbd.ttf", 75)
        number_font = ImageFont.truetype("arialbd.ttf", 80)
    except:
        name_font = ImageFont.load_default()
        number_font = ImageFont.load_default()

    name_text = str(new_item_type)
    chars_per_line = 15
    
    lines = []
    for i in range(0, len(name_text), chars_per_line):
        line = name_text[i:i+chars_per_line]
        lines.append(line)
    
    y_position = 130
    line_height = 90

    for line in lines:
        try:
            line_bbox = name_font.getbbox(line)
            line_width = line_bbox[2] - line_bbox[0]
        except (AttributeError, TypeError):
            try:
                line_width = name_font.getsize(line)[0]
            except:
                line_width = len(line) * 30
        
        x_position = (width - line_width) // 2
        draw.text((x_position, y_position), line, fill=(0, 0, 0), font=name_font)
        y_position += line_height
    
    number_text = str(next_item_number)
    try:
        number_bbox = number_font.getbbox(number_text)
        number_width = number_bbox[2] - number_bbox[0]
    except (AttributeError, TypeError):
        try:
            number_width = number_font.getsize(number_text)[0]
        except:
            number_width = len(number_text) * 30
    
    number_position = ((width - number_width) // 2, padding_top + height - 100)
    draw.text(number_position, number_text, fill=(0, 0, 0), font=number_font)
    
    return new_image

def save_code128_barcode_image(barcode_image, next_item_number):
    barcode_dir = "barcode_images"
    if not os.path.exists(barcode_dir):
        os.makedirs(barcode_dir)
    
    filename = os.path.join(barcode_dir, f"{next_item_number}_code128.png")
    barcode_image.save(filename)
    
    return True, f"Barcode saved as {filename}"

def save_uploaded_image(uploaded_file, next_item_number):
    try:
        image = Image.open(uploaded_file)
                                                                          
        if image.mode == 'RGBA':
            image = image.convert('RGB')
            
        max_size = (800, 800)  
        image.thumbnail(max_size, Image.LANCZOS)
        
        save_path = os.path.join("item_images", f"{next_item_number}.jpg")
        image.save(save_path, "JPEG", quality=85)
        return True, "Image saved successfully"
    except Exception as e:
        return False, str(e)
    
@st.dialog('Add New Item')
def new_product():
    st.session_state.stocklist_prod['Item No'] = st.session_state.stocklist_prod['Item No'].astype(str).str.zfill(13)
    try:  
        if not st.session_state.stocklist_prod.empty and 'Item No' in st.session_state.stocklist_prod.columns:
            existing_numbers = st.session_state.stocklist_prod['Item No']
            
            max_numeric_value = max(int(num) for num in existing_numbers)
            
            next_item_number = f"{max_numeric_value + 1:013d}"
        else:
            # If no existing items, start with the first number
            next_item_number = "0000000000001"
    except Exception as e:
        st.error(f"Error generating item number: {e}")
        next_item_number = "0000000000001"
        
        
    st.write(f"Item Number: **{next_item_number}**")

    barcode_image = generate_code128_barcode(next_item_number)

    new_item_name = st.text_input("New Item Name", value=None)

    new_item_type = st.text_input("Type:", value=None)

    if new_item_type:
        item_machine = st.text_input("Machine", value=None)
        add_no_hri = st.text_input("No HRI", value=None)
        new_item_quantity = st.number_input("Beginning Quantity", min_value=0, step=1, value=0, placeholder='0')
        min_qty = st.number_input("Minimum Quantity", min_value=0, step=1, value=0, placeholder='0')
        unit_options = [x for x in unit_list['DAFTAR UNIT'].unique() if pd.notna(x)]
        selected_unit = st.selectbox("Select Unit of Your Item", options=unit_options)
        st.warning("Gunakan titik penanda puluhan, ratusan atau ribuah")
        item_price = st.number_input(
        "Item Price", min_value=0, value=0, step=1000, placeholder="Rp10.000"
        )

        uploaded_file = st.file_uploader("Upload Product Image", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, caption=f"will be saved as {next_item_number}.jpg", width=200)
        
            
        button_col1, button_col2 = st.columns(2, gap="large")
        with button_col1:
            if st.button("Cancel", key="cancel_dialog", type="primary"):
                st.rerun()
        
        with button_col2:
            if st.button("Confirm", key="confirm_dialog_new"):
                if new_item_name:
                    success = True
                    message = ""
                    if uploaded_file:
                        success, message = save_uploaded_image(uploaded_file, next_item_number)
                        if success:
                            st.success(f"Image uploaded successfully as {next_item_number}.jpg")
                        else:
                            st.error(f"Failed to save image: {message}")
                            return 
                    
                    if st.session_state.stocklist_prod.empty or 'No' not in st.session_state.stocklist_prod.columns:
                        new_item_num = 1
                    else:
                        last_item_no = st.session_state.stocklist_prod['No'].max() 
                        new_item_num = int(last_item_no) + 1 if not pd.isna(last_item_no) else 1
                    
                    new_stock_data = pd.DataFrame({
                        'No': [new_item_num],
                        'Item No': [str(next_item_number)],  
                        'Item Name': [new_item_name],
                        'Type': [new_item_type],
                        'Machine': [item_machine],
                        'Quantity': [new_item_quantity],
                        'Unit': [selected_unit],
                        'No HRI': [add_no_hri],
                        'Minimum Stock Qty': [min_qty],
                        'Price': [item_price]
                    })
                    
                    st.session_state.pending_stock_data = new_stock_data
                    st.session_state.pending_stock_index = 0
                    
                    if new_item_quantity > 0:
                        current_date = datetime.today().strftime('%Y-%m-%d')
                        new_trans_data = pd.DataFrame({
                            'Date': [current_date],
                            'Item No': [str(next_item_number)],
                            'No HRI': [add_no_hri],
                            'Item Name': [new_item_name],
                            'Type': [new_item_type],
                            'Machine': [item_machine],
                            'Unit': [selected_unit],
                            'Purpose': "-",
                            'Status': ['new'],
                            'Received Qty': [new_item_quantity],
                            'Issued Qty': "0",
                            'Price': [item_price],
                            'Person in Charge': [st.session_state.scan_result['id_name'] if st.session_state.get('scan_result') else None]
                        })

                        st.session_state.transaction = pd.concat([st.session_state.transaction, new_trans_data], ignore_index=True)
                        st.session_state.pending_transaction_index = len(st.session_state.transaction) - 1
                        st.session_state.waiting_for_scan = False
                        st.session_state.dialog_shown = False 
                        st.session_state.page = "Confirm Transaction" 
                        st.rerun()
                else:
                    st.error("Please enter item name")
            
@st.dialog('Add Item')
def add_product():   
    st.session_state.transaction_type = "add"
    scanned_item = st.text_input("Scan Item Number:", value=None)
    if scanned_item:
        if scanned_item in stocklist_prod['Item No'].values:
            item_name = stocklist_prod.loc[stocklist_prod['Item No'] == scanned_item, 'Item Name'].values[0]
            st.session_state.item_name = item_name
            st.text(f"Selected Item: \n {item_name}")

            item_row = stocklist_prod[stocklist_prod['Item No'] == scanned_item].iloc[0]
            no_hri = item_row['No HRI']
            st.write(f"No HRI: {no_hri}")   

            current_stock = stocklist_prod.loc[stocklist_prod['Item No'] == scanned_item, 'Quantity'].values[0]
            st.success(f"**Available Stock**: {current_stock}")
            
            current_type = stocklist_prod.loc[stocklist_prod['Item No'] == scanned_item, 'Type'].values[0]
            st.write(f"type: {current_type}")

            image_path = os.path.join("item_images", f"{scanned_item}.jpg")
            if os.path.exists(image_path):
                st.image(image_path, width=100)
            else:
                st.warning("No image found for this item")

            machine = stocklist_prod.loc[stocklist_prod['Item No'] == scanned_item, 'Machine'].values[0]
            st.session_state.machine = machine

            unit = stocklist_prod.loc[stocklist_prod['Item No'] == scanned_item, 'Unit'].values[0]
            st.session_state.unit = unit

            qty = st.number_input("Enter Quantity:", min_value=1, step=1)
            st.session_state.qty = qty

            purpose = st.text_input("Purpose:", value=None)
            st.session_state.purpose = purpose
            
            price = stocklist_prod.loc[stocklist_prod['Item No'] == scanned_item, 'Price'].values[0]
            st.session_state.price = price
            
            button_col1, button_col2 = st.columns(2)
            with button_col1:
                if st.button("Cancel", key="cancel_dialog_add", type="primary"):
                    st.rerun()
            with button_col2:
                if st.button("Confirm", key="confirm_dialog_add"):
                    st.session_state.selected_item = scanned_item
                    status = "in"
                    iss_qty= "0"
                    current_date = datetime.today().strftime('%Y-%m-%d')
                    new_data = pd.DataFrame({
                        'Date': [current_date],
                        'Item No': [scanned_item],
                        'No HRI': [no_hri],
                        'Item Name': [item_name],
                        'Type': [current_type],
                        'Machine': [machine],
                        'Unit': [unit],  
                        'Purpose': [purpose],
                        'Status': [status],
                        'Received Qty': [qty],
                        'Issued Qty' : [iss_qty],
                        'Price': [price],
                        'Person in Charge': [st.session_state.scan_result['id_name'] if st.session_state.get('scan_result') else None]
                    })
                    
                    st.session_state.transaction = pd.concat([st.session_state.transaction, new_data], ignore_index=True)
                    st.session_state.pending_transaction_index = len(st.session_state.transaction) - 1
                    st.session_state.waiting_for_scan = False
                    st.session_state.dialog_shown = False
                    st.session_state.page = "Confirm Transaction"
                    st.rerun()
        else:
            st.error("Item number not found in stock list")

            
@st.dialog('Edit Item')
def edit_item():
    item_options = stocklist_prod['Item No'].tolist()
    selected_item_num = st.selectbox("Select Item to Edit", options=item_options)
    
    selected_row = stocklist_prod[stocklist_prod['Item No'] == selected_item_num].iloc[0]

    item_name = selected_row['Item Name']
    no_hri = selected_row['No HRI']
    item_type = selected_row['Type']
    machine = selected_row['Machine']
    current_quantity = selected_row['Quantity']
    price = selected_row['Price']
    
    image_path = os.path.join("item_images", f"{selected_item_num}.jpg")
    if os.path.exists(image_path):
        st.image(image_path, caption=f"Current Image", width=200)
    else:
        st.info("No image available for this item")

    new_item_num = st.text_input("Item Number", value=selected_item_num)
    new_item_name = st.text_input("Item Name", value=item_name)
    new_no_hri = st.text_input("No HRI", value=no_hri)
    new_item_type = st.text_input("Type", value=item_type)
    new_machine = st.text_input("Machine", value=machine)
    new_quantity = st.number_input("Quantity", value=current_quantity, min_value=0, step=1)
    new_price = st.number_input("Price", value=price, min_value=0, step=10000)
    current_threshold = selected_row['Minimum Stock Qty'] if 'Minimum Stock Qty' in selected_row else 0
    new_threshold = st.number_input("Minimum Stock Threshold", value=current_threshold, min_value=0, step=1)
    unit_options = [x for x in unit_list['DAFTAR UNIT'].unique() if pd.notna(x)]
    selected_unit = st.selectbox("Select Unit of Your Item", options=unit_options)
    new_unit = selected_unit
    barcode_image = generate_code128_barcode(new_item_num)

    if new_item_type:
        final_barcode = add_text_to_code128_barcode(barcode_image, selected_item_num, new_item_type)
        st.image(final_barcode, caption=f"Current Barcode: {selected_item_num}", width=300)
            
    
    st.subheader("Update Image (Optional)")
    new_image = st.file_uploader("Upload New Image", type=['png', 'jpg', 'jpeg'])
    if new_image:
        st.image(new_image, caption="New Image Preview", width=200)
        
    button_col1, button_col2 = st.columns(2, gap="large")
    with button_col1:
        if st.button("Cancel", key="cancel_edit", type="primary"):
            st.rerun() 
    with button_col2:
        if st.button("Save Changes", key="save_edit"):
            if new_image:
                success, message = save_uploaded_image(new_image, new_item_num)
                if success:
                    st.success(f"Image updated")
                else:
                    st.error(f"Failed to update image: {message}")
            
            idx = stocklist_prod[stocklist_prod['Item No'] == selected_item_num].index[0]
            stocklist_prod.at[idx, 'Item No'] = new_item_num
            stocklist_prod.at[idx, 'No HRI'] = new_no_hri
            stocklist_prod.at[idx, 'Item Name'] = new_item_name
            stocklist_prod.at[idx, 'Type'] = new_item_type
            stocklist_prod.at[idx, 'Machine'] = new_machine
            stocklist_prod.at[idx, 'Quantity'] = new_quantity
            stocklist_prod.at[idx, 'Price'] = new_price
            stocklist_prod.at[idx, 'Unit'] = new_unit
            stocklist_prod.at[idx, 'Minimum Stock Qty'] = new_threshold
            
            stocklist_prod.to_csv('data/tbl_stock_prod.csv', index=False)
            st.session_state.stocklist_prod = stocklist_prod
            st.success("Item updated")
            # Clear cache to reload data
            st.cache_data.clear()
            st.rerun()
        
    #with button_col3:
      #  if st.button("",icon=":material/delete:", type="primary"):
@st.dialog('Delete Item')
def delete_item():
    item_options = stocklist_prod['Item No'].tolist()
    selected_item_num = st.selectbox("Select Item to Delete", options=item_options)
    
    selected_row = stocklist_prod[stocklist_prod['Item No'] == selected_item_num].iloc[0]
    no_hri = selected_row['No HRI']
    item_name = selected_row['Item Name']
    type_value = selected_row['Type']
    current_quantity = selected_row['Quantity']

    st.warning(f"You are about to delete: **{item_name}** (Item No: **{selected_item_num}**)")
    st.info(f"Current Quantity: {current_quantity}")
    
    image_path = os.path.join("item_images", f"{selected_item_num}.jpg")
    if os.path.exists(image_path):
        st.image(image_path, caption="Item Image", width=150)
    
    button_col1, button_col2 = st.columns(2)
    with button_col1:
        if st.button("Cancel", key="cancel_delete", type="primary"):
            st.rerun()
    
    with button_col2:
        if st.button("Delete Item", key="confirm_delete", type="secondary"):
            stocklist_updated = stocklist_prod[stocklist_prod['Item No'] != selected_item_num]
            stocklist_updated['No'] = range(1, len(stocklist_updated) + 1)
            stocklist_updated.to_csv('data/tbl_stock_prod.csv', index=False)
            st.session_state.stocklist_prod = stocklist_updated
        
            if os.path.exists(image_path):
                try:
                    os.remove(image_path) 
                    st.success(f"Image file {selected_item_num}.jpg removed")
                except Exception as e:
                    st.error(f"Could not remove image file: {e}")
            
            st.success(f"Item {item_name} deleted")
            
            current_date = datetime.today().strftime('%Y-%m-%d')
            delete_record = pd.DataFrame({
                'Date': [current_date],
                'Item No': [selected_item_num],
                'No HRI': [no_hri],
                'Item Name': [item_name],
                'Type': ["-"],
                'Machine': ["-"],
                'Unit': ["-"],
                'Purpose': ["item deleted"],
                'Status': ["deleted"],
                'Received Qty': [0],
                'Issued Qty': [current_quantity],
                'Price': ["-"],
                'Person in Charge': [st.session_state.get('person_in_charge', 'Admin')]
            })
            
            st.session_state.transaction = pd.concat([st.session_state.transaction, delete_record], ignore_index=True)
            st.session_state.transaction.to_csv('data/tbl_transaction_prod.csv', index=False)
            
            
            st.cache_data.clear()
            st.rerun()

@st.dialog("Confirm Transaction")
def confirm():
    st.session_state.dialog_active = True 
    if ('transaction' in st.session_state and 
    st.session_state.transaction is not None and 
    not st.session_state.transaction.empty and
    st.session_state.pending_transaction_index is not None and
    0 <= st.session_state.pending_transaction_index < len(st.session_state.transaction)):
        
        transaction_data = st.session_state.transaction.iloc[st.session_state.pending_transaction_index]
        
        st.write(f"**Item No:** {transaction_data['Item No']}")
        st.write(f"**No HRI:** {transaction_data['No HRI']}")
        st.write(f"**Selected Item:** {transaction_data['Item Name']}")
        st.write(f"**Type:** {transaction_data['Type'].upper()}")
        st.write(f"**Machine:** {transaction_data['Machine'].upper()}")
        st.write(f"**Status:** {transaction_data['Status'].upper()}")
        st.write(f"**Received Quantity:** {transaction_data['Received Qty']}")
        st.write(f"**Issued Quantity:** {transaction_data['Issued Qty']}")
        st.write(f"**Price:** Rp {transaction_data['Price']}")
        st.write(f"**Unit:** {transaction_data['Unit']}")
        st.write(f"**Purpose:** {transaction_data['Purpose']}")

        # Cek apakah person in charge sudah ada (dari authorized scan)
        if transaction_data['Person in Charge'] is not None and transaction_data['Person in Charge'] != '':
            st.info(f"**Person in Charge:** {transaction_data['Person in Charge']}")
            person_already_scanned = True
        elif st.session_state.get('scan_result'):
            st.info(f"**Person in Charge:** {st.session_state.scan_result['id_name']}")
            person_already_scanned = True
        else:
            st.warning("ID Card Not Scanned Yet")
            person_already_scanned = False
            
        # Show barcode for new items
        if transaction_data['Status'] == 'new':
            item_no = transaction_data['Item No']
            item_type = transaction_data['Type']
            
            # Generate barcode
            barcode_image = generate_code128_barcode(item_no)
            final_barcode = add_text_to_code128_barcode(barcode_image, item_no, item_type)
            
            st.subheader("Item Barcode")
            st.image(final_barcode, caption=f"Barcode for {item_no}: {transaction_data['Item Name']}", width=300)

        button_col1, button_col2 = st.columns(2)

        with button_col1:
            if st.button("Cancel Transaction", key="cancel_transaction_confirm", type="primary"):
                if 'pending_stock_data' in st.session_state:
                    del st.session_state.pending_stock_data
                st.session_state.pending_stock_index = None
                st.session_state.pending_transaction_index = None  
                st.session_state.scan_result = None
                st.session_state.input_value = ""
                st.session_state.waiting_for_scan = False
                st.session_state.dialog_shown = False
                st.session_state.page = "Main Page" 
                st.rerun()

        with button_col2:
            if person_already_scanned:
                if st.button("Confirm Transaction", key="confirm_transaction_dialog"):
                    idx = st.session_state.pending_transaction_index
                    
                    # Get person in charge
                    if transaction_data['Person in Charge'] is not None and transaction_data['Person in Charge'] != '':
                        id_name = transaction_data['Person in Charge']
                    else:
                        id_name = st.session_state.scan_result['id_name']
                        st.session_state.transaction.at[idx, 'Person in Charge'] = id_name

                    item_no = st.session_state.transaction.at[idx, 'Item No']
                    type = st.session_state.transaction.at[idx, 'Type']
                    status = st.session_state.transaction.at[idx, 'Status']
                    rcv_qty = st.session_state.transaction.at[idx, 'Received Qty']
                    iss_qty = st.session_state.transaction.at[idx, 'Issued Qty']
                    

                    if rcv_qty == "0":
                        qty = int(iss_qty) if isinstance(iss_qty, str) else iss_qty
                    elif iss_qty == "0":
                        qty = int(rcv_qty) if isinstance(rcv_qty, str) else rcv_qty

                    if st.session_state.get('pending_stock_data') is not None:
                        st.session_state.stocklist_prod = pd.concat(
                            [st.session_state.stocklist_prod, st.session_state.pending_stock_data], 
                            ignore_index=True
                        )
                    
                    if status == "out":
                        st.session_state.stocklist_prod.loc[st.session_state.stocklist_prod['Item No'] == item_no, 'Quantity'] -= qty
                    elif status == "in":
                        st.session_state.stocklist_prod.loc[st.session_state.stocklist_prod['Item No'] == item_no, 'Quantity'] += qty
                    elif status == "new":
                        pass

                    st.session_state.stocklist_prod.to_csv('data/tbl_stock_prod.csv', index=False)
                    st.session_state.transaction.to_csv('data/tbl_transaction_prod.csv', index=False)

                    if 'pending_stock_data' in st.session_state:
                        del st.session_state.pending_stock_data
                    st.session_state.pending_stock_index = None
                    st.session_state.pending_transaction_index = None
                    st.session_state.scan_result = None
                    st.session_state.waiting_for_scan = False
                    st.session_state.person_in_charge = id_name
                    st.session_state.dialog_shown = False
                    st.session_state.page = "Main Page"
                    
                    # Reload data
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.button("Confirm Transaction", key="confirm_transaction_disabled", disabled=True)
    else:
        if st.session_state.get('pending_transaction_index') is None:
            st.error("No pending transaction index found.")
        elif not isinstance(st.session_state.pending_transaction_index, (int, np.integer)):
            st.error(f"Transaction index is not an integer: {type(st.session_state.pending_transaction_index)}")
        else:
            st.error(f"Transaction index {st.session_state.pending_transaction_index} is out of bounds. Transaction list has {len(st.session_state.transaction)} records.")
        
        if st.button("Back to Main Page", key="back_to_main_confirm"):
            st.session_state.dialog_shown = False
            st.session_state.page = "Main Page"
            st.rerun()

@st.dialog("Scan ID Card")
def scan():
    st.session_state.dialog_active = True 
    st.info("Please place your ID card near the scanner")
    
    # Inisialisasi session state 
    if 'input_value' not in st.session_state:
        st.session_state.input_value = ""
    if 'force_process' not in st.session_state:
        st.session_state.force_process = False
    if 'last_processed_id' not in st.session_state:
        st.session_state.last_processed_id = ""
    
    if 'dialog_just_opened' not in st.session_state or st.session_state.dialog_just_opened:
        st.session_state.input_value = ""
        st.session_state.dialog_just_opened = False
    
    id_code = st.text_input("Scan RFID Card", key='rfid_input', 
                          label_visibility="collapsed", value=st.session_state.input_value)
    
    # Fungsi untuk memproses ID
    def process_rfid(rfid_code):
        if not rfid_code:
            return False
            
        formatted_id = str(rfid_code).zfill(10)
        matched_user = rfid_scan[rfid_scan['rfid_id'] == formatted_id]
        
        if not matched_user.empty:
            id_name = matched_user['nama'].iloc[0]
            
            st.session_state.scan_result = {
                'id_code': formatted_id,
                'id_name': id_name
            }
            st.success(f"ID Verified: **{id_name}**")
            
            st.info("Directing to confirmation page...")
            st.session_state.page = "Confirm Transaction"
            st.session_state.dialog_shown = False
            time.sleep(0.5)  
            return True
        else:
            st.error("Card not registered!")
            # Reset input untuk scan baru
            st.session_state.input_value = ""
            return False
    
    button_col1, button_col2 = st.columns(2)

    with button_col1:
        # Tombol cancel
        cancel_button = st.button("Cancel", key="cancel_scan_button", type="primary")
        if cancel_button:
            # Reset semua status
            st.session_state.pending_transaction_index = None
            st.session_state.scan_result = None
            st.session_state.input_value = ""
            st.session_state.waiting_for_scan = False
            st.session_state.force_process = False
            if 'pending_stock_data' in st.session_state:
                del st.session_state.pending_stock_data
            st.session_state.pending_stock_index = None
            st.session_state.dialog_shown = False
            st.session_state.page = "Main Page"
            st.rerun()

    with button_col2:
        # Tombol verify untuk pemrosesan manual
        scan_button = st.button("Verify", key="manual_scan_button")
        if scan_button:
            if id_code:
                if process_rfid(id_code):
                    st.rerun()
            else:
                st.warning("Please scan or enter RFID first")
    
    # Proses otomatis saat RFID discan 
    if id_code and id_code != st.session_state.last_processed_id:
        st.session_state.last_processed_id = id_code
        if process_rfid(id_code):
            st.rerun()
    
    # test_button = st.button("Debug: Force Rerun")
    # if test_button:
    #     st.warning("Forcing rerun...")
    #     st.session_state.force_process = True
    #     st.rerun()
    
    if id_code and st.session_state.scan_result is None:
        st.session_state.input_value = id_code

@st.dialog('Authorized Scan')
def scan_authorized():
    st.session_state.dialog_active = True 
    st.info("Please place your ID card near the scanner")
    
    if 'input_value' not in st.session_state:
        st.session_state.input_value = ""
    if 'force_process' not in st.session_state:
        st.session_state.force_process = False
    if 'last_processed_id' not in st.session_state:
        st.session_state.last_processed_id = ""
    
    # Reset input value setiap kali dialog dibuka
    if 'dialog_just_opened' not in st.session_state or st.session_state.dialog_just_opened:
        st.session_state.input_value = ""
        st.session_state.dialog_just_opened = False
    
    # Input field untuk scan RFID
    id_code = st.text_input("Scan RFID Card", key='rfid_input', 
                        label_visibility="collapsed", value=st.session_state.input_value)
    
    # Fungsi untuk memproses ID
    def process_rfid(rfid_code):
        if not rfid_code:
            return False
            
        formatted_id = str(rfid_code).zfill(10)
        matched_user = authorized_user[authorized_user['rfid id'] == formatted_id]
        
        if not matched_user.empty:
            id_name = matched_user['nama'].iloc[0]
            
            st.session_state.scan_result = {
                'id_code': formatted_id,
                'id_name': id_name
            }
            st.success(f"ID Verified: **{id_name}**")
            
            if st.session_state.scan_authorized_purpose == "delete":
                st.session_state.page = "Delete Item"
            elif st.session_state.scan_authorized_purpose == "edit":
                st.session_state.page = "Edit Item"
            elif st.session_state.scan_authorized_purpose == "add item":
                st.session_state.page = "Add Item"
            elif st.session_state.scan_authorized_purpose == "new":
                st.session_state.page = "Add New Item"

            st.session_state.dialog_shown = False
            time.sleep(0.5)  
            return True
        else:
            st.error("Card not registered!")
            # Reset input untuk scan baru
            st.session_state.input_value = ""
            return False

    button_col1, button_col2 = st.columns(2)  

    with button_col1:
        # Tombol cancel
        cancel_button = st.button("Cancel", key="cancel_scan_button", type="primary")
        if cancel_button:
            # Reset semua status
            st.session_state.pending_transaction_index = None
            st.session_state.scan_result = None
            st.session_state.input_value = ""
            st.session_state.waiting_for_scan = False
            st.session_state.force_process = False
            st.session_state.scan_authorized_purpose = None
            if 'pending_stock_data' in st.session_state:
                del st.session_state.pending_stock_data
            st.session_state.pending_stock_index = None
            st.session_state.dialog_shown = False
            st.session_state.page = "Main Page"
            st.rerun()

    with button_col2:
        # Tombol verify 
        scan_button = st.button("Verify", key="manual_scan_button")
        if scan_button:
            if id_code:
                if process_rfid(id_code):
                    st.rerun()
            else:
                st.warning("Please scan or enter RFID first")

    if id_code and id_code != st.session_state.last_processed_id:
        st.session_state.last_processed_id = id_code
        if process_rfid(id_code):
            st.rerun()
        
    if id_code and st.session_state.scan_result is None:
        st.session_state.input_value = id_code

# Handle dialog states
if st.session_state.page == "Authorized Scan" and not st.session_state.dialog_shown:
    st.session_state.scan_authorized = True
    st.session_state.dialog_shown = True
    scan_authorized()
elif st.session_state.page == 'Delete Item' and not st.session_state.dialog_shown:
    st.session_state.delete_item = True
    st.session_state.dialog_shown = True
    delete_item()
elif st.session_state.page == 'Edit Item' and not st.session_state.dialog_shown:
    st.session_state.edit_item = True 
    st.session_state.dialog_shown = True
    edit_item()
elif st.session_state.page == 'Add Item' and not st.session_state.dialog_shown:
    st.session_state.add_product = True
    st.session_state.dialog_shown = True
    add_product()
elif st.session_state.page == 'Add New Item' and not st.session_state.dialog_shown:
    st.session_state.new_product = True
    st.session_state.dialog_shown = True
    new_product()
elif st.session_state.page == "Confirm Transaction" and not st.session_state.dialog_shown:
    st.session_state.confirm = True
    st.session_state.dialog_shown = True
    confirm()
elif st.session_state.page == "Scan ID Card" and not st.session_state.dialog_shown:
    st.session_state.scan = True
    st.session_state.dialog_shown = True
    scan()

if st.session_state.page == "Main Page":
    st.session_state.dialog_shown = False

tab1, tab2 = st.tabs(["Stock List", "Transaction History"])

with tab1:
    # Stock display with search functionality
    search = st.text_input("Search by Name or Type:", value=None, placeholder="Search item here")

    if search:
        # Filter berdasarkan item name
        filtered_by_name = stocklist_prod[stocklist_prod['Item Name'].str.contains(search, case=False, na=False)]
        # Filter berdasarkan type
        filtered_by_type = stocklist_prod[stocklist_prod['Type'].str.contains(search, case=False, na=False)]
        # Gabungkan hasil kedua filter 
        filtered_stocklist = pd.concat([filtered_by_name, filtered_by_type]).drop_duplicates()
        
        empty_rows = pd.DataFrame([[""] * len(stocklist_prod.columns)] * 8, columns=stocklist_prod.columns)
        final_display = pd.concat([filtered_stocklist, empty_rows], ignore_index=True)
    else:
        final_display = stocklist_prod

    final_display = final_display.set_index('No')
    st.dataframe(final_display, use_container_width=True, height=350)
    
    # Take and add item buttons
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        if st.button("Take Item", use_container_width=True, icon=":material/upload:"):
            @st.dialog('Take Out Product')
            def takeout_product():
                st.session_state.transaction_type = "takeout"
                scanned_item = st.text_input("Scan Item Number:", value=None)
                if scanned_item:
                    if scanned_item in stocklist_prod['Item No'].values:
                        item_name = stocklist_prod.loc[stocklist_prod['Item No'] == scanned_item, 'Item Name'].values[0]
                        st.session_state.item_name = item_name
                        st.text(f'Selected Item: \n {item_name}')

                        item_row = stocklist_prod[stocklist_prod['item no'] == scanned_item].iloc[0]
                        no_hri = item_row['No HRI']
                        st.write(f"No HRI: {no_hri}")                            
                        
                        current_stock = stocklist_prod.loc[stocklist_prod['item no'] == scanned_item, 'quantity'].values[0]
                        st.success(f"**Available Stock**: {current_stock}")

                        current_type = stocklist_prod.loc[stocklist_prod['item no'] == scanned_item, 'type'].values[0]
                        st.write(f"type: {current_type}")

                        price = stocklist_prod.loc[stocklist_prod['Item No'] == scanned_item, 'Price'].values[0]
                        st.write(f"price: {price}")
                        
                        image_path = os.path.join("item_images", f"{scanned_item}.jpg")
                        if os.path.exists(image_path):
                            st.image(image_path, width=100)
                        else:
                            st.warning("No image found for this item")
                        
                        machine = stocklist_prod.loc[stocklist_prod['Item No'] == scanned_item, 'Machine'].values[0]
                        st.session_state.machine = machine

                        unit = stocklist_prod.loc[stocklist_prod['Item No'] == scanned_item, 'Unit'].values[0]
                        st.session_state.unit = unit

                        qty = st.number_input("Enter Quantity:", min_value=1, step=1)
                        st.session_state.qty = qty

                        purpose = st.text_input("Purpose:", value=None)
                        st.session_state.purpose = purpose

                        button_col1, button_col2 = st.columns(2, gap="medium")
                        with button_col1:
                            if st.button("Cancel", key="cancel_dialog_take", type="primary"):
                                st.rerun()
                        with button_col2:
                            if st.button("Confirm", key="confirm_dialog_take"):
                             if qty > current_stock:
                                st.error(f"Insufficient stock! Available: {current_stock}, Requested: {qty}")
                             else:
                                st.session_state.selected_item = scanned_item
                                status = "out"
                                rcv_qty = "0"
                                current_date = datetime.today().strftime('%Y-%m-%d')
                                new_data = pd.DataFrame({
                                    'Date': [current_date],
                                    'Item No': [scanned_item],
                                    'No Hri': [no_hri],
                                    'Item Name': [item_name],
                                    'Type': [current_type],
                                    'Machine': [machine],
                                    'Unit': [unit],
                                    'Purpose': [purpose],
                                    'Status': [status],
                                    'Received Qty': [rcv_qty], 
                                    'Issued Qty': [qty],
                                    'Price': [price], 
                                    'Person in Charge': [None]
                                })
                                st.session_state.transaction = pd.concat([st.session_state.transaction, new_data], ignore_index=True)
                                st.session_state.pending_transaction_index = len(st.session_state.transaction) - 1
                                st.session_state.waiting_for_scan = True
                                st.session_state.dialog_shown = False
                                st.session_state.page = "Scan ID Card"
                                st.rerun()
                    else:
                        st.error("Item number not found in stock list")

            takeout_product()
        
            if st.session_state.waiting_for_scan and not st.session_state.dialog_shown:
                st.session_state.dialog_shown = True
                scan()

    with col2:
        if st.button("Add Item", use_container_width=True, icon=":material/library_add:"):
           st.session_state.scan_authorized_purpose = "add item"
           st.session_state.page = "Authorized Scan"
           st.rerun() 

    #if st.session_state.waiting_for_scan and not st.session_state.dialog_shown:
     #   st.session_state.dialog_shown = True
      #  scan()
        
    #if not os.path.exists('item_images'):
     #   os.makedirs('item_images')

   
    button_col1, button_col2, button_col3 = st.columns([18.5, 2, 1])

    with button_col1:  
        if st.button("Add New Item ", use_container_width=True, icon=":material/add_box:"):
            st.session_state.scan_authorized_purpose = "new"
            st.session_state.page = "Authorized Scan"
            st.rerun()

            #if st.session_state.waiting_for_scan and not st.session_state.dialog_shown:
             #   st.session_state.dialog_shown = True
              #  scan()

    with button_col2:
        if st.button("Edit", icon=":material/edit_note:"):
            st.session_state.scan_authorized_purpose = "edit"
            st.session_state.page = "Authorized Scan"
            st.rerun()

    with button_col3:
        if st.button("",icon=":material/delete:", type="primary"):
            st.session_state.scan_authorized_purpose = "delete"
            st.session_state.page = "Authorized Scan"
            st.rerun()

with tab2:
    st.subheader("Transaction History")
        
    date_col, status_col, item_col = st.columns(3)
    
    with date_col:
        # Filter berdasarkan tanggal
        date_options = ["All Dates"] + sorted(st.session_state.transaction['Date'].unique().tolist(), reverse=True)
        selected_date = st.selectbox("Filter by Date:", options=date_options)
    
    with status_col:
        # Filter berdasarkan status
        status_options = ["All Status"] + sorted(st.session_state.transaction['Status'].unique().tolist())
        selected_status = st.selectbox("Filter by Status:", options=status_options)
    
    with item_col:
        # Filter berdasarkan item name/number
        item_search = st.text_input("Search Item Name/Number:", key="transaction_item_search")
    
    filtered_transaction = st.session_state.transaction.copy()
    
    if selected_date != "All Dates":
        filtered_transaction = filtered_transaction[filtered_transaction['Date'] == selected_date]
    
    if selected_status != "All Status":
        filtered_transaction = filtered_transaction[filtered_transaction['Status'] == selected_status]
    
    if item_search:
        filtered_by_name = filtered_transaction[filtered_transaction['Item Name'].str.contains(item_search, case=False, na=False)]
        filtered_by_type = filtered_transaction[filtered_transaction['Type'].str.contains(item_search, case=False, na=False)]
        
        filtered_transaction = pd.concat([filtered_by_name, filtered_by_type]).drop_duplicates()
    
    if not filtered_transaction.empty:
        filtered_transaction['Date'] = filtered_transaction['Date'].astype(str)
        filtered_transaction = filtered_transaction.sort_values(by='Date', ascending=False)
        
        def highlight_status(val):
            if val == 'in':
                return 'background-color: #c6efce; color: #006100'
            elif val == 'out':
                return 'background-color: #ffc7ce; color: #9c0006'
            elif val == 'new':
                return 'background-color: #ffeb9c; color: #9c6500'
            elif val == 'deleted':
                return 'background-color: #d9d9d9; color: #666666'
            return ''
        
        st.dataframe(
            filtered_transaction.style.applymap(highlight_status, subset=['Status']), 
            use_container_width=True, 
            height=400
        )
    
        
st.markdown("---")
st.markdown("Inventory Management System © 2025")