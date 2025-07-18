import streamlit as st
import pandas as pd
from datetime import datetime
import os

def calculate_monthly_report(data, year, month, stocklist):
    start_date = pd.Timestamp(year=year, month=month, day=1)
    end_date = start_date + pd.offsets.MonthEnd(0)
    report = {}
    
    data = data.copy()
    data['Date'] = pd.to_datetime(data['Date'])
    data['Received Qty'] = pd.to_numeric(data['Received Qty'], errors='coerce')
    data['Issued Qty'] = pd.to_numeric(data['Issued Qty'], errors='coerce')

    data = data[data['Person in Charge'].notna()]
    
    items_with_input = data[
        (data['Received Qty'] > 0) & 
        (data['Date'] <= end_date)     
    ].groupby('Item No').agg({
        'Date': 'min' 
    }).reset_index()
    
    for _, item_row in items_with_input.iterrows():
        item_no = item_row['Item No']
        try:
            item_data = data[data['Item No'] == item_no]

            is_new_item = item_data[
                (item_data['Date'] >= start_date) & 
                (item_data['Date'] <= end_date) & 
                (item_data['Status'] == 'new')
            ].any().any()

            if is_new_item:
                beg_qty = 0  
                total_input = pd.to_numeric(item_data['Received Qty'], errors='coerce').sum()
                total_output = pd.to_numeric(item_data['Issued Qty'], errors='coerce').sum()
            else:
                previous_transactions = item_data[item_data['Date'] < start_date]
                if not previous_transactions.empty:
                    total_previous_input = previous_transactions['Received Qty'].sum()
                    total_previous_output = pd.to_numeric(previous_transactions['Issued Qty'], errors='coerce').sum()
                    beg_qty = total_previous_input - total_previous_output
                else:
                    stock_item = stocklist[stocklist['Item No'] == item_no]
                    if not stock_item.empty:
                        beg_qty = float(stock_item['Quantity'].values[0])
                    else:
                        beg_qty = 0

            month_transactions = item_data[
                (item_data['Date'] >= start_date) & 
                (item_data['Date'] <= end_date)]

            total_input = month_transactions['Received Qty'].sum()
            total_output = pd.to_numeric(month_transactions['Issued Qty'], errors='coerce').sum()

            end_qty = beg_qty + total_input - total_output
            
            print(f"Item {item_no}: beg_qty={beg_qty}, total_input={total_input}, total_output={total_output}, end_qty={end_qty}")

            # Fetch item details from stocklist instead of item_data
            stock_item = stocklist[stocklist['Item No'] == item_no]
            if not stock_item.empty:
                item_name = stock_item['Item Name'].iloc[0]
                unit = stock_item['Unit'].iloc[0] if 'Unit' in stock_item.columns else '-'
                item_type = stock_item['Type'].iloc[0] if 'Type' in stock_item.columns else '-'
                no_hri = stock_item['No HRI'].iloc[0] if 'No HRI' in stock_item.columns else '-'
                machine = stock_item['Machine'].iloc[0] if 'Machine' in stock_item.columns else '-'
                price = stock_item['Price'].iloc[0] if 'Price' in stock_item.columns else '-'
            else:
                # Fallback to transaction data if item not found in stocklist
                item_name = item_data['Item Name'].iloc[0]
                unit = item_data['Unit'].iloc[0] if 'Unit' in item_data.columns else '-'
                item_type = item_data['Type'].iloc[0] if 'Type' in item_data.columns else '-'
                no_hri = item_data['No HRI'].iloc[0] if 'No HRI' in item_data.columns else '-'
                machine = item_data['Machine'].iloc[0] if 'Machine' in item_data.columns else '-'
                price = item_data['Price'].iloc[0] if 'Price' in item_data.columns else '-'

            # Person in Charge still comes from transaction data
            person_incharge = item_data['Person in Charge'].iloc[0]

            report[item_no] = {
                'month': month,
                'year': year,
                'Item No': item_no,
                'No HRI': no_hri,
                'Item Name': item_name,
                'Type': item_type,
                'Machine': machine,
                'Unit': unit,
                'Price': price,
                'Beginning Qty': beg_qty,
                'Received Qty': total_input,
                'Issued Qty': total_output,
                'End Qty': end_qty,
                'Person in Charge': person_incharge
            }
        
        except Exception as e:
            st.warning(f"Error processing item {item_no}: {str(e)}")
            continue

    if report:
        report_df = pd.DataFrame.from_dict(report, orient='index')
        cols = ['month', 'year', 'Item No', 'No HRI', 'Item Name', 'Type', 'Machine', 'Unit', 'Price',
                'Beginning Qty', 'Received Qty', 'Issued Qty', 'End Qty', 'Person in Charge']
        report_df['year'] = report_df['year'].astype(str)
        report_df['Item No'] = report_df['Item No'].astype(str)
        
        for col in cols:
            if col not in report_df.columns:
                report_df[col] = '-'
        
        report_df = report_df[cols]
        return report_df
    else:
        return pd.DataFrame(columns=['month', 'year', 'Item No', 'No HRI', 'Item Name', 'Type', 'Machine', 'Unit', 'Price',
                                     'Beginning Qty', 'Received Qty', 'Issued Qty', 'End Qty', 'Person in Charge'])