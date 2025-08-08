import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Hotel Demand Prophet Dashboard", 
    layout="wide"
)

# Title
st.title("🏨 Hotel Demand Prophet Forecast")

# Sidebar
st.sidebar.header("Forecast Settings")

# Load model
@st.cache_resource
def load_prophet_model():
    try:
        model = joblib.load("prophetmodel.joblib")
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_prophet_model()

if model is None:
    st.stop()

st.sidebar.success("✅ Prophet model loaded")

# Date inputs
st.sidebar.subheader("Select Forecast Period")
start_date = st.sidebar.date_input(
    "Start Date", 
    value=datetime(2017, 9, 1).date()
)
end_date = st.sidebar.date_input(
    "End Date", 
    value=datetime(2017, 9, 30).date()
)

# Convert to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Validate dates
if start_date >= end_date:
    st.error("Start date must be before end date")
    st.stop()

# Generate forecast
if st.sidebar.button("Generate Forecast") or True:  # Auto-generate
    
    # Create future dataframe for Prophet
    future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    future_df = pd.DataFrame({'ds': future_dates})
    
    # Generate forecast
    with st.spinner("Generating forecast..."):
        try:
            forecast = model.predict(future_df)
            
            # Extract predictions
            predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            predictions.columns = ['Date', 'Prediction', 'Lower_CI', 'Upper_CI']
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_guests = predictions['Prediction'].mean()
                st.metric("Avg Daily Guests", f"{avg_guests:.0f}")
            
            with col2:
                max_guests = predictions['Prediction'].max()
                st.metric("Peak Day", f"{max_guests:.0f}")
            
            with col3:
                min_guests = predictions['Prediction'].min()
                st.metric("Low Day", f"{min_guests:.0f}")
            
            with col4:
                total_guests = predictions['Prediction'].sum()
                st.metric("Total Guests", f"{total_guests:.0f}")
            
            # Plot forecast
            st.subheader("Forecast Visualization")
            
            fig = go.Figure()
            
            # Add prediction line
            fig.add_trace(go.Scatter(
                x=predictions['Date'],
                y=predictions['Prediction'],
                mode='lines+markers',
                name='Predicted Guests',
                line=dict(color='blue', width=3)
            ))
            
            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=predictions['Date'],
                y=predictions['Upper_CI'],
                fill=None,
                mode='lines',
                line_color='rgba(0,0,0,0)',
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=predictions['Date'],
                y=predictions['Lower_CI'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(0,0,0,0)',
                name='Confidence Interval',
                fillcolor='rgba(0,100,255,0.2)'
            ))
            
            fig.update_layout(
                title="Hotel Guest Demand Forecast",
                xaxis_title="Date",
                yaxis_title="Number of Guests",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display data table
            st.subheader("Forecast Data")
            predictions_display = predictions.copy()
            predictions_display['Date'] = predictions_display['Date'].dt.strftime('%Y-%m-%d')
            predictions_display['Prediction'] = predictions_display['Prediction'].round(0).astype(int)
            predictions_display['Lower_CI'] = predictions_display['Lower_CI'].round(0).astype(int)
            predictions_display['Upper_CI'] = predictions_display['Upper_CI'].round(0).astype(int)
            
            st.dataframe(predictions_display, use_container_width=True)
            
            # Download option
            csv = predictions_display.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"hotel_forecast_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"Error generating forecast: {e}")
            st.error("Make sure your Prophet model was trained with 'ds' and 'y' columns")

# Footer
st.markdown("---")
st.markdown("**Prophet Model Dashboard** | Built with Streamlit")