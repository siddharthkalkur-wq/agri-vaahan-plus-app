import pandas as pd
import streamlit as st

def data_imputation(method: str, symbol: str):
    """
    Combined data imputation function to handle various missing value techniques.
    """
    try:
        if 'data' not in st.session_state or st.session_state['data'] is None:
            return "ERROR: No data found. Please ask the user to upload a file."

        data_imputed = st.session_state['data'].copy()
        column_name = symbol
        
        # SMART ERROR REPORTING
        available_cols = data_imputed.columns.tolist()
        if column_name not in available_cols:
            return f"ERROR: Column '{column_name}' not found. Available columns are: {available_cols}. Please try the tool again with the exact column name."

        data_series = data_imputed[column_name]
        missing_indexes = data_series.isnull().index

        method = method.lower().replace(" ", "").replace("_", "")

        # 1. Native Directional Fills (Works on text and numbers)
        if method in ['bfill', 'backward']:
            data_series_imputed = data_series.bfill()
            data_imputed.loc[missing_indexes, column_name] = data_series_imputed
            
        elif method in ['ffill', 'forward']:
            data_series_imputed = data_series.ffill()
            data_imputed.loc[missing_indexes, column_name] = data_series_imputed
            
        # 2. Mathematical Fills (Forced numeric conversion to prevent crashes)
        elif method == 'spline':
            numeric_series = pd.to_numeric(data_series, errors='coerce')
            data_series_imputed = numeric_series.interpolate(method='spline', order=2, limit_direction='both')
            data_imputed.loc[missing_indexes, column_name] = data_series_imputed
            
        elif method == 'mean':
            numeric_val = pd.to_numeric(data_imputed[column_name], errors='coerce').mean()
            data_imputed[column_name] = data_imputed[column_name].fillna(numeric_val)
            
        elif method == 'min':
            numeric_val = pd.to_numeric(data_imputed[column_name], errors='coerce').min()
            data_imputed[column_name] = data_imputed[column_name].fillna(numeric_val)
            
        elif method == 'max':
            numeric_val = pd.to_numeric(data_imputed[column_name], errors='coerce').max()
            data_imputed[column_name] = data_imputed[column_name].fillna(numeric_val)
            
        # 3. Categorical Fill
        elif method == 'mode':
            mode_value = data_imputed[column_name].mode().iloc[0]
            data_imputed.loc[data_imputed[column_name].isnull(), column_name] = mode_value
            
        else:
            return f"ERROR: Invalid imputation method '{method}'."

        st.session_state['data'] = data_imputed
        return data_imputed

    except Exception as e:
        return f"ERROR during imputation: {str(e)}"
