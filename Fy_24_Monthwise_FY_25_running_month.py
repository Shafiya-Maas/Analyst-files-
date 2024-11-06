import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Load the data
df = pd.read_csv("Transaction_Vs_Billing_data (3).csv")

# Set page configuration
st.set_page_config(page_title="Fy 24 Monthwise & FY 25 Running Month", page_icon=":bar_chart:", layout="wide")

# Title
st.title("📊 Fy 24 Monthwise & FY 25 Running Month")

# Sidebar for filters
st.sidebar.header("Filter Options")

# Convert 'billing date' and 'delivery date' to datetime
df['billing date'] = pd.to_datetime(df['billing date'])
df['delivery date'] = pd.to_datetime(df['delivery date'])


# Calculate TAT as billing date - delivery date + 1
df['TAT'] = (df['delivery date'] - df[ 'billing date']).dt.days + 1

# Define month-year combinations for fiscal years 2024 and 2025
month_years = [
    'April 2024', 'May 2024', 'June 2024', 'July 2024', 'August 2024', 'September 2024', 'October 2024',
    'November 2024', 'December 2024', 'January 2025', 'February 2025', 'March 2025',
    'April 2025', 'May 2025', 'June 2025', 'July 2025', 'August 2025', 'September 2025'
]

# Default start and end values
default_start = month_years[0]
default_end = month_years[-1]


# Initialize session state for start and end dates if not already set
if 'start_month_year' not in st.session_state:
    st.session_state['start_month_year'] = default_start
if 'end_month_year' not in st.session_state:
    st.session_state['end_month_year'] = default_end

# Clear Filters button functionality
if st.sidebar.button('Clear Filters'):
    st.session_state['start_month_year'] = default_start
    st.session_state['end_month_year'] = default_end
    st.experimental_rerun()  # Rerun to update the dropdowns immediately

# Month-Year Dropdown Filter
start_month_year = st.sidebar.selectbox(
    "Start Month-Year", 
    month_years, 
    index=month_years.index(st.session_state['start_month_year']),
    key="start_month_select"
)
end_month_year = st.sidebar.selectbox(
    "End Month-Year", 
    month_years, 
    index=month_years.index(st.session_state['end_month_year']),
    key="end_month_select"
)

# Update session state with current selection
st.session_state['start_month_year'] = start_month_year
st.session_state['end_month_year'] = end_month_year

# Convert selected month-year to datetime
start_date = datetime.strptime(start_month_year, '%B %Y')
end_date = datetime.strptime(end_month_year, '%B %Y')

# Adjust the end_date to the last day of the selected month
next_month = end_date.replace(day=28) + timedelta(days=4)  # Move to the next month
end_date = next_month - timedelta(days=next_month.day)  # Move to the last day of the current month

# Filter data based on selected month-year range and other conditions
filtered_df = df[(df['status type'] == 'Billed') & 
                 (df['garage type'].isin(['COCO', 'FOCO'])) & 
                 (df['delivery date'] >= pd.to_datetime(start_date)) & 
                 (df['delivery date'] <= pd.to_datetime(end_date))]

# Create a new column for fiscal year
filtered_df['fiscal_year'] = filtered_df['delivery date'].apply(lambda x: x.year if x.month >= 4 else x.year - 1)




# Calculate KPIs for RJC Total, AJC Total, and Billed Count
rjc_total = filtered_df[filtered_df['document type'].str.contains("RJC")]['document type'].count()
ajc_total = filtered_df[filtered_df['document type'].str.contains("AJC")]['document type'].count()
billed_count = filtered_df['document type'].count()  # Total billed entries

# Calculate TAT RJC and TAT AJC totals
tat_rjc_total = filtered_df[filtered_df['document type'].str.contains("RJC")]['TAT'].sum()
tat_ajc_total = filtered_df[filtered_df['document type'].str.contains("AJC")]['TAT'].sum()

# Define CSS for the metric box styling
st.markdown("""
    <style>
        .metric-box { 
            padding: 20px; 
            border-radius: 10px; 
            color: white; 
            font-weight: bold; 
            text-align: center;
            margin: 5px;
        }
        .rjc-total { background-color: #FF6F61; }  /* Light Red for RJC Total */
        .ajc-total { background-color: #6FA8DC; }  /* Light Blue for AJC Total */
        .billed-count { background-color: #FFD700; } /* Gold for Total Billed Count */
        .tat-rjc-total { background-color: #5F9EA0; } /* Light Teal for TAT RJC Total */
        .tat-ajc-total { background-color: #FFB6C1; } /* Light Pink for TAT AJC Total */
    </style>
""", unsafe_allow_html=True)

# Display KPIs in a row with styled backgrounds
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"<div class='metric-box rjc-total'>RJC Total<br><span style='font-size: 24px;'>{rjc_total}</span></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='metric-box ajc-total'>AJC Total<br><span style='font-size: 24px;'>{ajc_total}</span></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='metric-box billed-count'>Total Billed Count<br><span style='font-size: 24px;'>{billed_count}</span></div>", unsafe_allow_html=True)

with col4:
    st.markdown(f"<div class='metric-box tat-rjc-total'>TAT RJC Total<br><span style='font-size: 24px;'>{tat_rjc_total}</span></div>", unsafe_allow_html=True)

with col5:
    st.markdown(f"<div class='metric-box tat-ajc-total'>TAT AJC Total<br><span style='font-size: 24px;'>{tat_ajc_total}</span></div>", unsafe_allow_html=True)


# Create the delivery count pivot table
delivery_pivot_table = pd.pivot_table(
    data=filtered_df,
    index='document type',
    columns=[filtered_df['fiscal_year'], filtered_df['delivery date'].dt.strftime('%B %Y')],
    values='delivery date',
    aggfunc='count',
    fill_value=0
)

# Check if the delivery pivot table is not empty
if not delivery_pivot_table.empty:
    # Rename columns to include MTD for the current month
    current_month = datetime.now().strftime('%B %Y')
    delivery_pivot_table.columns = [f"{col[1]} (MTD)" if col[1] == current_month else col[1] for col in delivery_pivot_table.columns]

    # Define the order of months from April 2023 to March 2025
    month_order = [
        'Apr 2023', 'May 2023', 'June 2023', 'July 2023', 'Aug 2023', 'Sep 2023', 'Oct 2023', 'Nov 2023', 'Dec 2023',
        'Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024', 'May 2024', 'June 2024', 'July 2024', 'August 2024',
        'September 2024', 'Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025', 'Feb 2025', 'Mar 2025'
    ]
    
    # Reorder columns by the defined month order
    delivery_pivot_table = delivery_pivot_table.reindex(columns=month_order, level=1)

    # Add a total row
    delivery_pivot_table.loc['Total (RJC + AJC)'] = delivery_pivot_table.sum(axis=0)

    # Fill non-finite values with 0 and convert to integers
    delivery_pivot_table = delivery_pivot_table.fillna(0).astype(int)

    # Ensure all months are displayed, even if they have no data
    delivery_pivot_table = delivery_pivot_table.reindex(columns=month_order, fill_value=0, level=1)

# Display the delivery pivot table
st.write("Pivot Table 1: RO Delivered FY 24 Monthwise & FY 25 Running Month")
st.write(delivery_pivot_table)

# Create the TAT pivot table
tat_pivot_table = pd.pivot_table(
    data=filtered_df,
    index='document type',
    columns=[filtered_df['fiscal_year'], filtered_df['delivery date'].dt.strftime('%B %Y')],
    values='TAT',
    aggfunc='sum',  # Calculate average TAT for each month
    fill_value=0
)

# Check if the TAT pivot table is not empty
if not tat_pivot_table.empty:
    # Rename columns to include MTD for the current month
    tat_pivot_table.columns = [f"{col[1]} (MTD)" if col[1] == current_month else col[1] for col in tat_pivot_table.columns]
    
    # Reorder columns by the defined month order
    tat_pivot_table = tat_pivot_table.reindex(columns=month_order, level=1)
    
    # Add a total row
    tat_pivot_table.loc['Total (RJC + AJC)'] = tat_pivot_table.sum(axis=0)
    
    # Fill non-finite values with 0 and convert to integers
    tat_pivot_table = tat_pivot_table.fillna(0).astype(int)

    # Ensure all months are displayed, even if they have no data
    tat_pivot_table = tat_pivot_table.reindex(columns=month_order, fill_value=0, level=1)

# Display the TAT pivot table
st.write("Pivot Table 2: Average TAT FY 24 Monthwise & FY 25 Running Month")
st.write(tat_pivot_table)


