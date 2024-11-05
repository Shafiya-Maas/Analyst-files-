import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

# Load the data
df = pd.read_csv("Transaction_Vs_Billing_data (3).csv")

# Set page configuration
st.set_page_config(page_title="Fy 24 Monthwise & FY 25 running month", page_icon=":bar_chart:", layout="wide")

# Title
st.title("📊 Fy 24 Monthwise & FY 25 running month")

# Sidebar for filters
st.sidebar.header("Filter Options")

# Convert 'delivery date' to datetime
df['delivery date'] = pd.to_datetime(df['delivery date'])

# Define month-year combinations for fiscal years 2024 and 2025
month_years = [
    'April 2024', 'May 2024', 'June 2024', 'July 2024', 'August 2024', 'September 2024', 'October 2024', 'November 2024', 'December 2024', 'January 2025', 'February 2025', 'March 2025',
    'April 2025', 'May 2025', 'June 2025', 'July 2025', 'August 2025', 'September 2025'
]

# Allow user to select the filter type: Exact Dates or Month-Year
filter_type = st.sidebar.radio("Select Date Range Type", ("Exact Date Range", "Month-Year"))

if filter_type == "Exact Date Range":
    # Calendar Date Input for Start Date and End Date
    start_date = st.sidebar.date_input("Start Date", value=datetime(2023, 4, 1))
    end_date = st.sidebar.date_input("End Date", value=datetime(2025, 3, 31))

    # Ensure the end date is not before the start date
    if start_date > end_date:
        st.sidebar.error("Error: End Date must be after Start Date.")

else:
    # Month-Year Dropdown Filter
    start_month_year = st.sidebar.selectbox("Start Month-Year", month_years)
    end_month_year = st.sidebar.selectbox("End Month-Year", month_years, index=len(month_years)-1)

    # Convert selected month-year to datetime
    start_date = datetime.strptime(start_month_year, '%B %Y')
    end_date = datetime.strptime(end_month_year, '%B %Y')

    # Adjust the end_date to the last day of the selected month
    next_month = end_date.replace(day=28) + timedelta(days=4)  # Move to the next month
    end_date = next_month - timedelta(days=next_month.day)  # Move to the last day of the current month


# Filter data based on selected date range and other conditions
filtered_df = df[(df['status type'] == 'Billed') & 
                 (df['garage type'].isin(['COCO', 'FOCO'])) & 
                 (df['delivery date'] >= pd.to_datetime(start_date)) & 
                 (df['delivery date'] <= pd.to_datetime(end_date))]

# Debug: Print the filtered data
print("Filtered Data:")
print(filtered_df)


# Create a new column for fiscal year
filtered_df['fiscal_year'] = filtered_df['delivery date'].apply(lambda x: x.year if x.month >= 4 else x.year - 1)

# Create pivot table
pivot_table = pd.pivot_table(
    data=filtered_df,
    index='document type',
    columns=[filtered_df['fiscal_year'], filtered_df['delivery date'].dt.strftime('%B %Y')],
    values='delivery date',
    aggfunc='count',
    fill_value=0
)


# Check if the pivot table is not empty
if not pivot_table.empty:
    # Rename columns to include MTD for the current month
    current_month = datetime.now().strftime('%B %Y')
    pivot_table.columns = [f"{col[1]} (MTD)" if col[1] == current_month else col[1] for col in pivot_table.columns]

    # Define the order of months from April 2023 to March 2025
    month_order = [
        'Apr 2023', 'May 2023', 'June 2023', 'July 2023', 'Aug 2023', 'Sep 2023', 'Oct 2023', 'Nov 2023', 'Dec 2023', 'Jan 2024', 'Feb 2024', 'Mar 2024',
        'Apr 2024', 'May 2024', 'June 2024', 'July 2024', 'Aug 2024', 'Sep 2024 (MTD)', 'Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025', 'Feb 2025', 'Mar 2025'
    ]
    
    # Reorder columns by the defined month order
    pivot_table = pivot_table.reindex(columns=month_order, level=1)

    # Add a total row
    pivot_table.loc['Total (RJC + AJC)'] = pivot_table.sum(axis=0)

    # Fill non-finite values with 0 and convert to integers
    pivot_table = pivot_table.fillna(0).astype(int)

    # Ensure all months are displayed, even if they have no data
    pivot_table = pivot_table.reindex(columns=month_order, fill_value=0, level=1)

#Print the final pivot table
st.write("Pivot Table: RO Delivered FY 24 Monthwise & FY 25 Running Month")
st.write(pivot_table)
