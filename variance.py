import streamlit as st
import pandas as pd
import altair as alt
import io

# --- Column Name Constants ---
# Use the exact, case-sensitive column names provided by the user
OUTLET_COL = 'outlet' 
CATEGORY_COL = 'CATEGORY'
STOCK_VALUE_COL = 'STOCK VALUE'
TOTAL_SALE_COL = 'TOTAL SALE'
MONTHLY_SALE_COL = 'MONTHLY SALE'
MAX_STOCK_COL = 'MAX STOCK'
REDUCE_STOCK_COL = 'REDUCE STOCK'

# --- Load Data ---
# Reverting to original file name and type, but with corrected column handling
try:
    # Ensure this file exists from the previous steps
    df_data = pd.read_csv("combined_stock_data.csv")
except FileNotFoundError:
    st.error("Error: 'combined_stock_data.csv' not found. Please ensure the file is in the same directory as the script.")
    st.stop()
# Note: In a real scenario, you'd check for the existence of the expected columns here.

# --- Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("🛒 Al Madina Inventory & Sales Dashboard")

# ----------------------------------------------------
# 1. Sidebar Filters
# ----------------------------------------------------
st.sidebar.header("Filter Options")

# Outlet Filter with "All Outlets" option
# 🚨 Use OUTLET_COL
outlet_list = sorted(df_data[OUTLET_COL].unique())
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
    # 🚨 Use OUTLET_COL
    df_outlet_filtered = df_data[df_data[OUTLET_COL] == selected_outlet].copy()

# Category Filter (Radio buttons for single selection, plus 'All Categories' option)
# 🚨 Use CATEGORY_COL
category_options = ['All Categories'] + sorted(df_outlet_filtered[CATEGORY_COL].unique())
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
    # 🚨 Use CATEGORY_COL
    df_final_filtered = df_outlet_filtered[df_outlet_filtered[CATEGORY_COL] == selected_category]


# Determine the data source for the main chart/table based on the selection
if selected_outlet == 'All Outlets' and selected_category != 'All Categories':
    # Aggregate data by OUTLET for the selected CATEGORY
    # 🚨 Use OUTLET_COL
    df_chart_data = df_final_filtered.groupby(OUTLET_COL).sum(numeric_only=True).reset_index()
    y_axis_field = OUTLET_COL # Chart will be Outlet-wise
elif selected_category == 'All Categories' and selected_outlet == 'All Outlets':
    # Aggregate data by CATEGORY for the overall view
    # 🚨 Use CATEGORY_COL and STOCK_VALUE_COL
    df_chart_data = df_final_filtered.groupby(CATEGORY_COL).sum(numeric_only=True).reset_index()
    df_chart_data = df_chart_data.sort_values(by=STOCK_VALUE_COL, ascending=False)
    y_axis_field = CATEGORY_COL # Chart will be Category-wise
else:
    # Single Outlet (All or Single Category selected)
    # 🚨 Use STOCK_VALUE_COL
    df_chart_data = df_final_filtered.sort_values(by=STOCK_VALUE_COL, ascending=False)
    y_axis_field = CATEGORY_COL # Chart will be Category-wise

# ----------------------------------------------------
# 3. Dynamic Key Insights
# ----------------------------------------------------

# Calculate total metrics for the Key Insights from the df_final_filtered (the non-aggregated source data)
# 🚨 Use correct column constants
current_stock_value = df_final_filtered[STOCK_VALUE_COL].sum()
current_total_sale = df_final_filtered[TOTAL_SALE_COL].sum()
current_monthly_sale = df_final_filtered[MONTHLY_SALE_COL].sum()
current_reduce_stock = df_final_filtered[REDUCE_STOCK_COL].sum()

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
        # 🚨 Use correct column constants/names for table
        st.table(data_display[[CATEGORY_COL, STOCK_VALUE_COL, REDUCE_STOCK_COL, MAX_STOCK_COL, MONTHLY_SALE_COL, TOTAL_SALE_COL]].rename({
            STOCK_VALUE_COL: 'Current Stock Value', 
            REDUCE_STOCK_COL: 'Max Stock - Current Stock',
            MAX_STOCK_COL: 'Max Allowed Stock'
        }).to_frame().T.set_index(CATEGORY_COL))
        
        st.subheader("Stock vs. Max Stock")
        stock_chart_data = pd.DataFrame({
            'Metric': ['Current Stock', 'Max Stock'],
            # 🚨 Use correct column constants
            'Value': [data_display[STOCK_VALUE_COL], data_display[MAX_STOCK_COL]]
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
        # df_chart_data is already sorted by STOCK_VALUE_COL
        
        # Chart 1: Stock Value by Y-axis Field (Category or Outlet) - VERTICAL
        base = alt.Chart(df_chart_data).encode(
            # 🚨 Use STOCK_VALUE_COL for sorting
            x=alt.X(y_axis_field, sort=alt.SortField(field=STOCK_VALUE_COL, op='sum', order='descending'), title=y_axis_field, axis=alt.Axis(labelAngle=-45)), 
            # 🚨 Use correct column constants
            tooltip=[y_axis_field, alt.Tooltip(STOCK_VALUE_COL, format=',.0f'), MAX_STOCK_COL]
        ).properties(
            title=f"Current Stock Value by {y_axis_field}"
        )

        chart_stock = base.mark_bar(color='#4c78a8').encode(
            # 🚨 Use STOCK_VALUE_COL
            y=alt.Y(STOCK_VALUE_COL, title="Current Stock Value (AED)"), # Set Y to value field
        )
        
        # Chart 2: Reduce Stock by Y-axis Field - VERTICAL with INVERTED Y-AXIS (Filtered to only show <= 0)
        # Get the sorted list of categories/outlets for explicit sort (fixes ValueError)
        sort_order = df_chart_data[y_axis_field].tolist()
        
        chart_reduce = alt.Chart(df_chart_data).transform_filter(
            # 🚨 Use REDUCE_STOCK_COL
            alt.FieldRangePredicate(field=REDUCE_STOCK_COL, range=[None, 0]) # Filter: Keep only Reduce Stock <= 0 (Overstocked)
        ).encode(
            # Use the explicit sort order
            x=alt.X(y_axis_field, sort=sort_order, title=y_axis_field, axis=alt.Axis(labelAngle=-45)),
            # 🚨 Use REDUCE_STOCK_COL
            y=alt.Y(REDUCE_STOCK_COL, title="Overstock (Max - Current)", scale=alt.Scale(reverse=True)), 
            color=alt.Color(REDUCE_STOCK_COL, 
                            # Adjust color range/domain since only negative/zero values remain
                            scale=alt.Scale(domain=[df_chart_data[REDUCE_STOCK_COL].min(), 0], range=['red', 'gray']),
                            legend=None),
            tooltip=[y_axis_field, alt.Tooltip(REDUCE_STOCK_COL, format=',.0f')]
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
    # 🚨 Use correct column constants
    table_cols = [OUTLET_COL, CATEGORY_COL, STOCK_VALUE_COL, REDUCE_STOCK_COL, TOTAL_SALE_COL, MAX_STOCK_COL, MONTHLY_SALE_COL]
    
    # Filter columns based on the selection to keep the table clean and relevant
    # 🚨 Use column constants
    if selected_outlet != 'All Outlets':
        table_cols.remove(OUTLET_COL)
    if selected_category != 'All Categories':
        table_cols.remove(CATEGORY_COL)
    
    # Show the non-aggregated data (df_final_filtered) in the table for detail
    st.dataframe(df_final_filtered[table_cols],
                 use_container_width=True)
