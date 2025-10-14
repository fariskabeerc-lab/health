import streamlit as st
import pandas as pd
import altair as alt
import io

# --- Load Data ---
# Load the pre-processed and combined data
df_data = pd.read_csv("combined_stock_data.csv")

# --- Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("🛒 Supermarket Inventory Analysis Dashboard")

# 1. Key Insights Display (Hardcoded from the prior analysis step)
st.header("Overall Key Insights")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Stock Value (Overall)", "AED 11,914,245")

with col2:
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
st.header("Category-wise Visualization by Outlet")
outlet_options = sorted(df_data['Outlet'].unique())
selected_outlet = st.selectbox(
    'Select Outlet for Detailed Visualization:',
    outlet_options,
    index=0 # Default to the first outlet
)

# 3. Filter data for the selected outlet, excluding the totals row which was already filtered out.
df_filtered = df_data[df_data['Outlet'] == selected_outlet]
# Sort by Stock Value for better visualization
df_filtered = df_filtered.sort_values(by='Stock Value', ascending=False)

# 4. Visualization (Horizontal Bar Charts)

# Chart 1: Stock Value by Category
base = alt.Chart(df_filtered).encode(
    y=alt.Y('Category', sort='-x', title="Category"),
    tooltip=['Category', alt.Tooltip('Stock Value', format=',.0f'), 'Max Stock']
).properties(
    title=f"Stock Value by Category in {selected_outlet}"
)

chart_stock = base.mark_bar(color='#4c78a8').encode(
    x=alt.X('Stock Value', title="Current Stock Value (AED)"),
)

# Chart 2: Reduce Stock by Category
# Reduce Stock > 0 is understocked (Needs Stocking) - Color: Green
# Reduce Stock < 0 is overstocked (Needs Reduction) - Color: Red
chart_reduce = alt.Chart(df_filtered).encode(
    y=alt.Y('Category', sort=alt.EncodingSortField(field="Stock Value", op="sum", order='descending')),
    x=alt.X('Reduce Stock', title="Reduce Stock (Max Stock - Current Stock)"),
    color=alt.Color('Reduce Stock', scale=alt.Scale(domain=[df_filtered['Reduce Stock'].min(), 0, df_filtered['Reduce Stock'].max()], range=['red', 'gray', 'green']),
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
st.dataframe(df_filtered[['Category', 'Stock Value', 'Reduce Stock', 'Total Sale', 'Max Stock', 'Monthly Sale']],
             use_container_width=True)
