import pandas as pd
import streamlit as st

def data_imputation(method: str, symbol: str) -> pd.DataFrame:
    """
    Combined data imputation function to handle various missing value techniques.

    Args:
        method (str): The imputation technique to apply. 
                      Valid options: 'spline', 'linear', 'bfill' (or 'backward'), 
                      'ffill' (or 'forward'), 'mean', 'mode', 'min', 'max'.
        symbol (str): The column/feature name to be imputed.

    Returns:
        pd.DataFrame: The imputed DataFrame.
    """
    try:
        # Ensure data exists in session state before proceeding
        if 'data' not in st.session_state:
            print("No data found in st.session_state.")
            return pd.DataFrame()

        data_imputed = st.session_state['data']
        column_name = symbol
        data_series = data_imputed[column_name]
        
        # Get indices of missing values
        missing_indexes = data_series.isnull().index

        # Normalize the method string to handle variations (e.g., "Forward Fill" -> "ffill")
        method = method.lower().replace(" ", "").replace("_", "")

        # ---------------------------------------------------------
        # Time Series Imputation Techniques
        # ---------------------------------------------------------
        if method == 'spline':
            data_series_imputed = data_series.interpolate(method='spline', order=2, limit_direction='both')
            data_imputed.loc[missing_indexes, column_name] = data_series_imputed

        elif method == 'linear':
            data_series_imputed = data_series.interpolate(method='linear')
            data_imputed.loc[missing_indexes, column_name] = data_series_imputed

        elif method in ['bfill', 'backward', 'backfill', 'backwardfill']:
            data_series_imputed = data_series.interpolate(method='bfill')
            data_imputed.loc[missing_indexes, column_name] = data_series_imputed

        elif method in ['ffill', 'forward', 'forwardfill']:
            data_series_imputed = data_series.interpolate(method='ffill')
            data_imputed.loc[missing_indexes, column_name] = data_series_imputed

        # ---------------------------------------------------------
        # Tabular Imputation Techniques
        # ---------------------------------------------------------
        elif method == 'mean':
            data_imputed[column_name] = data_imputed[column_name].fillna(data_imputed[column_name].mean())

        elif method == 'mode':
            mode_value = data_imputed[column_name].mode().iloc[0]
            data_imputed.loc[data_imputed[column_name].isnull(), column_name] = mode_value

        elif method == 'min':
            data_imputed[column_name] = data_imputed[column_name].fillna(data_imputed[column_name].min())

        elif method == 'max':
            data_imputed[column_name] = data_imputed[column_name].fillna(data_imputed[column_name].max())

        # ---------------------------------------------------------
        # Fallback: Invalid Method
        # ---------------------------------------------------------
        else:
            print(f"Invalid imputation method provided: '{method}'")
            return pd.DataFrame()

        # Update session state and return the imputed DataFrame
        st.session_state['data'] = data_imputed
        return data_imputed

    except Exception as e:
        print(f"Error executing '{method}' imputation on '{symbol}': {e}")
        return pd.DataFrame()