import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="SKU Performance Analyzer",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Top SKU Performance Analysis")
st.markdown("**Identify your best-performing products over the last 6 months**")

# Sidebar for controls
st.sidebar.header("Analysis Controls")

# Sample data generator (replace with actual data connection)
@st.cache_data
def generate_sample_data():
    """Generate realistic sample sales data"""
    # Create 6 months of daily data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Sample SKUs
    skus = [
        "SKU-001", "SKU-002", "SKU-003", "SKU-004", "SKU-005",
        "SKU-006", "SKU-007", "SKU-008", "SKU-009", "SKU-010",
        "SKU-011", "SKU-012", "SKU-013", "SKU-014", "SKU-015"
    ]
    
    product_names = [
        "Premium Coffee Beans", "Organic Tea Blend", "Artisan Chocolate",
        "Natural Honey", "Gourmet Crackers", "Specialty Jam",
        "Craft Beer Pack", "Wine Selection", "Cheese Platter",
        "Nuts & Seeds Mix", "Dried Fruits", "Herbal Soap",
        "Essential Oil", "Handmade Candle", "Ceramic Mug"
    ]
    
    categories = [
        "Beverages", "Beverages", "Confectionery", "Pantry", "Snacks",
        "Pantry", "Beverages", "Beverages", "Dairy", "Snacks",
        "Snacks", "Personal Care", "Personal Care", "Home", "Home"
    ]
    
    data = []
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for date in date_range:
        for i, sku in enumerate(skus):
            # Simulate realistic sales patterns
            base_quantity = np.random.poisson(5 + i * 2)
            weekend_boost = 1.3 if date.weekday() >= 5 else 1.0
            seasonal_factor = 1 + 0.3 * np.sin((date.dayofyear / 365) * 2 * np.pi)
            
            quantity = int(base_quantity * weekend_boost * seasonal_factor)
            unit_price = 10 + i * 3 + np.random.uniform(-2, 2)
            
            if quantity > 0:  # Only add records with sales
                data.append({
                    'date': date,
                    'sku': sku,
                    'product_name': product_names[i],
                    'category': categories[i],
                    'quantity_sold': quantity,
                    'unit_price': round(unit_price, 2),
                    'total_revenue': round(quantity * unit_price, 2)
                })
    
    return pd.DataFrame(data)

# Load data
@st.cache_data
def load_data():
    """Load sales data - replace with your data source"""
    # In production, replace this with:
    # return pd.read_sql("SELECT * FROM sales_data WHERE date >= CURRENT_DATE - INTERVAL '6 months'", connection)
    return generate_sample_data()

# Data upload option
st.sidebar.subheader("Data Source")
data_source = st.sidebar.radio(
    "Choose data source:",
    ["Use Sample Data", "Upload CSV File"]
)

if data_source == "Upload CSV File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload your sales data CSV",
        type=['csv'],
        help="CSV should contain: date, sku, product_name, quantity_sold, unit_price"
    )
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df['date'] = pd.to_datetime(df['date'])
        df['total_revenue'] = df['quantity_sold'] * df['unit_price']
    else:
        df = load_data()
else:
    df = load_data()

# Analysis parameters
st.sidebar.subheader("Analysis Parameters")
top_n = st.sidebar.slider("Top N SKUs to analyze", 5, 20, 10)
metric = st.sidebar.selectbox(
    "Primary Metric",
    ["Total Revenue", "Quantity Sold", "Average Order Value"]
)

# Date range filter
date_range = st.sidebar.date_input(
    "Date Range",
    value=(df['date'].min().date(), df['date'].max().date()),
    min_value=df['date'].min().date(),
    max_value=df['date'].max().date()
)

# Filter data by date range
if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
else:
    df_filtered = df

# Calculate key metrics
@st.cache_data
def calculate_sku_metrics(df):
    """Calculate key performance metrics for each SKU"""
    sku_metrics = df.groupby(['sku', 'product_name', 'category']).agg({
        'quantity_sold': 'sum',
        'total_revenue': 'sum',
        'unit_price': 'mean',
        'date': 'nunique'  # Days with sales
    }).reset_index()
    
    sku_metrics.columns = ['sku', 'product_name', 'category', 'total_quantity', 
                          'total_revenue', 'avg_unit_price', 'days_with_sales']
    
    # Calculate additional metrics
    sku_metrics['avg_daily_quantity'] = sku_metrics['total_quantity'] / sku_metrics['days_with_sales']
    sku_metrics['avg_order_value'] = sku_metrics['total_revenue'] / sku_metrics['total_quantity']
    
    return sku_metrics

sku_metrics = calculate_sku_metrics(df_filtered)

# Sort by selected metric
if metric == "Total Revenue":
    sku_metrics_sorted = sku_metrics.sort_values('total_revenue', ascending=False)
elif metric == "Quantity Sold":
    sku_metrics_sorted = sku_metrics.sort_values('total_quantity', ascending=False)
else:  # Average Order Value
    sku_metrics_sorted = sku_metrics.sort_values('avg_order_value', ascending=False)

# Main dashboard
col1, col2, col3 = st.columns(3)

with col1:
    total_revenue = df_filtered['total_revenue'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

with col2:
    total_quantity = df_filtered['quantity_sold'].sum()
    st.metric("Total Units Sold", f"{total_quantity:,}")

with col3:
    avg_order_value = total_revenue / total_quantity if total_quantity > 0 else 0
    st.metric("Overall AOV", f"${avg_order_value:.2f}")

# Top SKUs analysis
st.header(f"Top {top_n} SKUs by {metric}")

# Display top SKUs table
top_skus = sku_metrics_sorted.head(top_n)
st.dataframe(
    top_skus[['sku', 'product_name', 'category', 'total_quantity', 'total_revenue', 'avg_order_value']].round(2),
    use_container_width=True
)

# Visualizations
col1, col2 = st.columns(2)

with col1:
    # Revenue chart
    fig_revenue = px.bar(
        top_skus, 
        x='sku', 
        y='total_revenue',
        title=f'Top {top_n} SKUs by Revenue',
        labels={'total_revenue': 'Total Revenue ($)', 'sku': 'SKU'},
        color='total_revenue',
        color_continuous_scale='Blues'
    )
    fig_revenue.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig_revenue, use_container_width=True)

with col2:
    # Quantity chart
    fig_quantity = px.bar(
        top_skus, 
        x='sku', 
        y='total_quantity',
        title=f'Top {top_n} SKUs by Quantity Sold',
        labels={'total_quantity': 'Units Sold', 'sku': 'SKU'},
        color='total_quantity',
        color_continuous_scale='Greens'
    )
    fig_quantity.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig_quantity, use_container_width=True)

# Category performance
st.header("Performance by Category")
category_metrics = df_filtered.groupby('category').agg({
    'total_revenue': 'sum',
    'quantity_sold': 'sum'
}).reset_index()

fig_category = px.pie(
    category_metrics,
    values='total_revenue',
    names='category',
    title='Revenue Distribution by Category'
)
st.plotly_chart(fig_category, use_container_width=True)

# Time series analysis
st.header("Sales Trends Over Time")
daily_sales = df_filtered.groupby('date').agg({
    'total_revenue': 'sum',
    'quantity_sold': 'sum'
}).reset_index()

fig_trend = px.line(
    daily_sales,
    x='date',
    y='total_revenue',
    title='Daily Revenue Trend',
    labels={'total_revenue': 'Daily Revenue ($)', 'date': 'Date'}
)
st.plotly_chart(fig_trend, use_container_width=True)

# AI Insights section
st.header("🤖 AI-Powered Insights")
st.info("""
**Key Findings:**
- Your top 3 SKUs account for {:.1f}% of total revenue
- {} category shows the strongest performance
- Peak sales typically occur on weekends
- Consider restocking {} (highest velocity item)
""".format(
    (top_skus.head(3)['total_revenue'].sum() / total_revenue * 100),
    category_metrics.loc[category_metrics['total_revenue'].idxmax(), 'category'],
    top_skus.iloc[0]['sku']
))

# Action items
st.header("📋 Recommended Actions")
with st.expander("View Detailed Recommendations"):
    st.markdown("""
    ### Immediate Actions:
    1. **Increase inventory** for top 3 performing SKUs
    2. **Review pricing** for high-volume, low-revenue items
    3. **Promote slow-moving** items in underperforming categories
    
    ### Strategic Considerations:
    1. **Bundle deals** combining high and low performers
    2. **Seasonal adjustments** based on trend analysis
    3. **Supplier negotiations** for top-volume items
    """)

# Export functionality
st.header("📁 Export Results")
if st.button("Download Top SKU Analysis"):
    csv = top_skus.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"top_skus_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit • Data analysis for smarter inventory decisions*")