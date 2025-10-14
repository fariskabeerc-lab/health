import streamlit as st
import pandas as pd
import altair as alt
import io

# --- Load Data ---
# Load the pre-processed and combined data
# Assuming 'combined_stock_data.csv' is in the same directory
try:
    df_data = pd.read_csv("combined_stock_data.csv")
except FileNotFoundError:
    st.error("Error: 'combined_stock_data.csv' not found. Please ensure the file is in the same directory as the script.")
    st.stop()

# --- Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("🛒 Supermarket Inventory Analysis Dashboard")

# 1. Overall Key Insights (Static for the combined data)
st.header("Overall Key Insights")
col1, col2, col3, col4 = st.columns(4)

# Static values calculated from the initial combined data analysis
with col1:
    st.metric("Total Stock Value (Overall)", "AED 11,914,245")

with col2:
    # Net Inventory Discrepancy (Negative indicates Overstock)
    st.metric("Net Inventory Discrepancy (Overall)", "AED -4,223,492", "-4,223,492")

with col3:
    st.subheader("Top 3 Overstocked Categories")
    st.markdown("""
    1. **FMCG NON FOOD**: -717,540
    2. **ELECTRONICS**: -579,846
    3. **GARMENTS**: -525,251
    """)

with col4:
    st.subheader("Top Understocked Category")
    st.markdown("""
    1. **FRUITS&VEGETABLE**: +2,432
    """)

st.markdown("---")

# 2. Outlet Filter
st.header("Category-wise Visualization")
col_outlet, col_category = st.columns([1, 2])

with col_outlet:
    outlet_options = sorted(df_data['Outlet'].unique())
    selected_outlet = st.selectbox(
        'Select Outlet:',
        outlet_options,
        index=0 # Default to the first outlet
    )

# Filter data based on the selected outlet
df_outlet_filtered = df_data[df_data['Outlet'] == selected_outlet].copy()

# 3. Category Filter (Dependent on Outlet Selection)
with col_category:
    category_options = sorted(df_outlet_filtered['Category'].unique())
    selected_categories = st.multiselect(
        'Select Category/Categories (or leave blank for all):',
        category_options,
        default=category_options # Default to all categories
    )

# Filter data based on selected categories
if selected_categories:
    df_final_filtered = df_outlet_filtered[df_outlet_filtered['Category'].isin(selected_categories)]
else:
    # If no category is selected, use the outlet-filtered data (or you can choose to show nothing)
    df_final_filtered = df_outlet_filtered

# Sort by Stock Value for better visualization
df_final_filtered = df_final_filtered.sort_values(by='Stock Value', ascending=False)

if df_final_filtered.empty:
    st.warning("No data to display for the current selection.")
else:
    # 4. Visualization (Horizontal Bar Charts)

    # Chart 1: Stock Value by Category
    base = alt.Chart(df_final_filtered).encode(
        y=alt.Y('Category', sort='-x', title="Category"),
        tooltip=['Category', alt.Tooltip('Stock Value', format=',.0f'), 'Max Stock']
    ).properties(
        title=f"Stock Value by Category in {selected_outlet}"
    )

    chart_stock = base.mark_bar(color='#4c78a8').encode(
        x=alt.X('Stock Value', title="Current Stock Value (AED)"),
    )

    # Chart 2: Reduce Stock by Category
    # Color: Red (Overstocked) or Green (Understocked)
    chart_reduce = alt.Chart(df_final_filtered).encode(
        # Use the same sort order as the stock chart
        y=alt.Y('Category', sort=alt.EncodingSortField(field="Stock Value", op="sum", order='descending')),
        x=alt.X('Reduce Stock', title="Reduce Stock (Max Stock - Current Stock)"),
        color=alt.Color('Reduce Stock', 
                        scale=alt.Scale(domain=[df_final_filtered['Reduce Stock'].min(), 0, df_final_filtered['Reduce Stock'].max()], range=['red', 'gray', 'green']),
                        legend=None),
        tooltip=['Category', alt.Tooltip('Reduce Stock', format=',.0f')]
    ).mark_bar().properties(
        title=f"Inventory Discrepancy (Reduce Stock) in {selected_outlet}"
    )

    # Combine the charts vertically
    final_chart = alt.vconcat(
        chart_stock,
        chart_reduce
    ).resolve_scale(
        y='shared' # Share the Category axis between both charts
    ).configure_title(
        fontSize=16,
        anchor='start'
    )

    # 5. Display the chart
    st.altair_chart(final_chart, use_container_width=True)

    # 6. Display the filtered data table
    st.subheader("Filtered Data Table")
    st.dataframe(df_final_filtered[['Category', 'Stock Value', 'Reduce Stock', 'Total Sale', 'Max Stock', 'Monthly Sale']],
                 use_container_width=True)
