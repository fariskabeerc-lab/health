import streamlit as st
import pandas as pd
import altair as alt
import io

# --- Column Name Constants ---
# 🚨 Fix 1: Use the exact, case-sensitive column names from your Excel file 🚨
OUTLET_COL = 'outlet' 
CATEGORY_COL = 'CATEGORY'

# --- Load Data ---
EXCEL_FILE_NAME = "combined_stock_data.xlsx"

try:
    # Reading from Excel (.xlsx).
    df_data = pd.read_excel(EXCEL_FILE_NAME)
    
    # --- ⚠️ DEBUGGING STEP ⚠️ ---
    # Display columns in the sidebar for confirmation
    st.sidebar.markdown(f"**Loaded Columns:** {df_data.columns.tolist()}")

except FileNotFoundError:
    st.error(f"Error: '{EXCEL_FILE_NAME}' not found. Please ensure the Excel file is in the same directory as the script.")
    st.stop()
except KeyError as e:
    st.error(f"KeyError: A required column was not found. Please ensure column names are exactly '{OUTLET_COL}' and '{CATEGORY_COL}'. Found columns: {df_data.columns.tolist()}")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while loading the data: {e}")
    st.stop()


# --- Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("🛒 Al Madina Inventory & Sales Dashboard")

# ----------------------------------------------------
# 1. Sidebar Filters
# ----------------------------------------------------
st.sidebar.header("Filter Options")

# Outlet Filter with "All Outlets" option
# 🚨 Fix 2: Use OUTLET_COL
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
    # 🚨 Fix 3: Use OUTLET_COL
    df_outlet_filtered = df_data[df_data[OUTLET_COL] == selected_outlet].copy()

# Category Filter (Radio buttons for single selection, plus 'All Categories' option)
# 🚨 Fix 4: Use CATEGORY_COL
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
    # 🚨 Fix 5: Use CATEGORY_COL
    df_final_filtered = df_outlet_filtered[df_outlet_filtered[CATEGORY_COL] == selected_category]


# Determine the data source for the main chart/table based on the selection
if selected_outlet == 'All Outlets' and selected_category != 'All Categories':
    # Aggregate data by OUTLET for the selected CATEGORY
    # 🚨 Fix 6: Use OUTLET_COL
    df_chart_data = df_final_filtered.groupby(OUTLET_COL).sum(numeric_only=True).reset_index()
    y_axis_field = OUTLET_COL # Chart will be Outlet-wise
elif selected_category == 'All Categories' and selected_outlet == 'All Outlets':
    # Aggregate data by CATEGORY for the overall view
    # 🚨 Fix 7: Use CATEGORY_COL
    df_chart_data = df_final_filtered.groupby(CATEGORY_COL).sum(numeric_only=True).reset_index()
    df_chart_data = df_chart_data.sort_values(by='STOCK VALUE', ascending=False)
    y_axis_field = CATEGORY_COL # Chart will be Category-wise
else:
    # Single Outlet (All or Single Category selected)
    # 🚨 Fix 8: Use 'STOCK VALUE'
    df_chart_data = df_final_filtered.sort_values(by='STOCK VALUE', ascending=False)
    y_axis_field = CATEGORY_COL # Chart will be Category-wise

# ----------------------------------------------------
# 3. Dynamic Key Insights
# ----------------------------------------------------

# Calculate total metrics for the Key Insights from the df_final_filtered (the non-aggregated source data)
# 🚨 Fix 9-12: Use correct column names
current_stock_value = df_final_filtered['STOCK VALUE'].sum()
current_total_sale = df_final_filtered['TOTAL SALE'].sum()
current_monthly_sale = df_final_filtered['MONTHLY SALE'].sum()
current_reduce_stock = df_final_filtered['REDUCE STOCK'].sum()

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
        # 🚨 Fix 13: Use correct column names
        st.table(data_display[[CATEGORY_COL, 'STOCK VALUE', 'REDUCE STOCK', 'MAX STOCK', 'MONTHLY SALE', 'TOTAL SALE']].rename({
            'STOCK VALUE': 'Current Stock Value', 
            'REDUCE STOCK': 'Max Stock - Current Stock',
            'MAX STOCK': 'Max Allowed Stock'
        }).to_frame().T.set_index(CATEGORY_COL))
        
        st.subheader("Stock vs. Max Stock")
        stock_chart_data = pd.DataFrame({
            'Metric': ['Current Stock', 'Max Stock'],
            # 🚨 Fix 14: Use correct column names
            'Value': [data_display['STOCK VALUE'], data_display['MAX STOCK']]
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
        # 🚨 Fix 15: Use 'STOCK VALUE'
        df_chart_data = df_chart_data.sort_values(by='STOCK VALUE', ascending=False)
        
        # Chart 1: Stock Value by Y-axis Field (Category or Outlet) - VERTICAL
        base = alt.Chart(df_chart_data).encode(
            x=alt.X(y_axis_field, sort='-y', title=y_axis_field, axis=alt.Axis(labelAngle=-45)), # Set X to category/outlet, add rotation for labels
            # 🚨 Fix 16: Use correct column names
            tooltip=[y_axis_field, alt.Tooltip('STOCK VALUE', format=',.0f'), 'MAX STOCK']
        ).properties(
            title=f"Current Stock Value by {y_axis_field}"
        )

        chart_stock = base.mark_bar(color='#4c78a8').encode(
            # 🚨 Fix 17: Use 'STOCK VALUE'
            y=alt.Y('STOCK VALUE', title="Current Stock Value (AED)"), # Set Y to value field
        )

        # Chart 2: Reduce Stock by Y-axis Field - VERTICAL with INVERTED Y-AXIS (Filtered to only show <= 0)
        # 🚨 Fix 18: Use 'REDUCE STOCK'
        chart_reduce = alt.Chart(df_chart_data).transform_filter(
            alt.FieldRangePredicate(field="REDUCE STOCK", range=[None, 0]) # Filter: Keep only Reduce Stock <= 0 (Overstocked)
        ).encode(
            # Use the same sort order as the stock chart, applied to X axis
            # 🚨 Fix 19: Use 'STOCK VALUE'
            x=alt.X(y_axis_field, sort=alt.EncodingSortField(field="STOCK VALUE", op="sum", order='descending'), title=y_axis_field, axis=alt.Axis(labelAngle=-45)),
            # 🚨 Fix 20: Use 'REDUCE STOCK'
            y=alt.Y('REDUCE STOCK', title="Overstock (Max - Current)", scale=alt.Scale(reverse=True)), 
            # 🚨 Fix 21: Use 'REDUCE STOCK'
            color=alt.Color('REDUCE STOCK', 
                            # Adjust color range/domain since only negative/zero values remain
                            scale=alt.Scale(domain=[df_chart_data['REDUCE STOCK'].min(), 0], range=['red', 'gray']),
                            legend=None),
            # 🚨 Fix 22: Use 'REDUCE STOCK'
            tooltip=[y_axis_field, alt.Tooltip('REDUCE STOCK', format=',.0f')]
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
    # 🚨 Fix 23: Use correct column names
    table_cols = [OUTLET_COL, CATEGORY_COL, 'STOCK VALUE', 'REDUCE STOCK', 'TOTAL SALE', 'MAX STOCK', 'MONTHLY SALE']
    
    # Filter columns based on the selection to keep the table clean and relevant
    # 🚨 Fix 24-25: Use column name constants
    if selected_outlet != 'All Outlets':
        table_cols.remove(OUTLET_COL)
    if selected_category != 'All Categories':
        table_cols.remove(CATEGORY_COL)
    
    # Show the non-aggregated data (df_final_filtered) in the table for detail
    st.dataframe(df_final_filtered[table_cols],
                 use_container_width=True)
