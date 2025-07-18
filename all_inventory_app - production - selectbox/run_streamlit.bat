@echo off
cd /c "C:\Users\MS\Documents\inventory_ms_app\"
start "" "C:\Users\MS\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run inventory_ms_app.py --server.port=8501
timeout /t 3
