import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import plotly.express as px

# Try to import required packages with error handling
try:
    import joblib
except ImportError:
    st.error("❌ joblib is not installed. Please add 'joblib' to your requirements.txt file.")
    st.code("pip install joblib")
    st.stop()

try:
    from prophet import Prophet
except ImportError:
    st.error("❌ Prophet is not installed. Please add 'prophet' to your requirements.txt file.")
    st.code("pip install prophet")
    st.stop()

# Set Streamlit page config
st.set_page_config(
    page_title="🏨 Hotel Intelligence • Demand Forecasting", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with cleaner dark styling (similar to second dashboard)
st.markdown("""
<style>
    /* Global dark theme */
    .stApp {
        background: #000;
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
        background: linear-gradient(135deg, #111 0%, #2d2d2d 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(255,255,255,0.05);
        border: 1px solid #333333;
        border-bottom: 4px solid #FFD700;
        margin: 1rem 0;
        color: #ffffff;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        height: 100%;
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
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFD700;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-subtitle {
        color: #9CA3AF;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 0.5rem;
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
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #00ff88;
        box-shadow: 0 12px 40px rgba(0,255,136,0.1);
    }
    
    .section-header {
        font-size: 1.75rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin: 3rem 0 2rem 0;
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, #FFD700, #FFA500);
        border-radius: 2px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #0f0f0f !important;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        padding: 1.25rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 400;
        font-size: 0.95rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(255,215,0,0.3);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 25px rgba(255,215,0,0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 35px rgba(255,215,0,0.3) !important;
    }
    
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
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🏨 Hotel Intelligence</h1>
    <h3>AI-Powered Prophet Forecasting System</h3>
    <p>Advanced Demand Forecasting • Powered by Prophet AI</p>
</div>
""", unsafe_allow_html=True)
st.markdown("Visit the [Analytics Dashboard](https://prohotelyticsdashboard.streamlit.app/)")
# Sidebar
st.sidebar.markdown('<div class="sidebar-header"> Forecast Configuration</div>', unsafe_allow_html=True)

# Load model
@st.cache_resource
def load_prophet_model():
    try:
        model_files = ["prophetmodel.joblib", "prophet_model.joblib", "model.joblib"]
        
        for model_file in model_files:
            try:
                model = joblib.load(model_file)
                # st.sidebar.success(f"✅ Model loaded: {model_file}")
                return model
            except FileNotFoundError:
                continue
        
        st.error("❌ No Prophet model file found!")
        st.markdown("""
        **Expected files:** `prophetmodel.joblib`, `prophet_model.joblib`, or `model.joblib`
        
        **Setup Instructions:**
        1. Train your Prophet model
        2. Save: `joblib.dump(model, 'prophetmodel.joblib')`
        3. Upload to repository
        """)
        return None
        
    except Exception as e:
        st.error(f"❌ Model loading error: {e}")
        return None

model = load_prophet_model()

if model is None:
    st.stop()

st.sidebar.markdown("### 📅 Analysis Period")
col1, col2 = st.sidebar.columns(2)

with col1:
    start_date = st.date_input(
        "From", 
        value=datetime(2017, 9, 1).date(),
        help="Select the start date for your forecast"
    )

with col2:
    end_date = st.date_input(
        "To", 
        value=datetime(2017, 9, 30).date(),
        help="Select the end date for your forecast"
    )

# Date inputs

# Additional options
st.sidebar.markdown("### ⚙️ Advanced Options")
show_confidence = st.sidebar.toggle("Show Confidence Intervals", value=True)
chart_style = st.sidebar.selectbox(
    "Chart Style",
    ["Luxury Gold", "Emerald Premium", "Coral Elegance", "Teal Sophistication"]
)

# Convert to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Validate dates
if start_date >= end_date:
    st.error("❌ Start date must be before end date")
    st.stop()

# Generate forecast button
forecast_button = st.sidebar.button("🚀 Generate Forecast", use_container_width=True)

if forecast_button or 'forecast_generated' not in st.session_state:
    st.session_state['forecast_generated'] = True
    
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
    
    # Create future dataframe
    future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    future_df = pd.DataFrame({'ds': future_dates})
    
    # Generate forecast
    with st.spinner("🔮 Generating intelligent forecast..."):
        try:
            forecast = model.predict(future_df)
            
            # Extract predictions
            predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            predictions.columns = ['Date', 'Prediction', 'Lower_CI', 'Upper_CI']
            
            # Store in session state
            st.session_state['predictions'] = predictions
            
        except Exception as e:
            st.error(f"❌ Forecast generation failed: {e}")
            st.stop()

# Display results if forecast exists
if 'predictions' in st.session_state:
    predictions = st.session_state['predictions']
    
    # Key metrics section
    st.markdown('<h2 class="section-header">📊 Forecast Results</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    avg_guests = predictions['Prediction'].mean()
    max_guests = predictions['Prediction'].max()
    min_guests = predictions['Prediction'].min()
    total_guests = predictions['Prediction'].sum()
    days = len(predictions)
    
    max_date = predictions.loc[predictions['Prediction'].idxmax(), 'Date'].strftime('%m/%d')
    min_date = predictions.loc[predictions['Prediction'].idxmin(), 'Date'].strftime('%m/%d')
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📈</div>
            <h4>Avg Daily Guests</h4>
            <div class="metric-value">{avg_guests:.0f}</div>
            <div class="metric-subtitle">per day average</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <h4>Peak Day</h4>
            <div class="metric-value">{max_guests:.0f}</div>
            <div class="metric-subtitle">on {max_date}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📉</div>
            <h4>Low Day</h4>
            <div class="metric-value">{min_guests:.0f}</div>
            <div class="metric-subtitle">on {min_date}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🏨</div>
            <h4>Total Guests</h4>
            <div class="metric-value">{total_guests:.0f}</div>
            <div class="metric-subtitle">{days} days</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Chart section
    st.markdown('<h2 class="section-header">📈 Interactive Forecast Visualization</h2>', unsafe_allow_html=True)
    
    
    # Create chart
    fig = go.Figure()
    
    # Color schemes
    color_schemes = {
        "Luxury Gold": {"main": "#FFD700", "confidence": "rgba(255, 215, 0, 0.15)"},
        "Emerald Premium": {"main": "#50C878", "confidence": "rgba(80, 200, 120, 0.15)"},
        "Coral Elegance": {"main": "#FF6B6B", "confidence": "rgba(255, 107, 107, 0.15)"},
        "Teal Sophistication": {"main": "#14B8A6", "confidence": "rgba(20, 184, 166, 0.15)"}
    }
    
    colors = color_schemes[chart_style]
    
    # Add confidence interval if enabled
    if show_confidence:
        fig.add_trace(go.Scatter(
            x=predictions['Date'],
            y=predictions['Upper_CI'],
            fill=None,
            mode='lines',
            line_color='rgba(0,0,0,0)',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=predictions['Date'],
            y=predictions['Lower_CI'],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,0,0,0)',
            name='95% Confidence Interval',
            fillcolor=colors["confidence"]
        ))
    
    # Add main prediction line
    fig.add_trace(go.Scatter(
        x=predictions['Date'],
        y=predictions['Prediction'],
        mode='lines+markers',
        name='Demand Forecast',
        line=dict(color=colors["main"], width=4, shape='spline'),
        marker=dict(size=8, color=colors["main"], line=dict(width=2, color='rgba(255,255,255,0.8)')),
        hovertemplate='<b>%{x|%B %d, %Y}</b><br>Predicted Demand: <b>%{y:.0f} guests</b><extra></extra>'
    ))
    
    # Update layout for dark theme
    fig.update_layout(
        title={
            'text': f'Hotel Guest Demand Forecast ({start_date.strftime("%b %d")} - {end_date.strftime("%b %d, %Y")})',
            'x': 0.5,
            'font': {'size': 20, 'color': '#ffffff', 'family': 'Inter'}
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
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)', color='#ffffff'),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)', color='#ffffff')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed forecast table
    st.markdown('<h2 class="section-header">📋 Detailed Forecast Data</h2>', unsafe_allow_html=True)
    
    # Create formatted dataframe
    display_data = predictions.copy()
    display_data['Date'] = display_data['Date'].dt.strftime('%A, %B %d, %Y')
    display_data['Day'] = predictions['Date'].dt.strftime('%A')
    display_data['Prediction'] = display_data['Prediction'].round(0).astype(int)
    display_data['Lower_CI'] = display_data['Lower_CI'].round(0).astype(int)
    display_data['Upper_CI'] = display_data['Upper_CI'].round(0).astype(int)
    
    display_data = display_data[['Date', 'Day', 'Prediction', 'Lower_CI', 'Upper_CI']]
    display_data.columns = ['📅 Date', '📆 Day', '🎯 Forecast', '📉 Lower Bound', '📈 Upper Bound']
    
    st.dataframe(display_data, use_container_width=True, height=400)
    
    # Export options
   
    st.markdown('<h2 class="section-header">💾 Export Options</h2>', unsafe_allow_html=True)
    st.markdown('<div class="export-section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = display_data.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"hotel_forecast_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Download forecast data as CSV file"
        )
    
    with col2:
        # Summary report
        summary_report = f"""
Hotel Intelligence Forecast Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Forecast Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}
Duration: {len(predictions)} days

Key Metrics:
- Average Daily Guests: {avg_guests:.0f}
- Peak Day: {max_guests:.0f} guests on {max_date}
- Low Day: {min_guests:.0f} guests on {min_date}
- Total Guests: {total_guests:.0f}

Model: Facebook Prophet Time Series Forecasting
        """
        
        st.download_button(
            label="📊 Download Report",
            data=summary_report,
            file_name=f"hotel_forecast_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            help="Download detailed forecast report"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Insights section
    st.markdown('<h2 class="section-header">🎯 Forecast Insights</h2>', unsafe_allow_html=True)
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        trend_direction = "increasing" if predictions['Prediction'].iloc[-1] > predictions['Prediction'].iloc[0] else "decreasing"
        trend_emoji = "📈" if trend_direction == "increasing" else "📉"
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>{trend_emoji} Demand Trend</h4>
            <p>Based on the forecast, your hotel demand shows <strong>{trend_direction}</strong> patterns during this period.</p>
            <br>
            <p><strong>Change:</strong> {predictions['Prediction'].iloc[-1] - predictions['Prediction'].iloc[0]:.0f} guests from start to end</p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        # Weekly patterns
        day_avg = predictions.groupby(predictions['Date'].dt.dayofweek)['Prediction'].mean()
        peak_day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_avg.idxmax()]
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>📅 Weekly Pattern</h4>
            <p>Highest demand is typically expected on <strong>{peak_day}s</strong> during this forecast period.</p>
            <br>
            <p><strong>Average on {peak_day}:</strong> {day_avg.max():.0f} guests</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #cccccc; padding: 3rem; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); border-radius: 20px; margin-top: 2rem; border: 1px solid #333333;">
    <h3 style="color: #FFD700; margin-bottom: 1rem;">🏨 Hotel Intelligence Dashboard</h3>
    <p style="color: #FFA500; font-size: 1.1rem; margin-bottom: 0.5rem;"><strong>Powered by Facebook Prophet Machine Learning</strong></p>
    <p style="color: #cccccc;">📊 Built with Streamlit & Python | ⚡ Optimized for Performance</p>
    <p style="color: #999999; font-size: 0.9rem;">Last Updated: {datetime.now().strftime('%B %Y')}</p>
</div>
""", unsafe_allow_html=True)