import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# Set Streamlit page config
st.set_page_config(page_title="SARIMAX Hotel Guest Forecast", layout="centered")

st.title("📈 SARIMAX Forecasting App")
st.markdown("Forecast **hotel totalGuests** using a pre-trained SARIMAX model.")

# Load SARIMAX model (cached)
@st.cache_resource
def load_model():
    return joblib.load("model.joblib")

model = load_model()

# --- Forecast Date Range Selection ---
st.subheader("📅 Select Forecast Range (after 31 Aug 2017)")

default_start = pd.to_datetime("2017-09-14").date()
default_end = pd.to_datetime("2017-09-28").date()

start_date = st.date_input("Start Date", value=default_start)
end_date = st.date_input("End Date", value=default_end)

# Convert to Timestamp for comparison
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
training_end = pd.Timestamp("2017-08-31")

# --- Validations ---
if start_date <= training_end:
    st.error("❌ Start date must be **after 31-Aug-2017** (end of training data).")
elif start_date > end_date:
    st.error("❌ Start date must be before or equal to end date.")
else:
    # Forecast required number of steps (up to end_date)
    total_days = (end_date - training_end).days
    start_offset = (start_date - training_end).days

    # Get full forecast up to end_date
    forecast_all = model.forecast(steps=total_days)

    # Get only the forecast from selected start_date to end_date
    forecast = forecast_all[start_offset - 1:]
    forecast.index = pd.date_range(start=start_date, end=end_date)

    # --- Output Forecast Table ---
    st.subheader("📊 Forecasted Total Guests:")
    st.dataframe(forecast.rename("Predicted totalGuests"))

    # --- Plotting ---
    st.subheader("📉 Forecast Plot")
    fig, ax = plt.subplots()
    forecast.plot(ax=ax, marker='o', linestyle='--')
    ax.set_title("Predicted Total Guests")
    ax.set_ylabel("Guests")
    ax.set_xlabel("Date")
    ax.grid(True)
    st.pyplot(fig)
