import pandas as pd
import streamlit as st
from dateutil.parser import parse

def data_cleaning(action: str, symbol: str = "", date1: str = "", date2: str = "") -> pd.DataFrame:
    """
    Combined data cleaning function to handle various DataFrame operations.

    Args:
        action (str): The specific cleaning task to perform. 
                      Valid options: 'drop_column', 'remove_row', 'remove_duplicates', 'extract_dates'.
        symbol (str): The column name or row index to be dropped. Defaults to "".
        date1 (str): Initial date string (e.g., '2020-01-01'). Defaults to "".
        date2 (str): Final date string (e.g., '2023-12-31'). Defaults to "".

    Returns:
        pd.DataFrame: The updated DataFrame.
    """
    try:
        # Ensure data exists in session state before proceeding
        if 'data' not in st.session_state:
            print("No data found in st.session_state.")
            return pd.DataFrame()

        df = st.session_state['data']

        # ---------------------------------------------------------
        # Condition 1: Drop a Feature/Column
        # ---------------------------------------------------------
        if action == 'drop_column':
            column_name = symbol
            df.drop(column_name, axis=1, inplace=True)
            st.session_state['data'] = df
            return df

        # ---------------------------------------------------------
        # Condition 2: Remove a Row by Index
        # ---------------------------------------------------------
        elif action == 'remove_row':
            row_id = int(symbol)
            df.drop(row_id, axis=0, inplace=True)
            st.session_state['data'] = df
            return df

        # ---------------------------------------------------------
        # Condition 3: Remove Duplicate Rows
        # ---------------------------------------------------------
        elif action == 'remove_duplicates':
            df_dropped = df.drop_duplicates(subset=None)
            st.session_state['data'] = df_dropped
            return df_dropped

        # ---------------------------------------------------------
        # Condition 4: Extract Data Between Dates
        # ---------------------------------------------------------
        elif action == 'extract_dates':
            initial_date = parse(date1)
            final_date = parse(date2)
            date_column = "Price_Date"
            
            df[date_column] = pd.to_datetime(df[date_column])
            filtered_df = df[(df[date_column] >= initial_date) & (df[date_column] <= final_date)]
            st.session_state['data'] = filtered_df
            return filtered_df
        
        # ---------------------------------------------------------
        # Condition 5: Filter by Column Value
        # ---------------------------------------------------------
        elif action == "filter_by_column_value":
            df = st.session_state['data'].copy()
            # Split the symbol argument assuming format "ColumnName:Value"
            if ":" in symbol:
                column_name, value = symbol.split(":", 1)
            else:
                column_name = symbol
                value = ""
            
            available_cols = df.columns.tolist()
            matched_col = column_name
            
            if column_name in available_cols:
                filtered_df = df[df[matched_col].astype(str).str.contains(value, case=False, na=False)]
                st.session_state['data'] = filtered_df
                st.write(f"Filtered to {len(filtered_df)} rows where '{matched_col}' contains '{value}'")
                return filtered_df
            return df
        # ---------------------------------------------------------
        # Fallback: Invalid Action
        # ---------------------------------------------------------
        else:
            print(f"Invalid action provided: '{action}'")
            return pd.DataFrame()

    except Exception as e:
        print(f"Error executing '{action}' in data_cleaning: {e}")
        return pd.DataFrame()