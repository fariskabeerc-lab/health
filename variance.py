import streamlit as st
import pandas as pd
import altair as alt
import io

# --- Load Data ---
# Load the pre-processed and combined data
try:
    # 🚨 CHANGE 1: Reading from Excel (.xlsx) instead of CSV
    # Make sure you have the 'openpyxl' or 'xlrd' library installed: pip install openpyxl
    df_data = pd.read_excel("shane.Xlsx")
except FileNotFoundError:
    # 🚨 CHANGE 2: Update the error message to reflect the new file name
    st.error("Error: 'combined_stock_data.xlsx' not found. Please ensure the Excel file is in the same directory as the script.")
    st.stop()

# --- Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("🛒 Al Madina Inventory & Sales Dashboard")

# ----------------------------------------------------
# 1. Sidebar Filters
# ----------------------------------------------------
st.sidebar.header("Filter Options")

# Outlet Filter with "All Outlets" option
outlet_list = sorted(df_data['Outlet'].unique())
outlet_options = ['All Outlets'] + outlet_list
selected_outlet = st.sidebar.selectbox(
    'Select Outlet:',
    outlet_options,
    index=0 # Default to 'All Outlets'
)

# Filter data based on the selected outlet
if selected_outlet == 'All Outlets':
    df_outlet_filtered = df_data.copy()
else:
    df_outlet_filtered = df_data[df_data['Outlet'] == selected_outlet].copy()

# Category Filter (Radio buttons for single selection, plus 'All Categories' option)
category_options = ['All Categories'] + sorted(df_outlet_filtered['Category'].unique())
selected_category = st.sidebar.radio(
    'Select Category:',
    category_options,
    index=0 # Default to 'All Categories'
)

# ----------------------------------------------------
# 2. Data Filtering and Aggregation
# ----------------------------------------------------

# Primary filter: filter by selected outlet and category
if selected_category == 'All Categories':
    df_final_filtered = df_outlet_filtered
else:
    df_final_filtered = df_outlet_filtered[df_outlet_filtered['Category'] == selected_category]


# Determine the data source for the main chart/table based on the selection
if selected_outlet == 'All Outlets' and selected_category != 'All Categories':
    # This is the new required case: Aggregate data by OUTLET for the selected CATEGORY
    df_chart_data = df_final_filtered.groupby('Outlet').sum(numeric_only=True).reset_index()
    y_axis_field = 'Outlet' # Chart will be Outlet-wise
elif selected_category == 'All Categories' and selected_outlet == 'All Outlets':
    # Aggregate data by CATEGORY for the overall view
    df_chart_data = df_final_filtered.groupby('Category').sum(numeric_only=True).reset_index()
    df_chart_data = df_chart_data.sort_values(by='Stock Value', ascending=False)
    y_axis_field = 'Category' # Chart will be Category-wise
else:
    # Single Outlet (All or Single Category selected)
    df_chart_data = df_final_filtered.sort_values(by='Stock Value', ascending=False)
    y_axis_field = 'Category' # Chart will be Category-wise

# ----------------------------------------------------
# 3. Dynamic Key Insights
# ----------------------------------------------------

# Calculate total metrics for the Key Insights from the df_final_filtered (the non-aggregated source data)
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
    st.metric("Total Stock Value (AED)", f"{current_stock_value:,.0f}")

with col2:
    st.metric("Total Sales (AED)", f"{current_total_sale:,.0f}")

with col3:
    st.metric("Total Monthly Sales (AED)", f"{current_monthly_sale:,.0f}")

with col4:
    # Use the reduce stock value and status
    delta_value = f"{current_reduce_stock:,.0f}"
    st.metric(f"Inventory Status (Reduce Stock)", delta_value, delta=status)

st.markdown("---")

# ----------------------------------------------------
# 4. Visualization and Table
# ----------------------------------------------------
if df_chart_data.empty:
    st.warning("No data to display for the current selection.")
else:
    st.subheader(f"{y_axis_field} Breakdown")

    # 4a. Single Item View (for a single Category in a single Outlet)
    if selected_category != 'All Categories' and selected_outlet != 'All Outlets':
        # Reuse logic for single item view: simpler table and stock vs max chart
        data_display = df_chart_data.iloc[0]
        st.table(data_display[['Category', 'Stock Value', 'Reduce Stock', 'Max Stock', 'Monthly Sale', 'Total Sale']].rename({
            'Stock Value': 'Current Stock Value', 
            'Reduce Stock': 'Max Stock - Current Stock',
            'Max Stock': 'Max Allowed Stock'
        }).to_frame().T.set_index('Category'))
        
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
            title=f"Stock Level Comparison for {selected_category} in {selected_outlet}"
        )
        st.altair_chart(stock_bar_chart, use_container_width=True)

    # 4b. Multiple Items/Full Chart View (Updated to be vertical)
    else:
        # Sort the visualization data by Stock Value
        df_chart_data = df_chart_data.sort_values(by='Stock Value', ascending=False)
        
        # Chart 1: Stock Value by Y-axis Field (Category or Outlet) - VERTICAL
        base = alt.Chart(df_chart_data).encode(
            x=alt.X(y_axis_field, sort='-y', title=y_axis_field, axis=alt.Axis(labelAngle=-45)), # Set X to category/outlet, add rotation for labels
            tooltip=[y_axis_field, alt.Tooltip('Stock Value', format=',.0f'), 'Max Stock']
        ).properties(
            title=f"Current Stock Value by {y_axis_field}"
        )

        chart_stock = base.mark_bar(color='#4c78a8').encode(
            y=alt.Y('Stock Value', title="Current Stock Value (AED)"), # Set Y to value field
        )

        # Chart 2: Reduce Stock by Y-axis Field - VERTICAL with INVERTED Y-AXIS (Filtered to only show <= 0)
        chart_reduce = alt.Chart(df_chart_data).transform_filter(
            alt.FieldRangePredicate(field="Reduce Stock", range=[None, 0]) # Filter: Keep only Reduce Stock <= 0 (Overstocked)
        ).encode(
            # Use the same sort order as the stock chart, applied to X axis
            x=alt.X(y_axis_field, sort=alt.EncodingSortField(field="Stock Value", op="sum", order='descending'), title=y_axis_field, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Reduce Stock', title="Overstock (Max - Current)", scale=alt.Scale(reverse=True)), 
            color=alt.Color('Reduce Stock', 
                            # Adjust color range/domain since only negative/zero values remain
                            scale=alt.Scale(domain=[df_chart_data['Reduce Stock'].min(), 0], range=['red', 'gray']),
                            legend=None),
            tooltip=[y_axis_field, alt.Tooltip('Reduce Stock', format=',.0f')]
        ).mark_bar().properties(
            title=f"Overstocked Items (Reduce Stock $\le 0$) by {y_axis_field}"
        )

        # Combine the charts vertically
        final_chart = alt.vconcat(
            chart_stock,
            chart_reduce
        ).resolve_scale(
            x='shared' # Share the X-axis (Category/Outlet) between the two charts
        ).configure_title(
            fontSize=16,
            anchor='start'
        )

        st.altair_chart(final_chart, use_container_width=True)

    # 5. Display the filtered data table (always show this)
    st.subheader("Filtered Data Table")
    # Determine the columns to show in the table
    table_cols = ['Outlet', 'Category', 'Stock Value', 'Reduce Stock', 'Total Sale', 'Max Stock', 'Monthly Sale']
    
    # Filter columns based on the selection to keep the table clean and relevant
    if selected_outlet != 'All Outlets':
        table_cols.remove('Outlet')
    if selected_category != 'All Categories':
        table_cols.remove('Category')
    
    # Show the non-aggregated data (df_final_filtered) in the table for detail
    st.dataframe(df_final_filtered[table_cols],
                 use_container_width=True)
