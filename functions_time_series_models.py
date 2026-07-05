import pandas as pd
import streamlit as st
import warnings
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
warnings.filterwarnings("ignore")

def time_series_forecasting(method: str, column_name: str, days: int = 15) -> pd.DataFrame:
    try:
        if 'data' not in st.session_state:
            print("No data found in st.session_state.")
            return pd.DataFrame()

        df = st.session_state['data'].copy()
        
        # Ensure correct column matching
        available_cols = df.columns.tolist()
        matched_col = column_name
        if column_name not in available_cols:
            lower_map = {c.lower(): c for c in available_cols}
            query_lower = column_name.lower()
            if query_lower in lower_map:
                matched_col = lower_map[query_lower]
            else:
                candidates = [c for c in available_cols if query_lower in c.lower()]
                if candidates:
                    matched_col = candidates[0]
                else:
                    return pd.DataFrame()

        # Group by date and clean for forecasting
        df["Price_Date"] = pd.to_datetime(df["Price_Date"])
        df = df.groupby("Price_Date", as_index=False)[matched_col].mean()
        df = df.sort_values("Price_Date").set_index("Price_Date")
        series = df[matched_col].dropna()

        method_normalized = method.lower().replace(" ", "_")
        
        if method_normalized == 'auto_arima':
            model = ARIMA(series, order=(5, 1, 0)) # Standard lightweight ARIMA
            fit_model = model.fit()
            forecast = fit_model.forecast(steps=days)
        
        elif method_normalized in ['exponential_smoothing', 'ets']:
            model = ExponentialSmoothing(series, trend='add', seasonal=None)
            fit_model = model.fit()
            forecast = fit_model.forecast(steps=days)
            
        else:
            return pd.DataFrame()

        # Format output
        pred_df = pd.DataFrame({
            "Date": pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=days),
            "Predicted_" + matched_col: forecast.values
        })
        
        st.write(f"### {method} Forecast for {matched_col}")
        st.write(pred_df)
        return pred_df

    except Exception as e:
        print(f"Error in time_series_forecasting: {e}")
        return pd.DataFrame()