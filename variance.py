import streamlit as st
import pandas as pd
import altair as alt
import io
import numpy as np # Import numpy for NaN handling

# --- Column Name Constants ---
OUTLET_COL = 'outlet' 
CATEGORY_COL = 'CATEGORY'
STOCK_VALUE_COL = 'STOCK VALUE'
TOTAL_SALE_COL = 'TOTAL SALE'
MONTHLY_SALE_COL = 'MONTHLY SALE'
MAX_STOCK_COL = 'MAX STOCK'
REDUCE_STOCK_COL = 'REDUCE STOCK'

# --- Load Data ---
try:
    df_data = pd.read_csv("sss.csv")
    
    # 🚨 CRITICAL FIX: Convert key columns to numeric. 
    # 'errors="coerce"' turns any non-numeric values (like text, symbols, 
    # or errors from badly formatted numbers) into NaN.
    numeric_cols = [STOCK_VALUE_COL, TOTAL_SALE_COL, MONTHLY_SALE_COL, MAX_STOCK_COL, REDUCE_STOCK_COL]
    
    for col in numeric_cols:
        # First, strip common non-numeric characters if any were missed by the original script
        if df_data[col].dtype == 'object':
             df_data[col] = df_data[col].astype(str).str.replace(r'[$,]', '', regex=True)
             
        df_data[col] = pd.to_numeric(df_data[col], errors='coerce')
        
    # Optional: Fill NaN values with 0 after coercion to prevent aggregation errors later.
    df_data[numeric_cols] = df_data[numeric_cols].fillna(0)


except FileNotFoundError:
    st.error("Error: 'combined_stock_data.csv' not found. Please ensure the file is in the same directory as the script.")
    st.stop()
except KeyError as e:
    # This block should handle the case-sensitivity issue if it somehow reappears.
    st.error(f"KeyError: Required column {e} not found. Please ensure all column constants match the CSV headers exactly (case-sensitive).")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while loading or processing the data: {e}")
    st.stop()


# --- Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("🛒 Al Madina Inventory & Sales Dashboard")

# ----------------------------------------------------
# 1. Sidebar Filters
# ----------------------------------------------------
st.sidebar.header("Filter Options")

# Outlet Filter with "All Outlets" option
outlet_list = sorted(df_data[OUTLET_COL].unique())
outlet_options = ['All Outlets'] + outlet_list
selected_outlet = st.sidebar.selectbox(
    'Select Outlet:',
    outlet_options,
    index=0 
)

# Filter data based on the selected outlet
if selected_outlet == 'All Outlets':
    df_outlet_filtered = df_data.copy()
else:
    df_outlet_filtered = df_data[df_data[OUTLET_COL] == selected_outlet].copy()

# Category Filter (Radio buttons for single selection, plus 'All Categories' option)
category_options = ['All Categories'] + sorted(df_outlet_filtered[CATEGORY_COL].unique())
selected_category = st.sidebar.radio(
    'Select Category:',
    category_options,
    index=0 
)

# ----------------------------------------------------
# 2. Data Filtering and Aggregation
# ----------------------------------------------------

# Primary filter: filter by selected outlet and category
if selected_category == 'All Categories':
    df_final_filtered = df_outlet_filtered
else:
    df_final_filtered = df_outlet_filtered[df_outlet_filtered[CATEGORY_COL] == selected_category]


# Determine the data source for the main chart/table based on the selection
if selected_outlet == 'All Outlets' and selected_category != 'All Categories':
    # Aggregate data by OUTLET for the selected CATEGORY
    df_chart_data = df_final_filtered.groupby(OUTLET_COL).sum(numeric_only=True).reset_index()
    y_axis_field = OUTLET_COL # Chart will be Outlet-wise
elif selected_category == 'All Categories' and selected_outlet == 'All Outlets':
    # Aggregate data by CATEGORY for the overall view
    df_chart_data = df_final_filtered.groupby(CATEGORY_COL).sum(numeric_only=True).reset_index()
    df_chart_data = df_chart_data.sort_values(by=STOCK_VALUE_COL, ascending=False)
    y_axis_field = CATEGORY_COL # Chart will be Category-wise
else:
    # Single Outlet (All or Single Category selected)
    df_chart_data = df_final_filtered.sort_values(by=STOCK_VALUE_COL, ascending=False)
    y_axis_field = CATEGORY_COL # Chart will be Category-wise

# ----------------------------------------------------
# 3. Dynamic Key Insights
# ----------------------------------------------------

# Calculations rely on the columns being numeric after the fix above
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
    # This line should now work as current_total_sale is guaranteed to be a number (or 0)
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
        data_display = df_chart_data.iloc[0]
        st.table(data_display[[CATEGORY_COL, STOCK_VALUE_COL, REDUCE_STOCK_COL, MAX_STOCK_COL, MONTHLY_SALE_COL, TOTAL_SALE_COL]].rename({
            STOCK_VALUE_COL: 'Current Stock Value', 
            REDUCE_STOCK_COL: 'Max Stock - Current Stock',
            MAX_STOCK_COL: 'Max Allowed Stock'
        }).to_frame().T.set_index(CATEGORY_COL))
        
        st.subheader("Stock vs. Max Stock")
        stock_chart_data = pd.DataFrame({
            'Metric': ['Current Stock', 'Max Stock'],
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
        # Get the sorted list of categories/outlets for explicit sort (fixes Altair errors)
        sort_order = df_chart_data[y_axis_field].tolist()
        
        # Chart 1: Stock Value by Y-axis Field (Category or Outlet) - VERTICAL
        base = alt.Chart(df_chart_data).encode(
            x=alt.X(y_axis_field, sort=alt.SortField(field=STOCK_VALUE_COL, op='sum', order='descending'), title=y_axis_field, axis=alt.Axis(labelAngle=-45)), 
            tooltip=[y_axis_field, alt.Tooltip(STOCK_VALUE_COL, format=',.0f'), MAX_STOCK_COL]
        ).properties(
            title=f"Current Stock Value by {y_axis_field}"
        )

        chart_stock = base.mark_bar(color='#4c78a8').encode(
            y=alt.Y(STOCK_VALUE_COL, title="Current Stock Value (AED)"),
        )
        
        # Chart 2: Reduce Stock by Y-axis Field - VERTICAL with INVERTED Y-AXIS (Filtered to only show <= 0)
        chart_reduce = alt.Chart(df_chart_data).transform_filter(
            alt.FieldRangePredicate(field=REDUCE_STOCK_COL, range=[None, 0])
        ).encode(
            x=alt.X(y_axis_field, sort=sort_order, title=y_axis_field, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y(REDUCE_STOCK_COL, title="Overstock (Max - Current)", scale=alt.Scale(reverse=True)), 
            color=alt.Color(REDUCE_STOCK_COL, 
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
            x='shared' 
        ).configure_title(
            fontSize=16,
            anchor='start'
        )

        st.altair_chart(final_chart, use_container_width=True)

    # 5. Display the filtered data table (always show this)
    st.subheader("Filtered Data Table")
    table_cols = [OUTLET_COL, CATEGORY_COL, STOCK_VALUE_COL, REDUCE_STOCK_COL, TOTAL_SALE_COL, MAX_STOCK_COL, MONTHLY_SALE_COL]
    
    if selected_outlet != 'All Outlets':
        table_cols.remove(OUTLET_COL)
    if selected_category != 'All Categories':
        table_cols.remove(CATEGORY_COL)
    
    st.dataframe(df_final_filtered[table_cols],
                 use_container_width=True)
