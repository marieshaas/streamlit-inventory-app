## Inventory Management System

📦 Overview

A web-based inventory management system built with Streamlit for managing production stock with RFID authentication and barcode generation features. This system is specifically designed for production environments with multi-level access control and comprehensive transaction tracking.

## ✨ Key Features

### 🏠 Dashboard & Monitoring
- **Real-time Stock Monitoring**: Real-time stock display with warnings for minimum stock items
- **Search & Filter**: Search by item name or product type
- **Low Stock Alerts**: Automatic alerts for items reaching minimum threshold

### 📱 RFID Integration
- **Dual-Level Authentication**: 
  - Regular users for take/add item transactions
  - Authorized users for sensitive operations (edit, delete, add new item)
- **RFID Card Scanner**: Automatic input with 10-digit format

### 📊 Transaction Management
- **Take Item**: Remove items from inventory with stock validation
- **Add Item**: Add stock for existing items
- **Add New Item**: Register new items with automatic barcode generation
- **Edit Item**: Modify item data (authorized only)
- **Delete Item**: Remove items (authorized only)

### 🏷️ Barcode System
- **Code128 Barcode Generation**: Automatic barcode creation for new items
- **Custom Barcode Design**: Barcodes with product name and item number
- **Auto-numbering**: Automatic numbering system with 13-digit format

### 📈 Reporting
- **Monthly Reports**: Monthly reports with Beginning Qty, Received, Issued, and End Qty data
- **Transaction History**: Transaction history with filters by date, status, and item
- **CSV Export**: Export reports in CSV format

### 🖼️ Media Management
- **Product Images**: Upload and manage product images
- **Image Optimization**: Automatic resize with 85% JPEG quality
- **File Organization**: Organized folder structure for images and barcodes

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Data Storage**: CSV files
- **Image Processing**: Pillow (PIL)
- **Barcode Generation**: python-barcode
- **Data Manipulation**: Pandas
- **Styling**: Custom CSS

## 📁 Project Structure

```
inventory_ms_app/
├── app.py                    # Main application file
├── Home.py                   # Home page module
├── Inventory.py              # Core inventory management
├── Monthly_Report.py         # Report generation module
├── style.css                 # Custom CSS styling
├── run_streamlit.bat        # Windows batch file to run app
├── data/
│   ├── tbl_stock_prod.csv   # Stock data
│   ├── tbl_transaction_prod.csv # Transaction history
│   ├── rfid_user.csv        # RFID user database
│   ├── authorized_user.csv  # Authorized users database
│   └── tempat_stock.xlsx    # Storage locations & units
├── item_images/             # Product images directory
└── barcode_images/          # Generated barcodes directory
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd inventory_ms_app
   ```

2. **Install required packages**
   ```bash
   pip install streamlit pandas pillow python-barcode openpyxl
   ```

3. **Create required directories**
   ```bash
   mkdir data item_images barcode_images
   ```

4. **Setup initial data files**
   
   Create `data/rfid_user.csv`:
   ```csv
   rfid_id,nama
   0000000001,John Doe
   0000000002,Jane Smith
   ```

   Create `data/authorized_user.csv`:
   ```csv
   rfid id,nama
   0000000001,Admin User
   0000000003,Supervisor
   ```

   Create `data/tempat_stock.xlsx` with columns:
   - DAFTAR TEMPAT: Storage locations
   - DAFTAR UNIT: Unit types

5. **Run the application**
   ```bash
   streamlit run app.py
   ```
   
   Or use the batch file (Windows):
   ```bash
   run_streamlit.bat
   ```

## 📖 Usage Guide

### Basic Operations

#### Taking Items from Inventory
1. Click **"Take Item"** button
2. Scan or input item number
3. Enter quantity to take
4. Specify purpose/reason
5. Scan your RFID card for authentication
6. Confirm transaction

#### Adding Stock to Existing Items
1. Click **"Add Item"** button
2. Scan authorized RFID card
3. Scan or input item number
4. Enter quantity to add
5. Specify purpose
6. Scan user RFID card
7. Confirm transaction

#### Adding New Items
1. Click **"Add New Item"** button
2. Scan authorized RFID card
3. Fill in item details:
   - Item name, type, machine
   - HRI number, quantity, minimum stock
   - Unit, price
4. Upload product image (optional)
5. Scan user RFID card
6. Confirm - barcode will be generated automatically

### Advanced Operations

#### Editing Items
- Requires authorized RFID scan
- Modify any item details
- Update product images
- Change minimum stock thresholds

#### Deleting Items
- Requires authorized RFID scan
- Removes item from stock
- Creates deletion record in transaction history
- Removes associated image files

### Reporting

#### Monthly Reports
1. Go to **"Monthly Report"** tab
2. Select year and month
3. View comprehensive report with:
   - Beginning quantities
   - Received quantities
   - Issued quantities
   - End quantities
4. Download as CSV

## 🔧 Configuration

### RFID Setup
- RFID IDs are stored as 10-digit zero-padded strings
- Two user levels: regular users and authorized users
- Configure in respective CSV files

### Storage Locations
- Modify `tempat_stock.xlsx` to add new storage locations
- Update unit types as needed

### Barcode Customization
- Barcode format: Code128
- Auto-numbering starts from 0000000000001
- Custom styling with product name and number

## 🔒 Security Features

- **Two-tier Authentication**: Regular vs Authorized users
- **RFID Card Verification**: All transactions require RFID scan
- **Transaction Logging**: Complete audit trail
- **Authorized Operations**: Sensitive operations require special permissions

## 📊 Data Management

### CSV Structure

**Stock Data (tbl_stock_prod.csv)**
```
No,Item No,Item Name,Type,Machine,Quantity,Unit,HRI No,Minimum Stock Qty,Price
```

**Transaction Data (tbl_transaction_prod.csv)**
```
Date,Item No,HRI No,Item Name,Type,Machine,Unit,Purpose,Status,Received Qty,Issued Qty,Price,Person in Charge
```

### Status Types
- `in`: Item received/added to stock
- `out`: Item taken from stock
- `new`: New item created
- `deleted`: Item deleted from system

## 🎨 UI/UX Features

- **Responsive Design**: Adapts to different screen sizes
- **Color-coded Status**: Visual indicators for transaction types
- **Interactive Tables**: Sortable and filterable data views
- **Progress Indicators**: Real-time feedback for operations
- **Warning System**: Low stock and error notifications

## 🐛 Troubleshooting

### Common Issues

1. **RFID Card Not Recognized**
   - Ensure RFID ID is properly formatted (10 digits)
   - Check if user exists in respective CSV file

2. **Images Not Loading**
   - Verify `item_images` directory exists
   - Check file permissions
   - Ensure image files are in JPG format

3. **CSV Data Issues**
   - Verify CSV file structure matches expected format
   - Check for missing columns or data types

4. **Barcode Generation Fails**
   - Ensure `barcode_images` directory exists
   - Check write permissions
   - Verify item number format

## 📈 Future Enhancements

- [ ] Database integration (MySQL/PostgreSQL)
- [ ] REST API development
- [ ] Mobile application
- [ ] Advanced analytics dashboard
- [ ] Multi-location support
- [ ] Automated reorder points
- [ ] Integration with ERP systems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Created for production inventory management with RFID integration.

---

**© 2025 Inventory Management System**
