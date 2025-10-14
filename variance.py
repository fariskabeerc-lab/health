import streamlit as st
import pandas as pd
import altair as alt
import io

# --- Load Data ---
# Load the pre-processed and combined data
try:
    # Assuming 'combined_stock_data.csv' is in the same directory
    df_data = pd.read_csv("combined_stock_data.csv")
except FileNotFoundError:
    st.error("Error: 'combined_stock_data.csv' not found. Please ensure the file is in the same directory as the script.")
    st.stop()

# --- Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("🛒 Supermarket Inventory & Sales Dashboard")

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
# 2. Data Filtering based on Selections
# ----------------------------------------------------
if selected_category == 'All Categories':
    df_final_filtered = df_outlet_filtered
else:
    # Filter by selected category
    df_final_filtered = df_outlet_filtered[df_outlet_filtered['Category'] == selected_category]

# Sort by Stock Value for better visualization if viewing multiple items
if selected_category == 'All Categories' or selected_outlet == 'All Outlets':
    # If viewing all outlets, we need to aggregate by category for charting
    if selected_outlet == 'All Outlets' and selected_category == 'All Categories':
         df_chart_data = df_final_filtered.groupby('Category').sum().reset_index()
         df_chart_data = df_chart_data.sort_values(by='Stock Value', ascending=False)
    else:
        # Sort data if viewing multiple categories in a single outlet
        df_chart_data = df_final_filtered.sort_values(by='Stock Value', ascending=False)
else:
    # Single record view
    df_chart_data = df_final_filtered


# ----------------------------------------------------
# 3. Dynamic Key Insights
# ----------------------------------------------------

# --- A. Insight Display for All Outlets + Single Category ---
if selected_outlet == 'All Outlets' and selected_category != 'All Categories':
    # Aggregate data by outlet for the selected category
    df_insight_agg = df_final_filtered.groupby('Outlet').sum().reset_index()
    
    st.header(f"Outlet Breakdown for Category: **{selected_category}**")
    st.subheader(f"Total Stock Value: **{df_final_filtered['Stock Value'].sum():,.0f}** AED")

    # Display outlet-wise metrics in columns
    cols = st.columns(len(df_insight_agg))
    
    for i, row in df_insight_agg.iterrows():
        outlet_name = row['Outlet'].split(' ')[0] # Use first word of outlet name for brevity
        stock_value = row['Stock Value']
        reduce_stock = row['Reduce Stock']
        
        status = "Balanced"
        if reduce_stock < 0:
            status = "Overstocked"
        elif reduce_stock > 0:
            status = "Understocked"
            
        with cols[i]:
            st.metric(
                label=f"**{outlet_name}** Stock",
                value=f"{stock_value:,.0f} AED",
                delta=f"Reduce: {reduce_stock:,.0f} ({status})",
                delta_color="off" if reduce_stock == 0 else ("inverse" if reduce_stock < 0 else "normal")
            )
    st.markdown("---")

# --- B. Standard Insight Display ---
else:
    # Calculate standard metrics for the current selection
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
    # Determine the y-axis field (Category name or Outlet name)
    y_field = 'Category' if selected_outlet != 'All Outlets' else 'Category' # Always category when multiple categories are shown
    
    # 4a. Single Item/Small View
    if selected_category != 'All Categories' and selected_outlet != 'All Outlets':
        st.subheader(f"Detailed Metrics for {selected_category}")
        
        # Display key figures in a simple table for the single category view
        data_display = df_final_filtered.iloc[0]
        
        st.table(data_display[['Category', 'Stock Value', 'Reduce Stock', 'Max Stock', 'Monthly Sale', 'Total Sale']].rename({
            'Stock Value': 'Current Stock Value', 
            'Reduce Stock': 'Max Stock - Current Stock',
            'Max Stock': 'Max Allowed Stock'
        }).to_frame().T.set_index('Category'))
        
        # Single item visualization (Stock vs. Max Stock)
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

    # 4b. Multiple Items/Full Chart View
    else:
        st.subheader("Breakdown Chart")
        
        # Determine the field to use for the y-axis based on the selection
        y_axis_field = 'Category'
        
        # Chart 1: Stock Value by Y-axis Field
        base = alt.Chart(df_chart_data).encode(
            y=alt.Y(y_axis_field, sort='-x', title=y_axis_field),
            tooltip=[y_axis_field, alt.Tooltip('Stock Value', format=',.0f'), 'Max Stock']
        ).properties(
            title=f"Current Stock Value"
        )

        chart_stock = base.mark_bar(color='#4c78a8').encode(
            x=alt.X('Stock Value', title="Current Stock Value (AED)"),
        )

        # Chart 2: Reduce Stock by Y-axis Field
        chart_reduce = alt.Chart(df_chart_data).encode(
            y=alt.Y(y_axis_field, sort=alt.EncodingSortField(field="Stock Value", op="sum", order='descending')),
            x=alt.X('Reduce Stock', title="Reduce Stock (Max Stock - Current Stock)"),
            color=alt.Color('Reduce Stock', 
                            scale=alt.Scale(domain=[df_chart_data['Reduce Stock'].min(), 0, df_chart_data['Reduce Stock'].max()], range=['red', 'gray', 'green']),
                            legend=None),
            tooltip=[y_axis_field, alt.Tooltip('Reduce Stock', format=',.0f')]
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

        st.altair_chart(final_chart, use_container_width=True)

    # 5. Display the filtered data table (always show this)
    st.subheader("Filtered Data Table")
    # Determine the columns to show in the table
    table_cols = ['Outlet', 'Category', 'Stock Value', 'Reduce Stock', 'Total Sale', 'Max Stock', 'Monthly Sale']
    if selected_outlet != 'All Outlets':
        table_cols.remove('Outlet')
    
    st.dataframe(df_final_filtered[table_cols],
                 use_container_width=True)
