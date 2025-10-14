import streamlit as st
import pandas as pd
import altair as alt
import io

# --- Load Data ---
# Load the pre-processed and combined data
try:
    # Ensure this file exists from the previous steps
    df_data = pd.read_csv("combined_stock_data.csv")
except FileNotFoundError:
    st.error("Error: 'combined_stock_data.csv' not found. Please ensure the file is in the same directory as the script.")
    st.stop()

# --- Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("🛒 Supermarket Inventory Analysis Dashboard")

# ----------------------------------------------------
# 1. Sidebar Filters
# ----------------------------------------------------
st.sidebar.header("Filter Options")

# Outlet Filter
outlet_options = sorted(df_data['Outlet'].unique())
selected_outlet = st.sidebar.selectbox(
    'Select Outlet:',
    outlet_options,
    index=0
)

# Filter data based on the selected outlet
df_outlet_filtered = df_data[df_data['Outlet'] == selected_outlet].copy()

# Category Filter (Radio buttons for single selection, plus 'All Categories' option)
category_options = ['All Categories'] + sorted(df_outlet_filtered['Category'].unique())
selected_category = st.sidebar.radio(
    'Select Category:',
    category_options,
    index=0 # Default to 'All Categories'
)

# ----------------------------------------------------
# 2. Data Filtering based on Selections
# ----------------------------------------------------
if selected_category == 'All Categories':
    df_final_filtered = df_outlet_filtered
else:
    df_final_filtered = df_outlet_filtered[df_outlet_filtered['Category'] == selected_category]

# Sort by Stock Value for better visualization if not filtering a single category
if selected_category == 'All Categories':
    df_final_filtered = df_final_filtered.sort_values(by='Stock Value', ascending=False)


# ----------------------------------------------------
# 3. Dynamic Key Insights
# ----------------------------------------------------
# Calculate dynamic key metrics for the current selection
current_stock_value = df_final_filtered['Stock Value'].sum()
current_total_sale = df_final_filtered['Total Sale'].sum()
current_monthly_sale = df_final_filtered['Monthly Sale'].sum()
current_reduce_stock = df_final_filtered['Reduce Stock'].sum()

# Determine Overstocked/Understocked status for the status message
status = "Balanced"
if current_reduce_stock < 0:
    status = "Overstocked"
elif current_reduce_stock > 0:
    status = "Understocked (Room for Stock)"

st.header(f"Key Insights for: {selected_outlet} - {selected_category}")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current Stock Value (AED)", f"{current_stock_value:,.0f}")

with col2:
    st.metric("Total Sales (AED)", f"{current_total_sale:,.0f}")

with col3:
    st.metric("Monthly Sales (AED)", f"{current_monthly_sale:,.0f}")

with col4:
    # Use the reduce stock value and status
    delta_value = f"{current_reduce_stock:,.0f}"
    st.metric(f"Inventory Status (Reduce Stock)", delta_value, delta=status)

st.markdown("---")

# ----------------------------------------------------
# 4. Visualization and Table
# ----------------------------------------------------
if df_final_filtered.empty:
    st.warning("No data to display for the current selection.")
else:
    # If a single category is selected, use a simplified view/table
    if selected_category != 'All Categories':
        st.subheader(f"Detailed Metrics for {selected_category}")
        
        # Display key figures in a simple table for the single category view
        data_display = df_final_filtered[['Category', 'Stock Value', 'Reduce Stock', 'Max Stock', 'Monthly Sale', 'Total Sale']].iloc[0]
        
        st.table(data_display.rename({
            'Stock Value': 'Current Stock Value', 
            'Reduce Stock': 'Max Stock - Current Stock',
            'Max Stock': 'Max Allowed Stock'
        }).to_frame().T.set_index('Category'))
        
        # Single category visualization (Gauge or simple bar)
        st.subheader("Stock vs. Max Stock")
        
        stock_chart_data = pd.DataFrame({
            'Metric': ['Current Stock', 'Max Stock'],
            'Value': [data_display['Stock Value'], data_display['Max Stock']]
        })
        
        stock_bar_chart = alt.Chart(stock_chart_data).mark_bar().encode(
            x=alt.X('Value', title="Value (AED)"),
            y=alt.Y('Metric', sort=None, title=""),
            color=alt.Color('Metric', scale=alt.Scale(range=['#4c78a8', '#e4575c']))
        ).properties(
            title=f"Stock Level Comparison for {selected_category}"
        )
        st.altair_chart(stock_bar_chart, use_container_width=True)
        
    # If 'All Categories' is selected, show the full bar charts
    else:
        st.subheader("Category Breakdown")
        
        # Chart 1: Stock Value by Category
        base = alt.Chart(df_final_filtered).encode(
            y=alt.Y('Category', sort='-x', title="Category"),
            tooltip=['Category', alt.Tooltip('Stock Value', format=',.0f'), 'Max Stock']
        ).properties(
            title=f"Current Stock Value by Category"
        )

        chart_stock = base.mark_bar(color='#4c78a8').encode(
            x=alt.X('Stock Value', title="Current Stock Value (AED)"),
        )

        # Chart 2: Reduce Stock by Category
        chart_reduce = alt.Chart(df_final_filtered).encode(
            # Use the same sort order as the stock chart
            y=alt.Y('Category', sort=alt.EncodingSortField(field="Stock Value", op="sum", order='descending')),
            x=alt.X('Reduce Stock', title="Reduce Stock (Max Stock - Current Stock)"),
            color=alt.Color('Reduce Stock', 
                            # Red for negative (overstocked), Green for positive (understocked)
                            scale=alt.Scale(domain=[df_final_filtered['Reduce Stock'].min(), 0, df_final_filtered['Reduce Stock'].max()], range=['red', 'gray', 'green']),
                            legend=None),
            tooltip=['Category', alt.Tooltip('Reduce Stock', format=',.0f')]
        ).mark_bar().properties(
            title=f"Inventory Discrepancy (Reduce Stock)"
        )

        # Combine the charts vertically
        final_chart = alt.vconcat(
            chart_stock,
            chart_reduce
        ).resolve_scale(
            y='shared'
        ).configure_title(
            fontSize=16,
            anchor='start'
        )

        # Display the chart
        st.altair_chart(final_chart, use_container_width=True)

    # Display the filtered data table (always show this)
    st.subheader("Filtered Data Table")
    st.dataframe(df_final_filtered[['Category', 'Stock Value', 'Reduce Stock', 'Total Sale', 'Max Stock', 'Monthly Sale']],
                 use_container_width=True)
