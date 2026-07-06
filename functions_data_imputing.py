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
        
        # 1. SMART ERROR REPORTING: Tell Mistral if it guessed the wrong column
        available_cols = data_imputed.columns.tolist()
        if column_name not in available_cols:
            return f"ERROR: Column '{column_name}' not found. Available columns are: {available_cols}. Please try the tool again with the exact column name."

        data_series = data_imputed[column_name]
        missing_indexes = data_series.isnull().index

        method = method.lower().replace(" ", "").replace("_", "")

        if method == 'spline':
            data_series_imputed = data_series.interpolate(method='spline', order=2, limit_direction='both')
            data_imputed.loc[missing_indexes, column_name] = data_series_imputed
        elif method in ['bfill', 'backward']:
            data_series_imputed = data_series.interpolate(method='bfill')
            data_imputed.loc[missing_indexes, column_name] = data_series_imputed
        elif method in ['ffill', 'forward']:
            data_series_imputed = data_series.interpolate(method='ffill')
            data_imputed.loc[missing_indexes, column_name] = data_series_imputed
        elif method == 'mean':
            data_imputed[column_name] = data_imputed[column_name].fillna(data_imputed[column_name].mean())
        elif method == 'mode':
            mode_value = data_imputed[column_name].mode().iloc[0]
            data_imputed.loc[data_imputed[column_name].isnull(), column_name] = mode_value
        elif method == 'min':
            data_imputed[column_name] = data_imputed[column_name].fillna(data_imputed[column_name].min())
        elif method == 'max':
            data_imputed[column_name] = data_imputed[column_name].fillna(data_imputed[column_name].max())
        else:
            return f"ERROR: Invalid imputation method '{method}'."

        st.session_state['data'] = data_imputed
        return data_imputed

    except Exception as e:
        return f"ERROR during imputation: {str(e)}"
