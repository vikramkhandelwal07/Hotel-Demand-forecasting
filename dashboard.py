import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Hotel Booking Analytics Dashboard",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #fafafa;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🏨 Hotel Booking Analytics Dashboard</p>', unsafe_allow_html=True)

# File upload section
st.sidebar.title("📁 Data Upload")
uploaded_file = st.sidebar.file_uploader(
    "Upload your hotel booking CSV file",
    type=['csv'],
    help="Upload a CSV file with hotel booking data"
)

if uploaded_file is not None:
    # Load data
    @st.cache_data
    def load_data(file):
        df = pd.read_csv(file)
        # Convert date columns if they exist
        if 'reservation_status_date' in df.columns:
            df['reservation_status_date'] = pd.to_datetime(df['reservation_status_date'])
        if 'arrival_date' in df.columns:
            df['arrival_date'] = pd.to_datetime(df['arrival_date'])
        return df
    
    try:
        data = load_data(uploaded_file)
        
        # Sidebar for navigation and filters
        st.sidebar.title("🎛️ Dashboard Controls")
        
        # Navigation
        page = st.sidebar.selectbox(
            "Select Analysis Page",
            ["📊 Overview", "📈 Univariate Analysis", "🔗 Bivariate Analysis", "📅 Time Series", "🌍 Geographic Analysis", "🎯 Advanced Analytics"]
        )
        
        # Global filters
        st.sidebar.subheader("🔍 Global Filters")
        
        # Hotel filter
        if 'hotel' in data.columns:
            selected_hotels = st.sidebar.multiselect(
                "Select Hotels", 
                data['hotel'].unique(), 
                default=data['hotel'].unique()
            )
        else:
            selected_hotels = []
        
        # Year filter
        if 'arrival_date_year' in data.columns:
            selected_years = st.sidebar.multiselect(
                "Select Years", 
                sorted(data['arrival_date_year'].unique()), 
                default=sorted(data['arrival_date_year'].unique())
            )
        else:
            selected_years = []
        
        # Filter data based on selections
        filtered_data = data.copy()
        if selected_hotels and 'hotel' in data.columns:
            filtered_data = filtered_data[filtered_data['hotel'].isin(selected_hotels)]
        if selected_years and 'arrival_date_year' in data.columns:
            filtered_data = filtered_data[filtered_data['arrival_date_year'].isin(selected_years)]
        
        # Overview Page
        if page == "📊 Overview":
            st.header("📊 Dataset Overview")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Bookings", f"{len(filtered_data):,}")
            
            with col2:
                if 'is_canceled' in filtered_data.columns:
                    cancellation_rate = (filtered_data['is_canceled'].sum() / len(filtered_data)) * 100
                    st.metric("Cancellation Rate", f"{cancellation_rate:.1f}%")
                else:
                    st.metric("Cancellation Rate", "N/A")
            
            with col3:
                if 'adr' in filtered_data.columns:
                    avg_adr = filtered_data['adr'].mean()
                    st.metric("Average ADR", f"${avg_adr:.2f}")
                else:
                    st.metric("Average ADR", "N/A")
            
            with col4:
                if 'lead_time' in filtered_data.columns:
                    avg_lead_time = filtered_data['lead_time'].mean()
                    st.metric("Avg Lead Time", f"{avg_lead_time:.0f} days")
                else:
                    st.metric("Avg Lead Time", "N/A")
            
            # Dataset information
            st.subheader("📋 Dataset Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Dataset Shape:**", filtered_data.shape)
                st.write("**Columns:**", len(filtered_data.columns))
                
                # Missing values
                st.write("**Missing Values:**")
                missing_vals = filtered_data.isnull().sum()
                if missing_vals.sum() == 0:
                    st.success("No missing values found! ✅")
                else:
                    missing_df = pd.DataFrame({
                        'Column': missing_vals.index,
                        'Missing Count': missing_vals.values,
                        'Missing %': (missing_vals.values / len(filtered_data) * 100).round(2)
                    })
                    st.dataframe(missing_df[missing_df['Missing Count'] > 0])
            
            with col2:
                st.write("**Data Types:**")
                dtypes_df = pd.DataFrame({
                    'Column': filtered_data.dtypes.index,
                    'Data Type': filtered_data.dtypes.values
                })
                st.dataframe(dtypes_df.head(15), use_container_width=True)
            
            # Quick statistics for numerical columns
            st.subheader("📊 Numerical Columns Statistics")
            numeric_cols = filtered_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.dataframe(filtered_data[numeric_cols].describe(), use_container_width=True)
            else:
                st.info("No numerical columns found in the dataset.")
            
            # Sample data preview
            st.subheader("👀 Data Preview")
            st.dataframe(filtered_data.head(10), use_container_width=True)
        
        # Univariate Analysis Page
        elif page == "📈 Univariate Analysis":
            st.header("📈 Univariate Analysis")
            
            tab1, tab2, tab3 = st.tabs(["📊 Numerical Distributions", "📈 Categorical Analysis", "🎯 Key Metrics"])
            
            with tab1:
                st.subheader("Numerical Variable Distributions")
                
                # Lead Time Distribution
                if 'lead_time' in filtered_data.columns:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig1 = px.histogram(
                            filtered_data, 
                            x='lead_time', 
                            nbins=50,
                            title='Lead Time Distribution',
                            labels={'lead_time': 'Lead Time (days)', 'count': 'Frequency'}
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        fig1b = px.box(
                            filtered_data, 
                            y='lead_time',
                            title='Lead Time Box Plot'
                        )
                        st.plotly_chart(fig1b, use_container_width=True)
                
                # ADR Distribution
                if 'adr' in filtered_data.columns:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig2 = px.histogram(
                            filtered_data, 
                            x='adr',
                            nbins=50,
                            title='Average Daily Rate (ADR) Distribution',
                            labels={'adr': 'ADR ($)', 'count': 'Frequency'}
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    with col2:
                        fig2b = px.box(
                            filtered_data, 
                            y='adr',
                            title='ADR Box Plot'
                        )
                        st.plotly_chart(fig2b, use_container_width=True)
                
                # Total People Distribution
                if 'total people' in filtered_data.columns:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig3 = px.histogram(
                            filtered_data, 
                            x='total people',
                            title='Total People per Booking Distribution'
                        )
                        st.plotly_chart(fig3, use_container_width=True)
                    
                    # Stay Duration Distribution
                    if 'total stayed' in filtered_data.columns:
                        with col2:
                            fig4 = px.histogram(
                                filtered_data, 
                                x='total stayed',
                                title='Total Stay Duration Distribution',
                                labels={'total stayed': 'Total Nights Stayed'}
                            )
                            st.plotly_chart(fig4, use_container_width=True)
                
                # Weekend vs Weekday stays
                if 'stays_in_weekend_nights' in filtered_data.columns and 'stays_in_week_nights' in filtered_data.columns:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig5 = px.histogram(
                            filtered_data, 
                            x='stays_in_weekend_nights',
                            title='Weekend Nights Distribution'
                        )
                        st.plotly_chart(fig5, use_container_width=True)
                    
                    with col2:
                        fig6 = px.histogram(
                            filtered_data, 
                            x='stays_in_week_nights',
                            title='Week Nights Distribution'
                        )
                        st.plotly_chart(fig6, use_container_width=True)
            
            with tab2:
                st.subheader("Categorical Variable Distributions")
                
                col1, col2 = st.columns(2)
                
                # Hotel Type Distribution
                if 'hotel' in filtered_data.columns:
                    with col1:
                        hotel_counts = filtered_data['hotel'].value_counts()
                        fig7 = px.pie(
                            values=hotel_counts.values, 
                            names=hotel_counts.index,
                            title='Hotel Type Distribution'
                        )
                        st.plotly_chart(fig7, use_container_width=True)
                
                # Cancellation Distribution
                if 'is_canceled' in filtered_data.columns:
                    with col2:
                        cancel_counts = filtered_data['is_canceled'].value_counts()
                        fig8 = px.pie(
                            values=cancel_counts.values,
                            names=['Not Canceled', 'Canceled'],
                            title='Booking Cancellation Distribution'
                        )
                        st.plotly_chart(fig8, use_container_width=True)
                
                # Market Segment Distribution
                if 'market_segment' in filtered_data.columns:
                    col1, col2 = st.columns(2)
                    with col1:
                        market_counts = filtered_data['market_segment'].value_counts()
                        fig9 = px.bar(
                            x=market_counts.values,
                            y=market_counts.index,
                            orientation='h',
                            title='Market Segment Distribution'
                        )
                        st.plotly_chart(fig9, use_container_width=True)
        
        # Geographic Analysis Page
        elif page == "🌍 Geographic Analysis":
            st.header("🌍 Geographic Analysis")
            
            tab1, tab2, tab3 = st.tabs(["🌎 Country Analysis", "📊 Regional Patterns", "🎯 Geographic Insights"])
            
            with tab1:
                st.subheader("Country-wise Booking Analysis")
                
                if 'country' in filtered_data.columns:
                    # Top countries by booking count
                    top_countries = filtered_data['country'].value_counts().head(15)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig1 = px.bar(
                            x=top_countries.values,
                            y=top_countries.index,
                            orientation='h',
                            title='Top 15 Countries by Booking Volume',
                            labels={'x': 'Number of Bookings', 'y': 'Country'}
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        fig2 = px.pie(
                            values=top_countries.head(10).values,
                            names=top_countries.head(10).index,
                            title='Top 10 Countries Distribution'
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    # Country-wise ADR analysis
                    if 'adr' in filtered_data.columns:
                        country_adr = filtered_data.groupby('country')['adr'].agg(['mean', 'count']).reset_index()
                        country_adr = country_adr[country_adr['count'] >= 50]  # Filter countries with at least 50 bookings
                        country_adr = country_adr.sort_values('mean', ascending=False).head(15)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            fig3 = px.bar(
                                country_adr,
                                x='mean',
                                y='country',
                                orientation='h',
                                title='Average ADR by Country (min 50 bookings)',
                                labels={'mean': 'Average ADR ($)', 'country': 'Country'}
                            )
                            st.plotly_chart(fig3, use_container_width=True)
                        
                        # Country-wise cancellation rate
                        if 'is_canceled' in filtered_data.columns:
                            with col2:
                                country_cancel = filtered_data.groupby('country').agg({
                                    'is_canceled': ['mean', 'count']
                                }).reset_index()
                                country_cancel.columns = ['country', 'cancel_rate', 'count']
                                country_cancel = country_cancel[country_cancel['count'] >= 50]
                                country_cancel = country_cancel.sort_values('cancel_rate', ascending=False).head(15)
                                
                                fig4 = px.bar(
                                    country_cancel,
                                    x='cancel_rate',
                                    y='country',
                                    orientation='h',
                                    title='Cancellation Rate by Country (min 50 bookings)',
                                    labels={'cancel_rate': 'Cancellation Rate', 'country': 'Country'}
                                )
                                fig4.update_xaxis(tickformat='.2%')
                                st.plotly_chart(fig4, use_container_width=True)
            
            with tab2:
                st.subheader("Regional Booking Patterns")
                
                if 'country' in filtered_data.columns and 'arrival_date_month' in filtered_data.columns:
                    # Get top 5 countries for monthly analysis
                    top_5_countries = filtered_data['country'].value_counts().head(5).index
                    top_countries_data = filtered_data[filtered_data['country'].isin(top_5_countries)]
                    
                    monthly_country = top_countries_data.groupby(['arrival_date_month', 'country']).size().reset_index(name='bookings')
                    
                    fig5 = px.line(
                        monthly_country,
                        x='arrival_date_month',
                        y='bookings',
                        color='country',
                        title='Monthly Booking Trends - Top 5 Countries'
                    )
                    fig5.update_xaxis(tickangle=45)
                    st.plotly_chart(fig5, use_container_width=True)
                
                # Lead time by country
                if 'lead_time' in filtered_data.columns and 'country' in filtered_data.columns:
                    country_leadtime = filtered_data.groupby('country').agg({
                        'lead_time': ['mean', 'count']
                    }).reset_index()
                    country_leadtime.columns = ['country', 'avg_lead_time', 'count']
                    country_leadtime = country_leadtime[country_leadtime['count'] >= 50]
                    country_leadtime = country_leadtime.sort_values('avg_lead_time', ascending=False).head(15)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig6 = px.bar(
                            country_leadtime,
                            x='avg_lead_time',
                            y='country',
                            orientation='h',
                            title='Average Lead Time by Country (min 50 bookings)',
                            labels={'avg_lead_time': 'Average Lead Time (days)', 'country': 'Country'}
                        )
                        st.plotly_chart(fig6, use_container_width=True)
                
                # Stay duration by country
                if 'total stayed' in filtered_data.columns and 'country' in filtered_data.columns:
                    with col2:
                        country_stay = filtered_data.groupby('country').agg({
                            'total stayed': ['mean', 'count']
                        }).reset_index()
                        country_stay.columns = ['country', 'avg_stay', 'count']
                        country_stay = country_stay[country_stay['count'] >= 50]
                        country_stay = country_stay.sort_values('avg_stay', ascending=False).head(15)
                        
                        fig7 = px.bar(
                            country_stay,
                            x='avg_stay',
                            y='country',
                            orientation='h',
                            title='Average Stay Duration by Country (min 50 bookings)',
                            labels={'avg_stay': 'Average Stay (nights)', 'country': 'Country'}
                        )
                        st.plotly_chart(fig7, use_container_width=True)
            
            with tab3:
                st.subheader("Geographic Insights")
                
                # Country statistics table
                if 'country' in filtered_data.columns:
                    country_stats = filtered_data.groupby('country').agg({
                        'hotel': 'count',
                        'is_canceled': 'mean' if 'is_canceled' in filtered_data.columns else 'count',
                        'adr': 'mean' if 'adr' in filtered_data.columns else 'count',
                        'lead_time': 'mean' if 'lead_time' in filtered_data.columns else 'count',
                        'total stayed': 'mean' if 'total stayed' in filtered_data.columns else 'count'
                    }).reset_index()
                    
                    country_stats.columns = ['Country', 'Total_Bookings', 'Cancellation_Rate', 'Avg_ADR', 'Avg_Lead_Time', 'Avg_Stay_Duration']
                    country_stats = country_stats[country_stats['Total_Bookings'] >= 20]  # Filter for meaningful data
                    country_stats = country_stats.sort_values('Total_Bookings', ascending=False)
                    
                    st.subheader("Country Statistics Summary")
                    st.dataframe(country_stats.head(20), use_container_width=True)
                    
                    # Interactive country selector for detailed analysis
                    st.subheader("Detailed Country Analysis")
                    selected_country = st.selectbox(
                        "Select a country for detailed analysis:",
                        country_stats['Country'].head(20).tolist()
                    )
                    
                    if selected_country:
                        country_data = filtered_data[filtered_data['country'] == selected_country]
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Bookings", len(country_data))
                        with col2:
                            if 'is_canceled' in country_data.columns:
                                cancel_rate = (country_data['is_canceled'].mean() * 100)
                                st.metric("Cancellation Rate", f"{cancel_rate:.1f}%")
                        with col3:
                            if 'adr' in country_data.columns:
                                avg_adr = country_data['adr'].mean()
                                st.metric("Average ADR", f"${avg_adr:.2f}")
                        with col4:
                            if 'lead_time' in country_data.columns:
                                avg_lead = country_data['lead_time'].mean()
                                st.metric("Avg Lead Time", f"{avg_lead:.0f} days")
        
        # Advanced Analytics Page
        elif page == "🎯 Advanced Analytics":
            st.header("🎯 Advanced Analytics")
            
            tab1, tab2, tab3 = st.tabs(["🔍 Segmentation Analysis", "📈 Revenue Analysis", "🎨 Custom Analysis"])
            
            with tab1:
                st.subheader("Customer Segmentation Analysis")
                
                # Market segment analysis
                if 'market_segment' in filtered_data.columns:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        segment_stats = filtered_data.groupby('market_segment').agg({
                            'hotel': 'count',
                            'is_canceled': 'mean' if 'is_canceled' in filtered_data.columns else 'count',
                            'adr': 'mean' if 'adr' in filtered_data.columns else 'count',
                            'lead_time': 'mean' if 'lead_time' in filtered_data.columns else 'count'
                        }).reset_index()
                        
                        if 'adr' in filtered_data.columns:
                            fig1 = px.bar(
                                segment_stats,
                                x='market_segment',
                                y='adr',
                                title='Average ADR by Market Segment'
                            )
                            fig1.update_xaxis(tickangle=45)
                            st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        if 'is_canceled' in filtered_data.columns:
                            fig2 = px.bar(
                                segment_stats,
                                x='market_segment',
                                y='is_canceled',
                                title='Cancellation Rate by Market Segment'
                            )
                            fig2.update_xaxis(tickangle=45)
                            fig2.update_yaxis(tickformat='.2%')
                            st.plotly_chart(fig2, use_container_width=True)
                
                # Customer type analysis
                if 'customer_type' in filtered_data.columns:
                    customer_stats = filtered_data.groupby('customer_type').agg({
                        'hotel': 'count',
                        'is_canceled': 'mean' if 'is_canceled' in filtered_data.columns else 'count',
                        'adr': 'mean' if 'adr' in filtered_data.columns else 'count',
                        'lead_time': 'mean' if 'lead_time' in filtered_data.columns else 'count'
                    }).reset_index()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if 'lead_time' in filtered_data.columns:
                            fig3 = px.bar(
                                customer_stats,
                                x='customer_type',
                                y='lead_time',
                                title='Average Lead Time by Customer Type'
                            )
                            st.plotly_chart(fig3, use_container_width=True)
                    
                    with col2:
                        fig4 = px.pie(
                            customer_stats,
                            values='hotel',
                            names='customer_type',
                            title='Booking Distribution by Customer Type'
                        )
                        st.plotly_chart(fig4, use_container_width=True)
            
            with tab2:
                st.subheader("Revenue Analysis")
                
                if 'adr' in filtered_data.columns and 'total stayed' in filtered_data.columns:
                    # Calculate total revenue per booking
                    filtered_data_copy = filtered_data.copy()
                    filtered_data_copy['total_revenue'] = filtered_data_copy['adr'] * filtered_data_copy['total stayed']
                    
                    # Revenue by hotel type
                    if 'hotel' in filtered_data.columns:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            revenue_by_hotel = filtered_data_copy.groupby('hotel')['total_revenue'].agg(['sum', 'mean', 'count']).reset_index()
                            fig1 = px.bar(
                                revenue_by_hotel,
                                x='hotel',
                                y='sum',
                                title='Total Revenue by Hotel Type'
                            )
                            st.plotly_chart(fig1, use_container_width=True)
                        
                        with col2:
                            fig2 = px.bar(
                                revenue_by_hotel,
                                x='hotel',
                                y='mean',
                                title='Average Revenue per Booking by Hotel Type'
                            )
                            st.plotly_chart(fig2, use_container_width=True)
                    
                    # Monthly revenue analysis
                    if 'arrival_date_month' in filtered_data.columns:
                        monthly_revenue = filtered_data_copy.groupby('arrival_date_month')['total_revenue'].sum().reindex(
                            ['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December']
                        ).reset_index()
                        
                        fig3 = px.line(
                            monthly_revenue,
                            x='arrival_date_month',
                            y='total_revenue',
                            title='Monthly Revenue Trend'
                        )
                        fig3.update_xaxis(tickangle=45)
                        st.plotly_chart(fig3, use_container_width=True)
                    
                    # Revenue insights
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        total_revenue = filtered_data_copy['total_revenue'].sum()
                        st.metric("Total Revenue", f"${total_revenue:,.2f}")
                    
                    with col2:
                        avg_revenue_per_booking = filtered_data_copy['total_revenue'].mean()
                        st.metric("Avg Revenue/Booking", f"${avg_revenue_per_booking:.2f}")
                    
                    with col3:
                        if 'is_canceled' in filtered_data.columns:
                            lost_revenue = filtered_data_copy[filtered_data_copy['is_canceled'] == 1]['total_revenue'].sum()
                            st.metric("Potential Lost Revenue", f"${lost_revenue:,.2f}")
                    
                    with col4:
                        revenue_per_night = filtered_data_copy['adr'].mean()
                        st.metric("Avg Revenue/Night", f"${revenue_per_night:.2f}")
            
            with tab3:
                st.subheader("Custom Analysis Builder")
                
                # Interactive analysis builder
                analysis_type = st.selectbox(
                    "Select Analysis Type",
                    ["Distribution Analysis", "Comparison Analysis", "Trend Analysis"]
                )
                
                if analysis_type == "Distribution Analysis":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        categorical_cols = filtered_data.select_dtypes(include=['object']).columns
                        selected_cat_var = st.selectbox("Select Categorical Variable", categorical_cols)
                    
                    with col2:
                        chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart"])
                    
                    if selected_cat_var:
                        var_counts = filtered_data[selected_cat_var].value_counts()
                        
                        if chart_type == "Bar Chart":
                            fig = px.bar(
                                x=var_counts.index,
                                y=var_counts.values,
                                title=f'Distribution of {selected_cat_var}'
                            )
                        else:
                            fig = px.pie(
                                values=var_counts.values,
                                names=var_counts.index,
                                title=f'Distribution of {selected_cat_var}'
                            )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                elif analysis_type == "Comparison Analysis":
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        numeric_cols = filtered_data.select_dtypes(include=[np.number]).columns
                        selected_num_var = st.selectbox("Select Numeric Variable", numeric_cols)
                    
                    with col2:
                        categorical_cols = filtered_data.select_dtypes(include=['object']).columns
                        selected_group_var = st.selectbox("Group By", categorical_cols)
                    
                    with col3:
                        agg_function = st.selectbox("Aggregation Function", ["mean", "sum", "median", "count"])
                    
                    if selected_num_var and selected_group_var:
                        if agg_function == "mean":
                            grouped_data = filtered_data.groupby(selected_group_var)[selected_num_var].mean().reset_index()
                        elif agg_function == "sum":
                            grouped_data = filtered_data.groupby(selected_group_var)[selected_num_var].sum().reset_index()
                        elif agg_function == "median":
                            grouped_data = filtered_data.groupby(selected_group_var)[selected_num_var].median().reset_index()
                        else:
                            grouped_data = filtered_data.groupby(selected_group_var)[selected_num_var].count().reset_index()
                        
                        fig = px.bar(
                            grouped_data,
                            x=selected_group_var,
                            y=selected_num_var,
                            title=f'{agg_function.title()} of {selected_num_var} by {selected_group_var}'
                        )
                        fig.update_xaxis(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                
                elif analysis_type == "Trend Analysis":
                    if 'arrival_date_month' in filtered_data.columns:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            numeric_cols = filtered_data.select_dtypes(include=[np.number]).columns
                            selected_trend_var = st.selectbox("Select Variable for Trend", numeric_cols)
                        
                        with col2:
                            trend_agg = st.selectbox("Aggregation for Trend", ["mean", "sum", "count"])
                        
                        if selected_trend_var:
                            month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                                         'July', 'August', 'September', 'October', 'November', 'December']
                            
                            if trend_agg == "mean":
                                trend_data = filtered_data.groupby('arrival_date_month')[selected_trend_var].mean().reindex(month_order).reset_index()
                            elif trend_agg == "sum":
                                trend_data = filtered_data.groupby('arrival_date_month')[selected_trend_var].sum().reindex(month_order).reset_index()
                            else:
                                trend_data = filtered_data.groupby('arrival_date_month')[selected_trend_var].count().reindex(month_order).reset_index()
                            
                            fig = px.line(
                                trend_data,
                                x='arrival_date_month',
                                y=selected_trend_var,
                                title=f'{trend_agg.title()} of {selected_trend_var} Over Months'
                            )
                            fig.update_xaxis(tickangle=45)
                            st.plotly_chart(fig, use_container_width=True)
                
                # Data export functionality
                st.subheader("📥 Data Export")
                
                export_data = st.selectbox(
                    "Select data to export",
                    ["Filtered Dataset", "Summary Statistics", "Country Analysis"]
                )
                
                if st.button("Generate Export Data"):
                    if export_data == "Filtered Dataset":
                        csv = filtered_data.to_csv(index=False)
                        st.download_button(
                            label="Download Filtered Data as CSV",
                            data=csv,
                            file_name='hotel_booking_filtered_data.csv',
                            mime='text/csv'
                        )
                    
                    elif export_data == "Summary Statistics":
                        numeric_cols = filtered_data.select_dtypes(include=[np.number]).columns
                        summary_stats = filtered_data[numeric_cols].describe()
                        csv = summary_stats.to_csv()
                        st.download_button(
                            label="Download Summary Statistics as CSV",
                            data=csv,
                            file_name='hotel_booking_summary_stats.csv',
                            mime='text/csv'
                        )
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please make sure your CSV file has the correct format and column names.")

else:
    st.info("👆 Please upload a CSV file to begin the analysis")
    
    # Show expected data format
    st.subheader("📋 Expected Data Format")
    st.write("Your CSV file should contain the following columns:")
    
    expected_columns = [
        'hotel', 'is_canceled', 'lead_time', 'arrival_date_year', 'arrival_date_month', 
        'arrival_date_week_number', 'arrival_date_day_of_month', 'stays_in_weekend_nights', 
        'stays_in_week_nights', 'adults', 'children', 'babies', 'meal', 'country', 
        'market_segment', 'distribution_channel', 'is_repeated_guest', 'previous_cancellations', 
        'previous_bookings_not_canceled', 'reserved_room_type', 'assigned_room_type', 
        'booking_changes', 'deposit_type', 'agent', 'company', 'days_in_waiting_list', 
        'customer_type', 'adr', 'required_car_parking_spaces', 'total_of_special_requests', 
        'reservation_status', 'reservation_status_date', 'total people', 'total stayed'
    ]
    
    # Display in a nice format
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Columns 1-17:**")
        for i, col in enumerate(expected_columns[:17]):
            st.write(f"{i+1}. {col}")
    
    with col2:
        st.write("**Columns 18-34:**")
        for i, col in enumerate(expected_columns[17:], 18):
            st.write(f"{i}. {col}")
    
    st.info("💡 The dashboard will automatically detect which columns are available in your dataset and adapt the visualizations accordingly.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🏨 Hotel Booking Analytics Dashboard | Built with Streamlit & Plotly</p>
    </div>
    """, 
    unsafe_allow_html=True
)
                
                # Customer Type Distribution
                if 'customer_type' in filtered_data.columns:
                    with col2:
                        customer_counts = filtered_data['customer_type'].value_counts()
                        fig10 = px.bar(
                            x=customer_counts.index,
                            y=customer_counts.values,
                            title='Customer Type Distribution'
                        )
                        fig10.update_xaxis(tickangle=45)
                        st.plotly_chart(fig10, use_container_width=True)
                
                # Meal Type Distribution
                if 'meal' in filtered_data.columns:
                    col1, col2 = st.columns(2)
                    with col1:
                        meal_counts = filtered_data['meal'].value_counts()
                        fig11 = px.pie(
                            values=meal_counts.values,
                            names=meal_counts.index,
                            title='Meal Preference Distribution'
                        )
                        st.plotly_chart(fig11, use_container_width=True)
                
                # Distribution Channel
                if 'distribution_channel' in filtered_data.columns:
                    with col2:
                        dist_counts = filtered_data['distribution_channel'].value_counts()
                        fig12 = px.bar(
                            x=dist_counts.index,
                            y=dist_counts.values,
                            title='Distribution Channel Usage'
                        )
                        st.plotly_chart(fig12, use_container_width=True)
            
            with tab3:
                st.subheader("Key Metrics and Insights")
                
                # Create metrics based on available columns
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                with metrics_col1:
                    if 'hotel' in filtered_data.columns:
                        most_popular_hotel = filtered_data['hotel'].mode()[0]
                        hotel_percentage = (filtered_data['hotel'].value_counts().iloc[0]/len(filtered_data)*100)
                        st.metric("Most Popular Hotel", most_popular_hotel, f"{hotel_percentage:.1f}% of bookings")
                    
                    if 'total_of_special_requests' in filtered_data.columns:
                        avg_special_requests = filtered_data['total_of_special_requests'].mean()
                        st.metric("Avg Special Requests", f"{avg_special_requests:.2f}", "per booking")
                
                with metrics_col2:
                    if 'arrival_date_month' in filtered_data.columns:
                        most_popular_month = filtered_data['arrival_date_month'].mode()[0]
                        month_percentage = (filtered_data['arrival_date_month'].value_counts().iloc[0]/len(filtered_data)*100)
                        st.metric("Peak Month", most_popular_month, f"{month_percentage:.1f}% of arrivals")
                    
                    if 'is_repeated_guest' in filtered_data.columns:
                        repeat_rate = (filtered_data['is_repeated_guest'].sum()/len(filtered_data)*100)
                        st.metric("Repeat Guest Rate", f"{repeat_rate:.1f}%", "returning customers")
                
                with metrics_col3:
                    if 'adults' in filtered_data.columns:
                        avg_adults = filtered_data['adults'].mean()
                        st.metric("Avg Adults per Booking", f"{avg_adults:.1f}", "adults")
                    
                    if 'required_car_parking_spaces' in filtered_data.columns:
                        parking_rate = (filtered_data['required_car_parking_spaces'].sum()/len(filtered_data)*100)
                        st.metric("Parking Request Rate", f"{parking_rate:.1f}%", "need parking")
        
        # Bivariate Analysis Page
        elif page == "🔗 Bivariate Analysis":
            st.header("🔗 Bivariate Analysis")
            
            tab1, tab2, tab3 = st.tabs(["📊 Correlations", "🎯 Key Relationships", "📈 Comparative Analysis"])
            
            with tab1:
                st.subheader("Correlation Analysis")
                
                # Correlation Heatmap
                numeric_cols = filtered_data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 1:
                    correlation_matrix = filtered_data[numeric_cols].corr()
                    
                    fig_corr = px.imshow(
                        correlation_matrix,
                        title='Correlation Heatmap of Numerical Variables',
                        color_continuous_scale='RdBu_r',
                        aspect='auto'
                    )
                    fig_corr.update_layout(height=600)
                    st.plotly_chart(fig_corr, use_container_width=True)
                    
                    # Show strongest correlations
                    st.subheader("Strongest Correlations")
                    corr_pairs = []
                    for i in range(len(correlation_matrix.columns)):
                        for j in range(i+1, len(correlation_matrix.columns)):
                            corr_pairs.append({
                                'Variable 1': correlation_matrix.columns[i],
                                'Variable 2': correlation_matrix.columns[j],
                                'Correlation': correlation_matrix.iloc[i,j]
                            })
                    
                    corr_df = pd.DataFrame(corr_pairs)
                    corr_df = corr_df.reindex(corr_df['Correlation'].abs().sort_values(ascending=False).index)
                    st.dataframe(corr_df.head(10), use_container_width=True)
                else:
                    st.info("Not enough numerical columns for correlation analysis.")
            
            with tab2:
                st.subheader("Key Relationships")
                
                # ADR vs Lead Time
                if 'adr' in filtered_data.columns and 'lead_time' in filtered_data.columns:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig1 = px.scatter(
                            filtered_data.sample(min(5000, len(filtered_data))),
                            x='lead_time',
                            y='adr',
                            title='ADR vs Lead Time',
                            opacity=0.6
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                
                # ADR vs Total Stayed
                if 'adr' in filtered_data.columns and 'total stayed' in filtered_data.columns:
                    with col2:
                        fig2 = px.scatter(
                            filtered_data.sample(min(5000, len(filtered_data))),
                            x='total stayed',
                            y='adr',
                            title='ADR vs Total Stayed',
                            opacity=0.6
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                
                # Cancellation Rate by Lead Time
                if 'is_canceled' in filtered_data.columns and 'lead_time' in filtered_data.columns:
                    # Create lead time bins
                    filtered_data_copy = filtered_data.copy()
                    filtered_data_copy['lead_time_bin'] = pd.cut(
                        filtered_data_copy['lead_time'], 
                        bins=10, 
                        labels=[f'{i*10}-{(i+1)*10}' for i in range(10)]
                    )
                    cancel_by_leadtime = filtered_data_copy.groupby('lead_time_bin')['is_canceled'].mean().reset_index()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig3 = px.bar(
                            cancel_by_leadtime,
                            x='lead_time_bin',
                            y='is_canceled',
                            title='Cancellation Rate by Lead Time Bins'
                        )
                        fig3.update_xaxis(tickangle=45)
                        st.plotly_chart(fig3, use_container_width=True)
                
                # Reservation Status by Hotel Type
                if 'reservation_status' in filtered_data.columns and 'hotel' in filtered_data.columns:
                    with col2:
                        status_hotel = filtered_data.groupby(['hotel', 'reservation_status']).size().reset_index(name='count')
                        fig4 = px.bar(
                            status_hotel,
                            x='hotel',
                            y='count',
                            color='reservation_status',
                            title='Reservation Status by Hotel Type',
                            barmode='group'
                        )
                        st.plotly_chart(fig4, use_container_width=True)
                
                # Booking Changes vs ADR
                if 'booking_changes' in filtered_data.columns and 'adr' in filtered_data.columns:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig5 = px.box(
                            filtered_data,
                            x='booking_changes',
                            y='adr',
                            title='ADR Distribution by Number of Booking Changes'
                        )
                        st.plotly_chart(fig5, use_container_width=True)
                
                # Total Stayed vs Special Requests
                if 'total stayed' in filtered_data.columns and 'total_of_special_requests' in filtered_data.columns:
                    with col2:
                        fig6 = px.violin(
                            filtered_data,
                            x='total_of_special_requests',
                            y='total stayed',
                            title='Stay Duration vs Special Requests'
                        )
                        st.plotly_chart(fig6, use_container_width=True)
            
            with tab3:
                st.subheader("Comparative Analysis")
                
                # Interactive scatter plot selector
                numeric_cols = filtered_data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        x_var = st.selectbox("Select X Variable", numeric_cols, index=0)
                    with col2:
                        y_var = st.selectbox("Select Y Variable", numeric_cols, index=1)
                    with col3:
                        color_var = st.selectbox("Color by (optional)", ['None'] + list(filtered_data.select_dtypes(include=['object']).columns))
                    
                    # Create scatter plot
                    sample_data = filtered_data.sample(min(5000, len(filtered_data)))
                    if color_var != 'None':
                        fig_interactive = px.scatter(
                            sample_data,
                            x=x_var,
                            y=y_var,
                            color=color_var,
                            title=f'{y_var} vs {x_var} (colored by {color_var})',
                            opacity=0.6
                        )
                    else:
                        fig_interactive = px.scatter(
                            sample_data,
                            x=x_var,
                            y=y_var,
                            title=f'{y_var} vs {x_var}',
                            opacity=0.6
                        )
                    
                    st.plotly_chart(fig_interactive, use_container_width=True)
        
        # Time Series Analysis Page
        elif page == "📅 Time Series":
            st.header("📅 Time Series Analysis")
            
            tab1, tab2, tab3 = st.tabs(["📈 Monthly Trends", "📊 Seasonal Patterns", "🎯 Time-based Insights"])
            
            with tab1:
                st.subheader("Monthly Booking Trends")
                
                # Monthly booking counts
                if 'arrival_date_month' in filtered_data.columns:
                    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                                 'July', 'August', 'September', 'October', 'November', 'December']
                    
                    monthly_bookings = filtered_data.groupby('arrival_date_month').size().reindex(month_order).reset_index(name='bookings')
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig1 = px.bar(
                            monthly_bookings,
                            x='arrival_date_month',
                            y='bookings',
                            title='Monthly Booking Volume'
                        )
                        fig1.update_xaxis(tickangle=45)
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        fig2 = px.line(
                            monthly_bookings,
                            x='arrival_date_month',
                            y='bookings',
                            title='Monthly Booking Trend Line'
                        )
                        fig2.update_xaxis(tickangle=45)
                        st.plotly_chart(fig2, use_container_width=True)
                
                # ADR trend over months
                if 'adr' in filtered_data.columns and 'arrival_date_month' in filtered_data.columns:
                    monthly_adr = filtered_data.groupby('arrival_date_month')['adr'].mean().reindex(month_order).reset_index()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig3 = px.line(
                            monthly_adr,
                            x='arrival_date_month',
                            y='adr',
                            title='Average ADR Trend by Month'
                        )
                        fig3.update_xaxis(tickangle=45)
                        st.plotly_chart(fig3, use_container_width=True)
                
                # Cancellation rate over months
                if 'is_canceled' in filtered_data.columns and 'arrival_date_month' in filtered_data.columns:
                    with col2:
                        monthly_cancel = filtered_data.groupby('arrival_date_month')['is_canceled'].mean().reindex(month_order).reset_index()
                        fig4 = px.line(
                            monthly_cancel,
                            x='arrival_date_month',
                            y='is_canceled',
                            title='Cancellation Rate by Month'
                        )
                        fig4.update_xaxis(tickangle=45)
                        fig4.update_yaxis(tickformat='.2%')
                        st.plotly_chart(fig4, use_container_width=True)
            
            with tab2:
                st.subheader("Seasonal Patterns")
                
                # Weekly patterns
                if 'arrival_date_week_number' in filtered_data.columns:
                    weekly_bookings = filtered_data.groupby('arrival_date_week_number').size().reset_index(name='bookings')
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig5 = px.line(
                            weekly_bookings,
                            x='arrival_date_week_number',
                            y='bookings',
                            title='Bookings by Week Number'
                        )
                        st.plotly_chart(fig5, use_container_width=True)
                
                # Day of month patterns
                if 'arrival_date_day_of_month' in filtered_data.columns:
                    with col2:
                        daily_bookings = filtered_data.groupby('arrival_date_day_of_month').size().reset_index(name='bookings')
                        fig6 = px.bar(
                            daily_bookings,
                            x='arrival_date_day_of_month',
                            y='bookings',
                            title='Bookings by Day of Month'
                        )
                        st.plotly_chart(fig6, use_container_width=True)
                
                # Yearly comparison
                if 'arrival_date_year' in filtered_data.columns and 'arrival_date_month' in filtered_data.columns:
                    yearly_monthly = filtered_data.groupby(['arrival_date_year', 'arrival_date_month']).size().reset_index(name='bookings')
                    
                    fig7 = px.line(
                        yearly_monthly,
                        x='arrival_date_month',
                        y='bookings',
                        color='arrival_date_year',
                        title='Monthly Bookings Comparison Across Years'
                    )
                    fig7.update_xaxis(tickangle=45)
                    st.plotly_chart(fig7, use_container_width=True)
            
            with tab3:
                st.subheader("Time-based Insights")
                
                # Average stay duration over time
                if 'total stayed' in filtered_data.columns and 'arrival_date_month' in filtered_data.columns:
                    col1, col2 = st.columns(2)
                    with col1:
                        monthly_stay = filtered_data.groupby('arrival_date_month')['total stayed'].mean().reindex(month_order).reset_index()
                        fig8 = px.bar(
                            monthly_stay,
                            x='arrival_date_month',
                            y='total stayed',
                            title='Average Stay Duration by Month'
                        )
                        fig8.update_xaxis(tickangle=45)
                        st.plotly_chart(fig8, use_container_width=True)
                
                # Lead time patterns
                if 'lead_time' in filtered_data.columns and 'arrival_date_month' in filtered_data.columns:
                    with col2:
                        monthly_leadtime = filtered_data.groupby('arrival_date_month')['lead_time'].mean().reindex(month_order).reset_index()
                        fig9 = px.line(
                            monthly_leadtime,
                            x='arrival_date_month',
                            y='lead_time',
                            title='Average Lead Time by Month'
                        )
                        fig9.update_xaxis(tickangle=45)
                        st.plotly_chart(fig9, use_container_width=True)
                
                # Weekend vs Weekday booking patterns
                if 'stays_in_weekend_nights' in filtered_data.columns and 'stays_in_week_nights' in filtered_data.columns:
                    # Calculate total weekend vs weekday nights
                    total_weekend = filtered_data['stays_in_weekend_nights'].sum()
                    total_weekday = filtered_data['stays_in_week_nights'].sum()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig10 = px.pie(
                            values=[total_weekend, total_weekday],
                            names=['Weekend Nights', 'Weekday Nights'],
                            title='Total Weekend vs Weekday Nights Distribution'
                        )
                        st.plotly_chart(fig10, use_container_width=True)
                    
                    # Monthly weekend vs weekday pattern
                    if 'arrival_date_month' in filtered_data.columns:
                        with col2:
                            monthly_nights = filtered_data.groupby('arrival_date_month').agg({
                                'stays_in_weekend_nights': 'sum',
                                'stays_in_week_nights': 'sum'
                            }).reset_index()
                            
                            fig11 = go.Figure()
                            fig11.add_trace(go.Bar(
                                x=monthly_nights['arrival_date_month'],
                                y=monthly_nights['stays_in_weekend_nights'],
                                name='Weekend Nights',
                                marker_color='lightblue'
                            ))
                            fig11.add_trace(go.Bar(
                                x=monthly_nights['arrival_date_month'],
                                y=monthly_nights['stays_in_week_nights'],
                                name='Weekday Nights',
                                marker_color='darkblue'
                            ))
                            fig11.update_layout(
                                title='Monthly Weekend vs Weekday Nights',
                                barmode='stack',
                                xaxis_tickangle=45
                            )
                            st.plotly_chart(fig11, use_container_width=True)
                
                # Time-based metrics summary
                st.subheader("📈 Time-based Summary Statistics")
                
                if 'arrival_date_month' in filtered_data.columns:
                    month_stats = filtered_data.groupby('arrival_date_month').agg({
                        'hotel': 'count',  # Total bookings
                        'is_canceled': 'mean' if 'is_canceled' in filtered_data.columns else 'count',
                        'adr': 'mean' if 'adr' in filtered_data.columns else 'count',
                        'lead_time': 'mean' if 'lead_time' in filtered_data.columns else 'count',
                        'total stayed': 'mean' if 'total stayed' in filtered_data.columns else 'count'
                    }).reset_index()
                    
                    month_stats.columns = ['Month', 'Total_Bookings', 'Cancellation_Rate', 'Avg_ADR', 'Avg_Lead_Time', 'Avg_Stay_Duration']
                    month_stats = month_stats.reindex([
                        filtered_data[filtered_data['arrival_date_month'] == month].index[0] 
                        for month in ['January', 'February', 'March', 'April', 'May', 'June',
                                    'July', 'August', 'September', 'October', 'November', 'December']
                        if month in filtered_data['arrival_date_month'].values
                    ]).reset_index(drop=True)
                    
                    # Reorder by actual month order
                    month_order_dict = {
                        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
                    }
                    month_stats['month_num'] = month_stats['Month'].map(month_order_dict)
                    month_stats = month_stats.sort_values('month_num').drop('month_num', axis=1)
                    
                    st.dataframe(month_stats, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please make sure your CSV file has the correct format and column names.")
        st.exception(e)  # This will help with debugging

else:
    st.info("👆 Please upload a CSV file to begin the analysis")
    
    # Show expected data format
    st.subheader("📋 Expected Data Format")
    st.write("Your CSV file should contain hotel booking data with columns such as:")
    
    expected_columns = [
        'hotel', 'is_canceled', 'lead_time', 'arrival_date_year', 'arrival_date_month', 
        'arrival_date_week_number', 'arrival_date_day_of_month', 'stays_in_weekend_nights', 
        'stays_in_week_nights', 'adults', 'children', 'babies', 'meal', 'country', 
        'market_segment', 'distribution_channel', 'is_repeated_guest', 'previous_cancellations', 
        'previous_bookings_not_canceled', 'reserved_room_type', 'assigned_room_type', 
        'booking_changes', 'deposit_type', 'agent', 'company', 'days_in_waiting_list', 
        'customer_type', 'adr', 'required_car_parking_spaces', 'total_of_special_requests', 
        'reservation_status', 'reservation_status_date', 'total people', 'total stayed'
    ]
    
    # Display in a nice format
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Essential Columns:**")
        essential_cols = ['hotel', 'is_canceled', 'adr', 'lead_time', 'arrival_date_month', 'country', 'total stayed']
        for col in essential_cols:
            st.write(f"• {col}")
        
        st.write("**Date Columns:**")
        date_cols = ['arrival_date_year', 'arrival_date_month', 'arrival_date_week_number', 'reservation_status_date']
        for col in date_cols:
            st.write(f"• {col}")
    
    with col2:
        st.write("**Guest Information:**")
        guest_cols = ['adults', 'children', 'babies', 'total people', 'customer_type', 'is_repeated_guest']
        for col in guest_cols:
            st.write(f"• {col}")
        
        st.write("**Booking Details:**")
        booking_cols = ['market_segment', 'distribution_channel', 'booking_changes', 'total_of_special_requests']
        for col in booking_cols:
            st.write(f"• {col}")
    
    st.info("💡 The dashboard will automatically detect available columns and adapt visualizations accordingly.")
    
    # Sample data format
    st.subheader("📄 Sample Data Format")
    sample_data = pd.DataFrame({
        'hotel': ['Resort Hotel', 'City Hotel', 'Resort Hotel'],
        'is_canceled': [0, 1, 0],
        'lead_time': [342, 737, 7],
        'arrival_date_year': [2015, 2015, 2015],
        'arrival_date_month': ['July', 'July', 'July'],
        'adr': [0.0, 75.0, 75.0],
        'country': ['PRT', 'PRT', 'GBR'],
        'total stayed': [0, 1, 1]
    })
    st.dataframe(sample_data, use_container_width=True)

# Additional Features Section
st.sidebar.markdown("---")
st.sidebar.subheader("📋 Dashboard Features")
st.sidebar.markdown("""
✅ **Overview Analytics**
- Dataset summary & key metrics
- Missing value analysis
- Data type information

✅ **Univariate Analysis**
- Distribution plots
- Box plots for outliers
- Categorical breakdowns

✅ **Bivariate Analysis**
- Correlation heatmaps
- Scatter plots
- Cross-tabulations

✅ **Time Series Analysis**
- Monthly trends
- Seasonal patterns
- Year-over-year comparisons

✅ **Geographic Analysis**
- Country-wise bookings
- Regional patterns
- Geographic insights

✅ **Advanced Analytics**
- Customer segmentation
- Revenue analysis
- Custom visualizations
""")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 14px;'>
        <p>🏨 <strong>Hotel Booking Analytics Dashboard</strong> | Built with Streamlit & Plotly</p>
        <p>📊 Upload your CSV file to explore comprehensive hotel booking insights</p>
        <p>🔍 Supports interactive filtering, multiple visualization types, and data export</p>
    </div>
    """, 
    unsafe_allow_html=True
)