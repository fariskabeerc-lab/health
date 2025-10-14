import streamlit as st
import pandas as pd
import io

# --- Data Definition ---
# Data for SHAMS AL MADINA HYPERMARKET LLC SALEM MALL STOCK
shams_data = {
    'Category': ['BAKERY', 'BEVERAGES', 'BUTCHERY', 'CHILLED AND DAIRY', 'ELECTRONICS', 'FISH', 'FMCG FOOD', 'FMCG NON FOOD', 'FOOT WEAR', 'FROZEN FOODS', 'FRUITS&VEGETABLE', 'GARMENTS', 'HOME APPLIANCE', 'HOME FURNISHING', 'HOUSEHOLD', 'IMITATION COUNTER', 'IT PRODUCTS', 'JEWELLERIES & ACCESSORIES', 'LUGGAGE', 'MEDICINE', 'MOBILE & ACCESSORIES', 'ROASTERY', 'SHOP CONSUMPTION', 'STATIONERY', 'TELEPHONE CARDS', 'TEXTILES', 'TOBACCO&ACC', 'TOYS & SPORTS', 'WATCH & ACCESSORIES', 'TOTAL'],
    'Stock Value': [11577, 95118, 29977, 27260, 560473, 4700, 1057312, 955668, 294809, 101321, 37399, 968724, 608782, 234560, 320269, 13, 4776, 90089, 57725, 56899, 32681, 143496, 27943, 85429, 17596, 81367, 211141, 121606, 147184, 6195894],
    'Total Sale': [394596, 1060804, 1701681, 1567269, 1309746, 505945, 8308776, 3624375, 1232117, 861511, 5574343, 4017802, 1250071, 1311796, 1447168, 102, 466, 435645, 715062, 496454, 980, 3458578, 319551, 285225, 662565, 141373, 178455, 443107, 375172, 41680734],
    'AVG per Day': [1385, 3722, 5971, 5499, 4596, 1775, 29154, 12717, 4323, 3023, 19559, 14098, 4386, 4603, 5078, 0, 2, 1529, 2509, 1742, 3, 12135, 1121, 1001, 2325, 496, 626, 1555, 1316, 146248],
    'Monthly Sale': [41536, 111664, 179124, 164976, 137868, 53257, 874608, 381513, 129697, 90695, 586773, 422927, 131586, 138084, 152333, 11, 49, 45857, 75270, 52258, 103, 364061, 33637, 30024, 69744, 14881, 18785, 46643, 39492, 4387446],
    'Max Stock': [10000, 60000, 20000, 25000, 300000, 4000, 870000, 580000, 260000, 90000, 40000, 845853, 350000, 200000, 230000, 0, 0, 70000, 60000, 50000, 10000, 120000, 15000, 60000, 15000, 50000, 10000, 100000, 120000, 4565853],
    'Reduce Stock': [-1577, -35118, -9977, -2260, -260473, -700, -187312, -375668, -34809, -11321, 2601, -122871, -258782, -34560, -90269, -13, -4776, -20089, 2275, -6899, -22681, -23496, -7943, -25429, -1596, -31367, -11141, -21606, -27184, -1628040]
}
df_shams = pd.DataFrame(shams_data)

# Data for HILAL AL MADINA HYPERMARKET LLC CRYSTAL MALL
hilal_data = {
    'Category': ['BAKERY', 'BEVERAGES', 'BUTCHERY', 'CHILLED AND DAIRY', 'ELECTRONICS', 'FISH', 'FMCG FOOD', 'FMCG NON FOOD', 'FOOT WEAR', 'FROZEN FOODS', 'FRUITS&VEGETABLE', 'GARMENTS', 'HOME APPLIANCE', 'HOME FURNISHING', 'HOUSEHOLD', 'IMITATION COUNTER', 'IT PRODUCTS', 'JEWELLERIES & ACCESSORIES', 'LUGGAGE', 'MEDICINE', 'MOBILE & ACCESSORIES', 'ROASTERY', 'SHOP CONSUMPTION', 'STATIONERY', 'TELEPHONE CARDS', 'TEXTILES', 'TOBACCO&ACC', 'TOYS & SPORTS', 'WATCH & ACCESSORIES', 'TOTAL'],
    'Stock Value': [5741, 65696, 23359, 16550, 387418, 5642, 641750, 485193, 252453, 53172, 11835, 585607, 304209, 184665, 361309, 24, 8163, 34845, 81814, 26400, 257654, 99417, 5522, 63900, 3425, 30745, 26035, 54771, 34440, 4176365],
    'Total Sale': [116268, 514090, 955117, 569490, 370143, 404204, 2832323, 1090094, 448585, 172839, 2179133, 1300537, 696438, 604899, 553588, 30, 4798, 75990, 227242, 122247, 700739, 1308559, 128343, 70465, 676492, 83301, 105282, 89528, 26840, 16597002],
    'AVG per Day': [439, 1940, 3604, 2149, 1397, 1525, 10688, 4114, 1693, 652, 8223, 4908, 2628, 2283, 2089, 0, 18, 287, 858, 461, 2644, 4938, 484, 266, 2553, 314, 397, 338, 101, 62630],
    'Monthly Sale': [13162, 58199, 108126, 64471, 41903, 45759, 320640, 123407, 50783, 19567, 246694, 147231, 78842, 68479, 62670, 3, 543, 8603, 25726, 13839, 79329, 148139, 14529, 7977, 76584, 9430, 11919, 10135, 3039, 1878906],
    'Max Stock': [3500, 32000, 15000, 12000, 120000, 3500, 330000, 190000, 110000, 30000, 12000, 300000, 200000, 100000, 100000, 0, 0, 15000, 25000, 15000, 80000, 50000, 5000, 18000, 3500, 30000, 10000, 25000, 10000, 1895500],
    'Reduce Stock': [-2241, -33696, -8359, -4550, -267418, -2142, -311750, -295193, -142453, -23172, 165, -285607, -104209, -84665, -261309, -24, -8163, -19845, -56814, -11400, -177654, -49417, -522, -45900, 75, -745, -16035, -29771, -24440, -3405511]
}
df_hilal = pd.DataFrame(hilal_data)

# Data for SABAH AL MADINA NAIF
sabah_data = {
    'Category': ['BAKERY', 'BEVERAGES', 'BUTCHERY', 'CHILLED AND DAIRY', 'ELECTRONICS', 'FISH', 'FMCG FOOD', 'FMCG NON FOOD', 'FOOT WEAR', 'FROZEN FOODS', 'FRUITS&VEGETABLE', 'GARMENTS', 'HOME APPLIANCE', 'HOME FURNISHING', 'HOUSEHOLD', 'IMITATION COUNTER', 'IT PRODUCTS', 'JEWELLERIES & ACCESSORIES', 'LUGGAGE', 'MEDICINE', 'MOBILE & ACCESSORIES', 'ROASTERY', 'SHOP CONSUMPTION', 'STATIONERY', 'TELEPHONE CARDS', 'TEXTILES', 'TOBACCO&ACC', 'TOYS & SPORTS', 'WATCH & ACCESSORIES', 'TOTAL'],
    'Stock Value': [8376, 20570, 4918, 28680, 91955, 1365, 328042, 246679, 36952, 27273, 334, 216773, 81000, 13091, 127813, 1, 724, 9018, 7212, 20727, 13089, 24666, 935, 20739, 14066, 3401, 24720, 9038, 34440, 1416598],
    'Total Sale': [321431, 427219, 1079490, 1176412, 166094, 360442, 3024289, 1225389, 61095, 273012, 2077397, 435559, 248750, 90571, 456167, 126, 377, 32305, 38790, 84311, 30942, 672605, 80648, 65716, 47283, 6291, 388896, 29111, 26840, 12927558],
    'AVG per Day': [1213, 1612, 4074, 4439, 627, 1360, 11412, 4624, 231, 1030, 7839, 1644, 939, 342, 1721, 0, 1, 122, 146, 318, 117, 2538, 304, 248, 178, 24, 1468, 110, 101, 48783],
    'Monthly Sale': [36388, 48364, 122206, 133179, 18803, 40805, 342372, 138723, 6916, 30907, 235177, 49309, 28160, 10253, 51642, 14, 43, 3657, 4391, 9545, 3503, 76144, 9130, 7440, 5353, 712, 44026, 3296, 3039, 1463497],
    'Max Stock': [8500, 20000, 5000, 25000, 40000, 1400, 325000, 200000, 15000, 27000, 0, 100000, 70000, 13000, 100000, 0, 0, 5000, 35000, 10000, 5000, 24000, 0, 15000, 1500, 3000, 20000, 7000, 10000, 1085400],
    'Reduce Stock': [124, -570, 82, -3680, -51955, 35, -3042, -46679, -21952, -273, -334, -116773, -11000, -91, -27813, -1, -724, -4018, 27788, -10727, -8089, -666, -935, -5739, -12566, -401, -4720, -2038, -24440, -331198]
}
df_sabah = pd.DataFrame(sabah_data)

# Store dataframes in a dictionary for easy access
outlet_data = {
    'SHAMS AL MADINA HYPERMARKET LLC SALEM MALL STOCK': df_shams,
    'HILAL AL MADINA HYPERMARKET LLC CRYSTAL MALL': df_hilal,
    'SABAH AL MADINA NAIF': df_sabah
}

# --- Streamlit App Layout ---
st.title("🛒 Supermarket Stock and Sales Data Visualization")
st.markdown("Use the tabs below to view the stock and sales data for each outlet.")

# Create tabs for each outlet
tab_names = list(outlet_data.keys())
tabs = st.tabs(tab_names)

# Populate the tabs
for name, tab in zip(tab_names, tabs):
    with tab:
        st.subheader(f"Data for **{name}**")
        
        # Display the DataFrame in the tab
        # Highlight TOTAL row and columns for better visibility
        def highlight_total_row(row):
            """Highlights the 'TOTAL' row."""
            if row['Category'] == 'TOTAL':
                return ['background-color: lightgray; font-weight: bold'] * len(row)
            return [''] * len(row)

        # Highlight key columns like 'Stock Value' and 'Monthly Sale'
        def bold_key_columns(col):
            """Bolds the 'Stock Value' and 'Monthly Sale' columns."""
            if col.name in ['Stock Value', 'Monthly Sale', 'Total Sale']:
                return ['font-weight: bold'] * len(col)
            return [''] * len(col)

        styled_df = outlet_data[name].style.apply(highlight_total_row, axis=1).apply(bold_key_columns, axis=0)

        st.dataframe(
            styled_df,
            height=800, # Set a fixed height for consistency
            use_container_width=True
        )

# --- Instructions for the user ---
st.markdown(
    """
    ***
    ## Next Steps for Visualization 📊
    
    You can now proceed with further visualizations using this data, such as:
    1.  **Comparison Bar Charts:** Compare `Stock Value`, `Total Sale`, or `Monthly Sale` across outlets for a specific category (e.g., FMCG FOOD).
    2.  **Category Breakdown:** Use a **pie chart** or **treemap** to show the distribution of `Total Sale` by `Category` for a single outlet.
    3.  **Stock Analysis:** Plot `Stock Value` vs. `Max Stock` to identify categories that need stock reduction or replenishment.
    
    Let me know what you'd like to visualize next!
    """
)
