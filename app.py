
import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Set Streamlit page config
st.set_page_config(
    page_title="🏨 Hotel Demand Analytics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium dark styling
st.markdown("""
<style>
    /* Global dark theme */
    .stApp {
        background: #0a0a0a;
        color: #ffffff;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: #ffffff;
        text-align: center;
        border: 1px solid #333333;
        box-shadow: 0 15px 50px rgba(255,255,255,0.05);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #FFD700 0%, #FFA500 50%, #FFD700 100%);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(255,255,255,0.05);
        border: 1px solid #333333;
        border-left: 4px solid #FFD700;
        margin: 1rem 0;
        color: #ffffff;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #FFD700 50%, transparent 100%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(255,215,0,0.15);
        border-color: #FFD700;
    }
    
    .metric-card h4 {
        color: #FFD700;
        margin-bottom: 1rem;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    .metric-card p {
        color: #cccccc;
        margin: 0;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    .success-message {
        background: linear-gradient(135deg, #1a2e1a 0%, #2d4a2d 100%);
        color: #00ff88;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 1px solid #00ff88;
        box-shadow: 0 8px 25px rgba(0,255,136,0.1);
    }
    
    .info-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: #ffffff;
        padding: 2rem;
        border-radius: 16px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(255,215,0,0.1);
        border: 1px solid #FFD700;
        position: relative;
    }
    
    .info-box::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 50%;
        height: 2px;
        background: #FFD700;
        border-radius: 2px;
    }
    
    .stats-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 1px solid #333333;
        box-shadow: 0 8px 25px rgba(255,255,255,0.05);
    }
    
    .insight-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 12px 40px rgba(255,255,255,0.08);
        border: 1px solid #333333;
        color: #ffffff;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .insight-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #FFA500 50%, transparent 100%);
        transition: left 0.6s ease;
    }
    
    .insight-card:hover::before {
        left: 100%;
    }
    
    .insight-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(255,165,0,0.15);
        border-color: #FFA500;
    }
    
    .insight-card h4 {
        color: #FFA500;
        margin-bottom: 1.5rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        font-size: 1.3rem;
    }
    
    .insight-card p {
        color: #e0e0e0;
        margin: 0;
        font-size: 1.1rem;
        line-height: 1.7;
    }
    
    .chart-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 15px 50px rgba(255,255,255,0.08);
        border: 1px solid #333333;
        position: relative;
    }
    
    .chart-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FFD700 0%, #FFA500 50%, #FFD700 100%);
        border-radius: 3px 3px 0 0;
    }
    
    .export-section {
        background: linear-gradient(135deg, #1a2e1a 0%, #2d4a2d 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        border: 1px solid #00ff88;
        box-shadow: 0 12px 40px rgba(0,255,136,0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #0f0f0f !important;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 1px solid #333333;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(255,255,255,0.05);
    }
    
    [data-testid="metric-container"]:hover {
        border-color: #FFD700;
        box-shadow: 0 12px 35px rgba(255,215,0,0.1);
    }
    
    /* Input styling */
    .stDateInput > label {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 25px rgba(255,165,0,0.2) !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 35px rgba(255,165,0,0.3) !important;
    }
    
    /* Premium glow effects */
    .premium-glow {
        box-shadow: 0 0 20px rgba(255,215,0,0.3), 0 0 40px rgba(255,215,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main header with premium dark styling
st.markdown("""
<div class="main-header">
    <h1>🏨 Hotel Demand Analytics Dashboard</h1>
    <h3>AI-Powered SARIMAX Forecasting System</h3>
    <p>Predict hotel guest demand with advanced time series modeling</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("## 🎯 Dashboard Controls")
    
    # Add hotel info section
    st.markdown("""
    <div class="info-box">
        <h4>📊 Model Information</h4>
        <p><strong>Algorithm:</strong> SARIMAX</p>
        <p><strong>Training Period:</strong> Up to Aug 31, 2017</p>
        <p><strong>Forecast Target:</strong> Total Guests</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Model loading status
    with st.spinner("🔄 Loading SARIMAX model..."):
        @st.cache_resource
        def load_model():
            return joblib.load("model.joblib")
        
        try:
            model = load_model()
            st.success("✅ Model loaded successfully!")
        except Exception as e:
            st.error(f"❌ Error loading model: {e}")
            st.stop()
    
    # Add some metrics about the model
    st.markdown("### 📈 Quick Stats")
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Model Type", "SARIMAX", delta=None)
    with col2:
        st.metric("Status", "Active", delta="Ready")
    st.markdown('</div>', unsafe_allow_html=True)

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("## 📅 Forecast Configuration")
    
    # Enhanced date selection with better UX
    st.markdown("### Select Your Forecast Period")
    st.info("🔍 **Note:** Forecasts are available from September 1, 2017 onwards (post-training period)")
    
    # Date inputs with better defaults and validation
    default_start = pd.to_datetime("2017-09-14").date()
    default_end = pd.to_datetime("2017-09-28").date()
    
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input(
            "📅 Start Date", 
            value=default_start,
            help="Select the beginning of your forecast period"
        )
    with date_col2:
        end_date = st.date_input(
            "📅 End Date", 
            value=default_end,
            help="Select the end of your forecast period"
        )

# Convert to Timestamp for comparison
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)
training_end = pd.Timestamp("2017-08-31")

# Enhanced validation with better error messages
if start_date <= training_end:
    st.error("❌ **Invalid Date Range:** Start date must be after August 31, 2017 (end of training data)")
elif start_date > end_date:
    st.error("❌ **Invalid Date Range:** Start date must be before or equal to end date")
else:
    # Calculate forecast period info
    forecast_days = (end_date - start_date).days + 1
    
    # Display forecast period info
    st.markdown(f"""
    <div class="success-message">
        <h4>✅ Forecast Period Configured</h4>
        <p><strong>Period:</strong> {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}</p>
        <p><strong>Duration:</strong> {forecast_days} days</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate forecast
    with st.spinner("🔮 Generating forecast..."):
        try:
            # Forecast required number of steps
            total_days = (end_date - training_end).days
            start_offset = (start_date - training_end).days
            
            # Get full forecast up to end_date
            forecast_all = model.forecast(steps=total_days)
            
            # Get only the forecast from selected start_date to end_date
            forecast = forecast_all[start_offset - 1:]
            forecast.index = pd.date_range(start=start_date, end=end_date)
            
            # Create main dashboard with forecast results
            st.markdown("## 📊 Forecast Results")
            
            # Key metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_guests = forecast.mean()
                st.metric(
                    "Average Daily Guests", 
                    f"{avg_guests:.0f}",
                    delta=f"{forecast.iloc[-1] - forecast.iloc[0]:.0f}",
                    help="Average predicted guests per day in the forecast period"
                )
            
            with col2:
                max_guests = forecast.max()
                max_date = forecast.idxmax().strftime('%m/%d')
                st.metric(
                    "Peak Day", 
                    f"{max_guests:.0f}",
                    delta=max_date,
                    help="Highest predicted occupancy day"
                )
            
            with col3:
                min_guests = forecast.min()
                min_date = forecast.idxmin().strftime('%m/%d')
                st.metric(
                    "Low Day", 
                    f"{min_guests:.0f}",
                    delta=min_date,
                    help="Lowest predicted occupancy day"
                )
            
            with col4:
                total_guests = forecast.sum()
                st.metric(
                    "Total Guests", 
                    f"{total_guests:.0f}",
                    delta=f"{forecast_days} days",
                    help="Total guests expected in the forecast period"
                )
            
            # Interactive Plotly chart
            st.markdown("### 📈 Interactive Forecast Visualization")
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            fig = go.Figure()
            
            # Add forecast line with premium styling
            fig.add_trace(go.Scatter(
                x=forecast.index,
                y=forecast.values,
                mode='lines+markers',
                name='Predicted Guests',
                line=dict(color='#FFD700', width=4, shape='spline'),
                marker=dict(size=8, color='#FFA500', line=dict(color='#FFD700', width=2)),
                hovertemplate='<b>Date:</b> %{x}<br><b>Guests:</b> %{y:.0f}<extra></extra>',
                fill='tonexty',
                fillcolor='rgba(255, 215, 0, 0.1)'
            ))
            
            # Update layout for dark theme
            fig.update_layout(
                title={
                    'text': f'Hotel Guest Demand Forecast ({start_date.strftime("%b %d")} - {end_date.strftime("%b %d, %Y")})',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 22, 'color': '#ffffff', 'family': 'Arial Black'}
                },
                xaxis_title="Date",
                yaxis_title="Number of Guests",
                hovermode='x unified',
                height=500,
                template='plotly_dark',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color='#ffffff')
                ),
                paper_bgcolor='rgba(26, 26, 26, 0.9)',
                plot_bgcolor='rgba(45, 45, 45, 0.9)',
                xaxis=dict(
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    color='#ffffff'
                ),
                yaxis=dict(
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    color='#ffffff'
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Detailed forecast table with enhanced styling
            st.markdown("### 📋 Detailed Forecast Data")
            
            # Create a formatted dataframe
            forecast_df = pd.DataFrame({
                'Date': forecast.index.strftime('%A, %B %d, %Y'),
                'Predicted Guests': forecast.values.astype(int),
                'Day of Week': forecast.index.strftime('%A'),
                'Month': forecast.index.strftime('%B')
            })
            
            # Add color coding based on guest numbers
            def color_code_guests(val):
                if val > avg_guests * 1.1:
                    return 'background-color: #d4edda; color: #155724'  # High demand - green
                elif val < avg_guests * 0.9:
                    return 'background-color: #f8d7da; color: #721c24'  # Low demand - red
                else:
                    return 'background-color: #fff3cd; color: #856404'  # Medium demand - yellow
            
            styled_df = forecast_df.style.applymap(
                color_code_guests, 
                subset=['Predicted Guests']
            ).format({'Predicted Guests': '{:,}'})
            
            st.dataframe(styled_df, use_container_width=True)
            
            # Download options
            st.markdown("### 💾 Export Options")
            st.markdown('<div class="export-section">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                csv_data = forecast_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"hotel_forecast_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    help="Download forecast data as CSV file"
                )
            
            with col2:
                # Create a summary report
                summary_report = f"""
                Hotel Demand Forecast Report
                Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                Forecast Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}
                Duration: {forecast_days} days
                
                Key Metrics:
                - Average Daily Guests: {avg_guests:.0f}
                - Peak Day: {max_guests:.0f} guests on {forecast.idxmax().strftime('%B %d, %Y')}
                - Low Day: {min_guests:.0f} guests on {forecast.idxmin().strftime('%B %d, %Y')}
                - Total Guests: {total_guests:.0f}
                
                Model: SARIMAX Time Series Forecasting
                """
                
                st.download_button(
                    label="📊 Download Report",
                    data=summary_report,
                    file_name=f"hotel_forecast_report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    help="Download detailed forecast report"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional insights
            st.markdown("### 🎯 Forecast Insights")
            
            insight_col1, insight_col2 = st.columns(2)
            
            with insight_col1:
                trend_direction = "increasing" if forecast.iloc[-1] > forecast.iloc[0] else "decreasing" if forecast.iloc[-1] < forecast.iloc[0] else "stable"
                trend_emoji = "📈" if trend_direction == "increasing" else "📉" if trend_direction == "decreasing" else "➡️"
                
                st.markdown(f"""
                <div class="insight-card">
                    <h4>{trend_emoji} Demand Trend</h4>
                    <p>Based on the forecast, your hotel demand shows <strong>{trend_direction}</strong> patterns during this period.</p>
                    <br>
                    <p><strong>Change:</strong> {forecast.iloc[-1] - forecast.iloc[0]:.0f} guests from start to end</p>
                </div>
                """, unsafe_allow_html=True)
            
            with insight_col2:
                # Calculate day of week patterns
                day_avg = forecast.groupby(forecast.index.dayofweek).mean()
                peak_day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_avg.idxmax()]
                peak_avg = day_avg.max()
                
                st.markdown(f"""
                <div class="insight-card">
                    <h4>📅 Weekly Pattern</h4>
                    <p>Highest demand is typically expected on <strong>{peak_day}s</strong> during this forecast period.</p>
                    <br>
                    <p><strong>Average on {peak_day}:</strong> {peak_avg:.0f} guests</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Add additional insights row
            st.markdown("#### 📊 Advanced Analytics")
            insight_col3, insight_col4 = st.columns(2)
            
            with insight_col3:
                volatility = forecast.std()
                st.markdown(f"""
                <div class="insight-card">
                    <h4>📊 Demand Volatility</h4>
                    <p>The forecast shows <strong>{"high" if volatility > avg_guests * 0.1 else "low"}</strong> volatility in guest demand.</p>
                    <br>
                    <p><strong>Standard Deviation:</strong> {volatility:.1f} guests</p>
                </div>
                """, unsafe_allow_html=True)
            
            with insight_col4:
                growth_rate = ((forecast.iloc[-1] / forecast.iloc[0]) - 1) * 100
                growth_emoji = "🚀" if growth_rate > 5 else "📉" if growth_rate < -5 else "📊"
                
                st.markdown(f"""
                <div class="insight-card">
                    <h4>{growth_emoji} Growth Rate</h4>
                    <p>Expected <strong>{abs(growth_rate):.1f}%</strong> {"growth" if growth_rate > 0 else "decline" if growth_rate < 0 else "stability"} over the forecast period.</p>
                    <br>
                    <p><strong>Period Performance:</strong> {"Above average" if growth_rate > 0 else "Below average" if growth_rate < 0 else "Stable"}</p>
                </div>
                """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error generating forecast: {e}")

# Footer with premium dark styling
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #cccccc; padding: 3rem; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); border-radius: 20px; margin-top: 2rem; border: 1px solid #333333;">
    <h3 style="color: #FFD700; margin-bottom: 1rem;">🏨 Hotel Demand Analytics Dashboard</h3>
    <p style="color: #FFA500; font-size: 1.1rem; margin-bottom: 0.5rem;"><strong>Powered by SARIMAX Machine Learning</strong></p>
    <p style="color: #cccccc;">📊 Built with Streamlit & Python | ⚡ Optimized for Performance</p>
    <p style="color: #999999; font-size: 0.9rem;">Last Updated: {}</p>
</div>
""".format(datetime.now().strftime('%B %Y')), unsafe_allow_html=True)