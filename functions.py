from functions_data_imputing import data_imputation
from functions_data_cleaning import data_cleaning
from functions_data_vis import data_visualization
from functions_time_series_models import time_series_forecasting

def get_mistral_tools() -> list:
    """Returns the JSON schema tools for the Mistral API."""
    return [
        {
            "type": "function",
            "function": {
                "name": "data_cleaning",
                "description": "Cleans data by dropping columns, removing rows/duplicates, extracting dates, or filtering by column value.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "One of: 'drop_column', 'remove_row', 'remove_duplicates', 'extract_dates', 'filter_by_column_value'"},
                        "symbol": {"type": "string", "description": "Column name or row index (used for drop/remove/filter)"},
                        "date1": {"type": "string", "description": "Initial date string (e.g., '2020-01-01')"},
                        "date2": {"type": "string", "description": "Final date string (e.g., '2023-12-31')"}
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "data_imputation",
                "description": "Fills missing values in a dataset.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "method": {"type": "string", "description": "One of: 'spline', 'linear', 'bfill', 'ffill', 'mean', 'mode', 'min', 'max'"},
                        "symbol": {"type": "string", "description": "The column/feature name to be imputed"}
                    },
                    "required": ["method", "symbol"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "data_visualization",
                "description": "Generates data visualizations or summary tables.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "One of: 'plot_time_series', 'null_counts'"},
                        "symbol": {"type": "string", "description": "The column name to plot (required for 'plot_time_series')"}
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "time_series_forecasting",
                "description": "Forecasts future values for a given column.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "method": {"type": "string", "description": "One of: 'auto_arima', 'exponential_smoothing'"},
                        "column_name": {"type": "string", "description": "The column to forecast"},
                        "days": {"type": "integer", "description": "Number of days to predict"}
                    },
                    "required": ["method", "column_name"]
                }
            }
        }
    ]