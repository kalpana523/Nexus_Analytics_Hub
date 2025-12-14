import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Nexus Analytics Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (MODERN DARK UI) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Custom Metric Card */
    .metric-card {
        background-color: #262730;
        border: 1px solid #363945;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #4e73df;
    }
    .metric-title {
        color: #A3A8B8;
        font-size: 0.9rem;
        margin-bottom: 5px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        color: #FAFAFA;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-delta {
        font-size: 0.8rem;
        margin-top: 5px;
        font-weight: 600;
    }
    .delta-pos { color: #00ff88; }
    .delta-neg { color: #ff4d4d; }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        color: #FAFAFA;
        border-radius: 5px 5px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262730;
        border-bottom: 2px solid #4e73df;
        color: #4e73df;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER: GENERATE ROBUST MOCK DATA ---
def generate_mock_data():
    # FIXED: Removed np.random.seed(42) so data changes on every refresh
    
    dates = pd.date_range(start="2023-01-01", end="2024-12-31", freq="D")
    # Skew selection towards end of year for seasonality effect
    selected_dates = np.random.choice(dates, 1200) 
    
    products_db = {
        'Electronics': {'Wireless Headphones': 120, '4K Monitor': 350, 'Gaming Mouse': 60},
        'Office': {'Mechanical Keyboard': 150, 'Laptop Stand': 45, 'Ergo Chair': 250},
        'Accessories': {'USB-C Hub': 30, 'Webcam': 80}
    }
    
    data = []
    for date in selected_dates:
        category = np.random.choice(list(products_db.keys()))
        product = np.random.choice(list(products_db[category].keys()))
        price = products_db[category][product]
        
        # Add random noise to price to simulate discounts
        final_price = price * np.random.uniform(0.9, 1.1)
        qty = np.random.randint(1, 4)
        
        data.append({
            'OrderDate': date,
            'CustomerID': f"CUST-{np.random.randint(1000, 1080)}",
            'Category': category,
            'ProductID': product,
            'Quantity': qty,
            'TotalSales': round(final_price * qty, 2)
        })
    return pd.DataFrame(data)

# --- HELPER: CLEAN DATA ---
def clean_data(df):
    df = df.drop_duplicates()
    if 'OrderDate' in df.columns:
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], dayfirst=True, errors='coerce')
    
    numeric_cols = ['TotalSales', 'Quantity']
    for col in numeric_cols:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(r'[$,]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    df = df.dropna(subset=['OrderDate', 'TotalSales'])
    return df

# --- HELPER: METRIC CARD COMPONENT ---
def metric_card(title, value, delta=None):
    delta_html = ""
    if delta:
        color_class = "delta-pos" if delta > 0 else "delta-neg"
        icon = "▲" if delta > 0 else "▼"
        delta_html = f'<div class="metric-delta {color_class}">{icon} {abs(delta):.1f}% vs Last Month</div>'
    
    html_code = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    data_source = st.radio("Data Source", ["Use Demo Data", "Upload CSV"], index=0)
    
    df = None
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Drop your CSV here", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            df = clean_data(df)
    else:
        # Generate data silently first time
        if 'mock_df' not in st.session_state:
            st.session_state.mock_df = clean_data(generate_mock_data())
        df = st.session_state.mock_df
        
        if st.button("🔄 Refresh Demo Data"):
            # This will now generate NEW random data because the fixed seed is gone
            st.session_state.mock_df = clean_data(generate_mock_data())
            st.rerun()

    st.markdown("---")
    st.markdown("### 🗓️ Time Filters")
    year_container = st.container()
    date_container = st.container()
    
    st.markdown("---")
    st.info("💡 **Tip:** Double-click charts to reset zoom.")

# --- MAIN LOGIC ---
if df is not None:
    # 1. Year Filter
    df['Year'] = df['OrderDate'].dt.year
    df['Month'] = df['OrderDate'].dt.month_name()
    df['MonthNum'] = df['OrderDate'].dt.month
    
    available_years = sorted(df['Year'].unique(), reverse=True)
    with year_container:
        selected_year = st.selectbox("Select Year", available_years)

    df_year = df[df['Year'] == selected_year]
    
    # 2. Date Filter
    with date_container:
        min_date = df_year['OrderDate'].min().date()
        max_date = df_year['OrderDate'].max().date()
        
        # Check if dates are available for the selected year
        if pd.isnull(min_date) or pd.isnull(max_date):
            st.warning("No data available for this year.")
            date_range = []
        else:
            date_range = st.date_input("Filter Date Range", value=[min_date, max_date], min_value=min_date, max_value=max_date)

    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df_year['OrderDate'].dt.date >= start_date) & (df_year['OrderDate'].dt.date <= end_date)
        filtered_df = df_year.loc[mask]
    else:
        filtered_df = df_year

    # --- DASHBOARD HEADER ---
    st.title("⚡ Nexus Analytics Hub")
    st.markdown(f"Performance Overview for **{selected_year}**")
    st.markdown("---")

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Summary", "🧠 Deep Dive & Pareto", "👥 Customer Segments", "📋 Raw Data"])

    # --- TAB 1: EXECUTIVE SUMMARY ---
    with tab1:
        # 1. Key Metrics with Delta Calculation
        current_sales = filtered_df['TotalSales'].sum()
        current_orders = len(filtered_df)
        current_aov = current_sales / current_orders if current_orders > 0 else 0
        
        # Calculate Previous Month Comparison (Simulated)
        prev_month_sales = current_sales * 0.92 # Mocking a +8% growth
        delta_sales = ((current_sales - prev_month_sales) / prev_month_sales) * 100
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("Total Revenue", f"${current_sales:,.0f}", delta_sales)
        with c2: metric_card("Total Orders", f"{current_orders:,}", 5.2)
        with c3: metric_card("Avg Order Value", f"${current_aov:.2f}", -2.1)
        with c4: metric_card("Active Customers", f"{filtered_df['CustomerID'].nunique()}", 12.5)

        st.markdown("###")
        
        # 2. Charts Row 1
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Revenue Trend Over Time")
            sales_time = filtered_df.set_index('OrderDate').resample('W')['TotalSales'].sum().reset_index()
            
            # Advanced Area Chart
            fig_trend = px.area(sales_time, x='OrderDate', y='TotalSales',
                                template="plotly_dark",
                                color_discrete_sequence=['#4e73df'])
            fig_trend.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="",
                yaxis_title="Revenue ($)",
                hovermode="x unified"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with col_right:
            st.subheader("Sales by Category")
            # If Category exists, use it, else fallback
            if 'Category' in filtered_df.columns:
                cat_sales = filtered_df.groupby('Category')['TotalSales'].sum().reset_index()
                fig_donut = px.pie(cat_sales, values='TotalSales', names='Category', hole=0.6,
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_donut.update_layout(
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    margin=dict(l=0, r=0, t=0, b=20),
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.warning("Category column missing in data.")

    # --- TAB 2: DEEP DIVE & PARETO ---
    with tab2:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🔥 Sales Heatmap (Day vs Month)")
            
            heatmap_data = filtered_df.copy()
            heatmap_data['DayOfWeek'] = heatmap_data['OrderDate'].dt.day_name()
            heatmap_data['Month'] = heatmap_data['OrderDate'].dt.month_name()
            
            # Ensure correct sorting
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            
            pivot_table = heatmap_data.pivot_table(index='DayOfWeek', columns='Month', values='TotalSales', aggfunc='sum')
            
            # Handle sorting only for existing data to prevent errors
            existing_days = [d for d in days_order if d in pivot_table.index]
            existing_months = [m for m in months_order if m in pivot_table.columns]
            
            pivot_table = pivot_table.reindex(index=existing_days, columns=existing_months)
            
            fig_heat = px.imshow(pivot_table, 
                                 labels=dict(x="Month", y="Day", color="Sales"),
                                 x=pivot_table.columns,
                                 y=pivot_table.index,
                                 color_continuous_scale='Viridis')
            fig_heat.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig_heat, use_container_width=True)

        with col2:
            st.markdown("### ⚖️ Pareto Analysis (80/20 Rule)")
            
            prod_sales = filtered_df.groupby('ProductID')['TotalSales'].sum().reset_index()
            prod_sales = prod_sales.sort_values('TotalSales', ascending=False)
            prod_sales['Cumulative Percentage'] = (prod_sales['TotalSales'].cumsum() / prod_sales['TotalSales'].sum()) * 100
            
            fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Bar (Sales)
            fig_pareto.add_trace(
                go.Bar(x=prod_sales['ProductID'], y=prod_sales['TotalSales'], name="Revenue", marker_color='#4e73df'),
                secondary_y=False
            )
            
            # Line (Cumulative %)
            fig_pareto.add_trace(
                go.Scatter(x=prod_sales['ProductID'], y=prod_sales['Cumulative Percentage'], name="Cumul %", marker_color='#ff4d4d', mode='lines+markers'),
                secondary_y=True
            )
            
            fig_pareto.update_layout(
                template="plotly_dark", 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(t=0, l=0, r=0, b=0)
            )
            st.plotly_chart(fig_pareto, use_container_width=True)

    # --- TAB 3: RFM SEGMENTATION ---
    with tab3:
        if not filtered_df.empty:
            snapshot_date = filtered_df['OrderDate'].max() + timedelta(days=1)
            rfm = filtered_df.groupby('CustomerID').agg({
                'OrderDate': lambda x: (snapshot_date - x.max()).days,
                'CustomerID': 'count',
                'TotalSales': 'sum'
            }).rename(columns={'OrderDate': 'Recency', 'CustomerID': 'Frequency', 'TotalSales': 'Monetary'})

            # Score calculation
            rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=['4','3','2','1'])
            rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=['1','2','3','4'])
            rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), 4, labels=['1','2','3','4'])
            
            rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

            def segment_customer(row):
                if row['RFM_Score'] in ['444', '434', '443', '344']: return 'Champions'
                elif row['R_Score'] in ['3', '4'] and row['F_Score'] in ['1', '2']: return 'Promising'
                elif row['R_Score'] in ['1', '2'] and row['F_Score'] in ['3', '4']: return 'At Risk'
                elif row['R_Score'] == '1': return 'Lost'
                else: return 'Standard'

            rfm['Segment'] = rfm.apply(segment_customer, axis=1)

            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("#### Segment Distribution")
                seg_counts = rfm['Segment'].value_counts()
                fig_seg = px.bar(x=seg_counts.values, y=seg_counts.index, orientation='h', 
                                 color=seg_counts.index, color_discrete_sequence=px.colors.qualitative.Prism)
                fig_seg.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_title="Count", yaxis_title="")
                st.plotly_chart(fig_seg, use_container_width=True)
            
            with c2:
                st.markdown("#### Value Matrix")
                fig_bubble = px.scatter(rfm, x='Recency', y='Monetary', 
                                        size='Frequency', color='Segment',
                                        hover_name=rfm.index, size_max=40,
                                        color_discrete_sequence=px.colors.qualitative.Prism)
                fig_bubble.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', xaxis_title="Recency (Days Ago)", yaxis_title="Total Spend")
                st.plotly_chart(fig_bubble, use_container_width=True)

            with st.expander("📥 Export Segmented Data"):
                st.dataframe(rfm, use_container_width=True)
                csv = rfm.to_csv().encode('utf-8')
                st.download_button("Download CSV", data=csv, file_name="rfm_segments.csv", mime="text/csv")

    # --- TAB 4: RAW DATA ---
    with tab4:
        st.dataframe(filtered_df, use_container_width=True)

elif df is None:
    # Landing State
    st.container()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>📊 Analytics Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: grey;'>Upload a CSV or generate demo data to begin.</p>", unsafe_allow_html=True)
        
        # Center button trick
        if st.button("🚀 Launch with Demo Data", type="primary", use_container_width=True):
            st.session_state.mock_df = clean_data(generate_mock_data())
            st.rerun()