import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from typing import Union

def data_visualization(action: str, symbol: str = "") -> Union[go.Figure, pd.DataFrame, None]:
    """
    Combined function for data visualization and summary tasks.

    Args:
        action (str): The specific task to perform. 
                      Valid options: 'plot_time_series', 'null_counts'.
        symbol (str): The column/feature name to plot (required for 'plot_time_series'). 
                      Defaults to "".

    Returns:
        Union[go.Figure, pd.DataFrame, None]: A Plotly figure, a DataFrame of null counts, 
                                              or None if an error occurs.
    """
    try:
        # Ensure data exists in session state before proceeding
        if 'data' not in st.session_state:
            print("No data found in st.session_state.")
            return None

        df = st.session_state['data']

        # ---------------------------------------------------------
        # Condition 1: Plot Time Series Graph
        # ---------------------------------------------------------
        if action == 'plot_time_series':
            feature_col = symbol
            timeseries_col = "Price_Date"
            
            # Convert if necessary
            df[timeseries_col] = pd.to_datetime(df[timeseries_col])  

            # Create the time series trace
            trace = go.Scatter(
                x=df[timeseries_col],
                y=df[feature_col],
                mode='lines',
                name=feature_col
            )

            # Create the figure object
            fig = go.Figure(data=[trace])
            fig.update_layout(
                title=f"Time Series of {feature_col}",
                xaxis_title=timeseries_col,
                yaxis_title=feature_col
            )
            return fig

        # ---------------------------------------------------------
        # Condition 2: Get Null Value Counts
        # ---------------------------------------------------------
        elif action == 'null_counts':
            # Get null value counts
            null_counts = df.isnull().sum()

            # Create DataFrame with column names and null counts
            result_df = pd.DataFrame({
                'Feature/Column Name': null_counts.index, 
                'Number of NULL values': null_counts.values
            })
            return result_df

        # ---------------------------------------------------------
        # Fallback: Invalid Action
        # ---------------------------------------------------------
        else:
            print(f"Invalid action provided: '{action}'")
            return None

    except Exception as e:
        print(f"Error executing '{action}' in data_visualization: {e}")
        return None