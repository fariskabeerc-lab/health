import streamlit as st
import pandas as pd
import altair as alt
import io

# --- 1. Data Definition and Preprocessing ---
# Define the dataframes as they were extracted from the images.
# Note: The original data is used directly to ensure correct totals.
shams_data = {
    'Category': ['BAKERY', 'BEVERAGES', 'BUTCHERY', 'CHILLED AND DAIRY', 'ELECTRONICS', 'FISH', 'FMCG FOOD', 'FMCG NON FOOD', 'FOOT WEAR', 'FROZEN FOODS', 'FRUITS&VEGETABLE', 'GARMENTS', 'HOME APPLIANCE', 'HOME FURNISHING', 'HOUSEHOLD', 'IMITATION COUNTER', 'IT PRODUCTS', 'JEWELLERIES & ACCESSORIES', 'LUGGAGE', 'MEDICINE', 'MOBILE & ACCESSORIES', 'ROASTERY', 'SHOP CONSUMPTION', 'STATIONERY', 'TELEPHONE CARDS', 'TEXTILES', 'TOBACCO&ACC', 'TOYS & SPORTS', 'WATCH & ACCESSORIES', 'TOTAL'],
    'Stock Value': [11577, 95118, 29977, 27260, 560473, 4700, 1057312, 955668, 294809, 101321, 37399, 968724, 608782, 234560, 320269, 13, 4776, 90089, 57725, 56899, 32681, 143496, 27943, 85429, 17596, 81367, 211141, 121606, 147184, 6195894],
    'Total Sale': [394596, 1060804, 1701681, 1567269, 1309746, 505945, 8308776, 3624375, 1232117, 861511, 5574343, 4017802, 1250071, 1311796, 1447168, 102, 466, 435645, 715062, 496454, 980, 3458578, 319551, 285225, 662565, 141373, 178455, 443107, 375172, 41680734],
    'Reduce Stock': [-1577, -35118, -9977, -2260, -260473, -700, -187312, -375668, -34809, -11321, 2601, -122871, -258782, -34560, -90269, -13, -4776, -20089, 2275, -6899, -22681, -23496, -7943, -25429, -1596, -31367, -11141, -21606, -27184, -1628040],
    'Max Stock': [10000, 60000, 20000, 25000, 300000, 4000, 870000, 580000, 260000, 90000, 40000, 845853, 350000, 200000, 230000, 0, 0, 70000, 60000, 50000, 10000, 120000, 15000, 60000, 15000, 50000, 10000, 100000, 120000, 4565853],
}
df_shams = pd.DataFrame(shams_data)
df_shams['Outlet'] = 'SHAMS AL MADINA HYPERMARKET LLC SALEM MALL STOCK'

hilal_data = {
    'Category': ['BAKERY', 'BEVERAGES', 'BUTCHERY', 'CHILLED AND DAIRY', 'ELECTRONICS', 'FISH', 'FMCG FOOD', 'FMCG NON FOOD', 'FOOT WEAR', 'FROZEN FOODS', 'FRUITS&VEGETABLE', 'GARMENTS', 'HOME APPLIANCE', 'HOME FURNISHING', 'HOUSEHOLD', 'IMITATION COUNTER', 'IT PRODUCTS', 'JEWELLERIES & ACCESSORIES', 'LUGGAGE', 'MEDICINE', 'MOBILE & ACCESSORIES', 'ROASTERY', 'SHOP CONSUMPTION', 'STATIONERY', 'TELEPHONE CARDS', 'TEXTILES', 'TOBACCO&ACC', 'TOYS & SPORTS', 'WATCH & ACCESSORIES', 'TOTAL'],
    'Stock Value': [5741, 65696, 23359, 16550, 387418, 5642, 641750, 485193, 252453, 53172, 11835, 585607, 304209, 184665, 361309, 24, 8163, 34845, 81814, 26400, 257654, 99417, 5522, 63900, 3425, 30745, 26035, 54771, 34440, 4176365],
    'Total Sale': [116268, 514090, 955117, 569490, 370143, 404204, 2832323, 1090094, 448585, 172839, 2179133, 1300537, 696438, 604899, 553588, 30, 4798, 75990, 227242, 122247, 700739, 1308559, 128343, 70465, 676492, 83301, 105282, 89528, 26840, 16597002],
    'Reduce Stock': [-2241, -33696, -8359, -4550, -267418, -2142, -311750, -295193, -142453, -23172, 165, -285607, -104209, -84665, -261309, -24, -8163, -19845, -56814, -11400, -177654, -49417, -522, -45900, 75, -745, -16035, -29771, -24440, -3405511],
    'Max Stock': [3500, 32000, 15000, 12000, 120000, 3500, 330000, 190000, 110000, 30000, 12000, 300000, 200000, 100000, 100000, 0, 0, 15000, 25000, 15000, 80000, 50000, 5000, 18000, 3500, 30000, 10000, 25000, 10000, 1895500],
}
df_hilal = pd.DataFrame(hilal_data)
df_hilal['Outlet'] = 'HILAL AL MADINA HYPERMARKET LLC CRYSTAL MALL'

sabah_data = {
    'Category': ['BAKERY', 'BEVERAGES', 'BUTCHERY', 'CHILLED AND DAIRY', 'ELECTRONICS', 'FISH', 'FMCG FOOD', 'FMCG NON FOOD', 'FOOT WEAR', 'FROZEN FOODS', 'FRUITS&VEGETABLE', 'GARMENTS', 'HOME APPLIANCE', 'HOME FURNISHING', 'HOUSEHOLD', 'IMITATION COUNTER', 'IT PRODUCTS', 'JEWELLERIES & ACCESSORIES', 'LUGGAGE', 'MEDICINE', 'MOBILE & ACCESSORIES', 'ROASTERY', 'SHOP CONSUMPTION', 'STATIONERY', 'TELEPHONE CARDS', 'TEXTILES', 'TOBACCO&ACC', 'TOYS & SPORTS', 'WATCH & ACCESSORIES', 'TOTAL'],
    'Stock Value': [8376, 20570, 4918, 28680, 91955, 1365, 328042, 246679, 36952, 27273, 334, 216773, 81000, 13091, 127813, 1, 724, 9018, 7212, 20727, 13089, 24666, 935, 20739, 14066, 3401, 24720, 9038, 34440, 1416598],
    'Total Sale': [321431, 427219, 1079490, 1176412, 166094, 360442, 3024289, 1225389, 61095, 273012, 2077397, 435559, 248750, 90571, 456167, 126, 377, 32305, 38790, 84311, 30942, 672605, 80648, 65716, 47283, 6291, 388896, 29111, 26840, 12927558],
    'Reduce Stock': [124, -570, 82, -3680, -51955, 35, -3042, -46679, -21952, -273, -334, -116773, -11000, -91, -27813, -1, -724, -4018, 27788, -10727, -8089, -666, -935, -5739, -12566, -401, -4720, -2038, -24440, -331198],
    'Max Stock': [8500, 20000, 5000, 25000, 40000, 1400, 325000, 200000, 15000, 27000, 0, 100000, 70000, 13000, 100000, 0, 0, 5000, 35000, 10000, 5000, 24000, 0, 15000, 1500, 3000, 20000, 7000, 10000, 1085400],
}
df_sabah = pd.DataFrame(sabah_data)
df_sabah['Outlet'] = 'SABAH AL MADINA NAIF'

# Combine all dataframes
df_combined = pd.concat([df_shams, df_hilal, df_sabah], ignore_index=True)

# Filter out the 'TOTAL' row for the operational data, but save the totals for the key insight calculation.
df_totals = df_combined[df_combined['Category'] == 'TOTAL'].copy()
df_data = df_combined[df_combined['Category'] != 'TOTAL'].copy()

# Correctly calculate the overall totals from the TOTAL rows
overall_stock_value = df_totals['Stock Value'].sum()          # Correct: 11,788,857
overall_total_sale = df_totals['Total Sale'].sum()            # Correct: 71,205,294
overall_reduce_stock = df_totals['Reduce Stock'].sum()        # Correct: -5,364,749

# --- Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("🛒 Supermarket Inventory & Sales Dashboard")

# ----------------------------------------------------
# 2. Sidebar Filters
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
    # Use df_combined (with TOTAL rows) for filtering the category list correctly
    df_outlet_filtered = df_combined.copy()
else:
    df_outlet_filtered = df_combined[df_combined['Outlet'] == selected_outlet].copy()

# Category Filter (Radio buttons for single selection, plus 'All Categories' option)
# Base the category list on the filtered outlet data, excluding the TOTAL row
category_options = ['All Categories'] + sorted(df_outlet_filtered[df_outlet_filtered['Category'] != 'TOTAL']['Category'].unique())
selected_category = st.sidebar.radio(
    'Select Category:',
    category_options,
    index=0 # Default to 'All Categories'
)

# ----------------------------------------------------
# 3. Data Filtering and Aggregation
# ----------------------------------------------------

# Data source for insights (df_insight_data) and charts (df_chart_data)

if selected_outlet == 'All Outlets':
    # For All Outlets, always use df_data (no TOTAL rows)
    df_insight_data = df_data.copy()
    
    if selected_category == 'All Categories':
        # Insight data is all categories, all outlets
        # Chart data aggregated by Category across all outlets
        df_chart_data = df_insight_data.groupby('Category').sum(numeric_only=True).reset_index()
        y_axis_field = 'Category'
    else:
        # Insight data is one category, all outlets
        df_insight_data = df_data[df_data['Category'] == selected_category].copy()
        # Chart data aggregated by Outlet for the selected Category
        df_chart_data = df_insight_data.groupby('Outlet').sum(numeric_only=True).reset_index()
        y_axis_field = 'Outlet'

else:
    # Single Outlet selection (use the TOTAL row for insights if All Categories is selected)
    if selected_category == 'All Categories':
        # Insight data comes from the single 'TOTAL' row
        df_insight_data = df_outlet_filtered[df_outlet_filtered['Category'] == 'TOTAL'].copy()
        # Chart data comes from all individual categories (no TOTAL row)
        df_chart_data = df_outlet_filtered[df_outlet_filtered['Category'] != 'TOTAL'].copy()
        y_axis_field = 'Category'
    else:
        # Insight data and Chart data come from the single category row
        df_insight_data = df_outlet_filtered[df_outlet_filtered['Category'] == selected_category].copy()
        df_chart_data = df_insight_data.copy()
        y_axis_field = 'Category'

# ----------------------------------------------------
# 4. Dynamic Key Insights
# ----------------------------------------------------

# If All Outlets and All Categories are selected, use the pre-calculated totals
if selected_outlet == 'All Outlets' and selected_category == 'All Categories':
    current_stock_value = overall_stock_value
    current_total_sale = overall_total_sale
    current_monthly_sale = df_totals['Monthly Sale'].sum()
    current_reduce_stock = overall_reduce_stock
    
    st.header(f"Key Insights: **Overall Combined Performance**")

# Otherwise, calculate totals from the df_insight_data (which is either a single row or a sum of category rows)
else:
    current_stock_value = df_insight_data['Stock Value'].sum()
    current_total_sale = df_insight_data['Total Sale'].sum()
    current_monthly_sale = df_insight_data['Monthly Sale'].sum()
    current_reduce_stock = df_insight_data['Reduce Stock'].sum()
    
    st.header(f"Key Insights for: **{selected_outlet}** - **{selected_category}**")


# Determine Overstocked/Understocked status for the status message
status = "Balanced"
if current_reduce_stock < 0:
    status = "Overstocked"
elif current_reduce_stock > 0:
    status = "Understocked (Room for Stock)"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Stock Value (AED)", f"{current_stock_value:,.0f}")

with col2:
    st.metric("Total Sales (AED)", f"{current_total_sale:,.0f}")

with col3:
    st.metric("Total Monthly Sales (AED)", f"{current_monthly_sale:,.0f}")

with col4:
    delta_value = f"{current_reduce_stock:,.0f}"
    st.metric(f"Inventory Status (Reduce Stock)", delta_value, delta=status)

st.markdown("---")

# ----------------------------------------------------
# 5. Visualization and Table
# ----------------------------------------------------
if df_chart_data.empty:
    st.warning("No data to display for the current selection.")
else:
    # Sort the chart data by Stock Value for better comparison
    df_chart_data = df_chart_data.sort_values(by='Stock Value', ascending=False)
    
    # 5a. Single Item View (for a single Category in a single Outlet)
    if selected_category != 'All Categories' and selected_outlet != 'All Outlets':
        st.subheader(f"Stock vs. Max Stock for {selected_category}")
        data_display = df_chart_data.iloc[0]
        
        # Comparison Bar Chart
        stock_chart_data = pd.DataFrame({
            'Metric': ['Current Stock', 'Max Stock'],
            'Value': [data_display['Stock Value'], data_display['Max Stock']]
        })
        
        stock_bar_chart = alt.Chart(stock_chart_data).mark_bar().encode(
            x=alt.X('Value', title="Value (AED)"),
            y=alt.Y('Metric', sort=None, title=""),
            color=alt.Color('Metric', scale=alt.Scale(range=['#4c78a8', '#e4575c']))
        )
        st.altair_chart(stock_bar_chart, use_container_width=True)

    # 5b. Multiple Items/Full Chart View (Most common scenarios)
    else:
        st.subheader(f"{y_axis_field} Breakdown")
        
        # Chart 1: Stock Value by Y-axis Field (Category or Outlet)
        base = alt.Chart(df_chart_data).encode(
            y=alt.Y(y_axis_field, sort='-x', title=y_axis_field),
            tooltip=[y_axis_field, alt.Tooltip('Stock Value', format=',.0f'), alt.Tooltip('Max Stock', format=',.0f')]
        ).properties(
            title=f"Current Stock Value by {y_axis_field}"
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
            title=f"Inventory Discrepancy (Reduce Stock) by {y_axis_field}"
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

    # 6. Display the filtered data table
    st.subheader("Filtered Data Table")
    
    # Show the data used for the chart (df_chart_data), which is correctly aggregated or filtered
    st.dataframe(df_chart_data, use_container_width=True)
