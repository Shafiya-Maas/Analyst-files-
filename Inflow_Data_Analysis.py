import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
from dateutil.relativedelta import relativedelta

# Load the data
df = pd.read_csv("Transaction_Vs_Billing_data (3).csv")
target_df = pd.read_csv("Target Data.csv")

# Convert 'date' to datetime
df['date'] = pd.to_datetime(df['date'])
target_df['date'] = pd.to_datetime(target_df['date'], format='%d-%m-%Y %H:%M', errors='coerce')

# Get the current date
today = date.today()

# Calculate the default date range (last three months, e.g., July to September)
current_month = today.month
current_year = today.year

# Determine the start month and year (three months ago)
start_month = current_month - 0 if current_month > 2 else current_month - 2 + 12
start_year = current_year if current_month > 2 else current_year - 1

# Start date is the first day of the start_month
start_date_default = date(start_year, start_month, 1)

# End date is today (or adjust as needed)
end_date_default = today

# Set page configuration
st.set_page_config(page_title="Inflow Source Data Analysis", page_icon=":bar_chart:", layout="wide")

# Title
st.title("📊 Inflow Source Data Analysis")

# Add widgets for filtering the data
st.sidebar.header("Filter Options")

# Clear Filters button action
if st.sidebar.button("Clear Filters"):
    st.session_state['start_date'] = start_date_default
    st.session_state['end_date'] = end_date_default
    # Rerun the app to reflect the reset values
    st.experimental_rerun()


# Add date filters in the Streamlit sidebar with default values
st.sidebar.header("Filter by Date Range")
start_date = st.sidebar.date_input("From Date", value=start_date_default)
end_date = st.sidebar.date_input("To Date", value=today)

# Define the `get_month_data` function to generate month names
def get_month_name(year, month):
    return datetime(year, month, 1).strftime('%B %Y')

def get_month_data(year, month, data_source):
    month_name = get_month_name(year, month)
    month_data = data_source[(data_source['date'].dt.year == year) & 
                             (data_source['date'].dt.month == month)]
    month_counts = month_data.groupby(['major source', 'status type']).size().reset_index(name=month_name)
    return month_counts

# Keep an unfiltered version of the data for month calculations
filtered_data = df.copy()

# Apply condition to include only inflow data with garage type FOFO or COCO
filtered_data = filtered_data[
    (filtered_data['status type'].str.lower() == 'inflow') & 
    (filtered_data['garage type'].isin(['FOCO', 'COCO']))
]


# --- KPI Calculations ---
# Filter by the selected date range for KPIs
kpi_filtered_data = filtered_data[
    (filtered_data['date'] >= pd.to_datetime(start_date)) & 
    (filtered_data['date'] <= pd.to_datetime(end_date))
]

# Sum of labor and parts amounts
labor_amount = kpi_filtered_data['labor amount'].count()
parts_amount = kpi_filtered_data['parts amount'].count()


# Create two columns for the KPIs
kpi1, kpi2 = st.columns(2)

# Define colors for the KPIs
labor_color_bg = "#FFC1C1"   # Light Coral for Labor Amount
labor_color_text = "#B22222"  # Firebrick for text

parts_color_bg = "#C1FFC1"   # Light Green for Parts Amount
parts_color_text = "#228B22"  # Forest Green for text

# Fill in the columns with respective metrics or KPIs with background colors
kpi1.markdown(f"""
    <div style="background-color: {labor_color_bg}; padding: 15px; border-radius: 10px; 
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1); text-align: center;">
        <h3 style="color: {labor_color_text};">Labor Amount</h3>
        <p style="font-size: 24px; color: {labor_color_text};"><b>₹ {labor_amount:,.2f}</b></p>
    </div>
""", unsafe_allow_html=True)

kpi2.markdown(f"""
    <div style="background-color: {parts_color_bg}; padding: 15px; border-radius: 10px; 
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1); text-align: center;">
        <h3 style="color: {parts_color_text};">Parts Amount</h3>
        <p style="font-size: 24px; color: {parts_color_text};"><b>₹ {parts_amount:,.2f}</b></p>
    </div>
""", unsafe_allow_html=True)




# Fill in the three columns with respective metrics or KPIs
kpi1.metric(
    label="Labor Amount ",
    value=f"₹ {labor_amount:,.2f}",  # Format to two decimal places with thousands separator
    delta=None,  # You can add delta if needed (change in amount)
)

kpi2.metric(
    label="Parts Amount ",
    value=f"₹ {parts_amount:,.2f}",  # Format to two decimal places with thousands separator
    delta=None,  # You can add delta if needed (change in amount)
)


kpi1.markdown(
    """
    <div style="background-color: #F0F8FF; padding: 15px; border-radius: 10px; 
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1); text-align: center;">
        <h3 style="color: #1E90FF;"> Labor Amount</h3>
        <p style="font-size: 24px; color: #1E90FF;"><b>₹ {0:,.2f}</b></p>
    </div>
    """.format(labor_amount),
    unsafe_allow_html=True
)

kpi2.markdown(
    """
    <div style="background-color: #E6FFE6; padding: 15px; border-radius: 10px; 
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1); text-align: center;">
        <h3 style="color: #32CD32;"> Parts Amount</h3>
        <p style="font-size: 24px; color: #32CD32;"><b>₹ {0:,.2f}</b></p>
    </div>
    """.format(parts_amount),
    unsafe_allow_html=True
)

# Adjust the data collection process
def collect_monthly_data(end_date):
    # Collect data for the selected month (MTD) and the previous two months (M - 1, M - 2)
    mtd_data = get_month_data(end_date.year, end_date.month, filtered_data)
    m_minus_1_date = pd.Timestamp(end_date) - relativedelta(months=1)
    m_minus_2_date = pd.Timestamp(end_date) - relativedelta(months=2)
    m_minus_1_data = get_month_data(m_minus_1_date.year, m_minus_1_date.month, filtered_data)
    m_minus_2_data = get_month_data(m_minus_2_date.year, m_minus_2_date.month, filtered_data)
    last_year_same_month_date = pd.Timestamp(end_date) - relativedelta(years=1)
    last_year_same_month_data = get_month_data(last_year_same_month_date.year, last_year_same_month_date.month, filtered_data)

    # Merge the three months' data into one table based on 'major source' and 'status type'
    pivot_table = pd.merge(mtd_data, m_minus_1_data, on=['major source', 'status type'], how='outer')
    pivot_table = pd.merge(pivot_table, m_minus_2_data, on=['major source', 'status type'], how='outer')
    pivot_table = pd.merge(pivot_table, last_year_same_month_data, on=['major source', 'status type'], how='outer', suffixes=('', '_last_year'))

    # Fill NaN values with 0
    pivot_table = pivot_table.fillna(0)

    # Rename the columns
    pivot_table.rename(columns={
        pivot_table.columns[2]: get_month_name(end_date.year, end_date.month),
        pivot_table.columns[3]: get_month_name(m_minus_1_date.year, m_minus_1_date.month),
        pivot_table.columns[4]: get_month_name(m_minus_2_date.year, m_minus_2_date.month),
        pivot_table.columns[5]: f"Last Year {get_month_name(last_year_same_month_date.year, last_year_same_month_date.month)}"
    }, inplace=True)

    return pivot_table

# Rest of the code ...


# Define the get_target_value_for_mtd function here
def get_target_value_for_mtd(row):
    major_source = row['major source']
    
    # Check if the major source exists in target_df columns
    if major_source not in target_df.columns:
        return 0
    
    # Filter the target data for the selected date range
    target_data_in_range = target_df[
        (target_df['date'] >= pd.to_datetime(start_date)) & 
        (target_df['date'] <= pd.to_datetime(end_date))
    ]
    
    # Check if the major source column exists in the filtered data
    if major_source not in target_data_in_range.columns:
        return 0
    
    # Sum the values in the target data for the specified major source column
    target_data_mtd = target_data_in_range[major_source].sum()
    
    return target_data_mtd

# Collect and prepare the pivot table data
pivot_table = collect_monthly_data(end_date)

# Apply the target mapping to the 'Target' column only for the MTD month
if pivot_table is not None:
    pivot_table['Target'] = pivot_table.apply(get_target_value_for_mtd, axis=1)

    # Add multiselect filter for major source  
    major_source = st.sidebar.multiselect("Select Major Source", ["BTL MARKETING", "CORPORATE", "DIGITAL", "DSA", "EVEREST", "HYPER LOCAL", "INSURANCE", "JUST DIAL", "SMART OUTLET"])

    # Filter the pivot table based on selected major sources  
    if major_source:  
        filtered_pivot_table = pivot_table[pivot_table['major source'].isin(major_source)]  
    else:  
        filtered_pivot_table = pivot_table  

    # Add Grand Total:
    if not filtered_pivot_table.empty:
        grand_total = filtered_pivot_table.iloc[:, 1:].sum().tolist()
        grand_total_row = pd.DataFrame([['Grand Total'] + grand_total], columns=filtered_pivot_table.columns)
        filtered_pivot_table = pd.concat([filtered_pivot_table, grand_total_row], ignore_index=True)

    # Drop the 'status type' column:
    filtered_pivot_table = filtered_pivot_table.drop('status type', axis=1)

    # Define a function to apply background colors
    def highlight_background(row):
        is_grand_total = row.name == len(filtered_pivot_table) - 1
        return ['background-color: pink' if is_grand_total else 'background-color: lightblue' for _ in row]

    # Apply styling to the DataFrame
    styled_table = filtered_pivot_table.style.apply(highlight_background, axis=1).format(precision=0)

    # Display the styled pivot table
    st.write("Pivot Table: Count of Sources")
    st.dataframe(styled_table, hide_index=True)







import pandas as pd
import streamlit as st
from datetime import datetime

# Sample DataFrame (replace 'df' with your actual DataFrame)
filtered_df = df[(df['status type'] == 'Inflow') & (df['garage type'].isin(['COCO', 'FOCO']))]

# Ensure that the 'job card date' is in datetime format
filtered_df['job card date'] = pd.to_datetime(filtered_df['job card date'], errors='coerce')

# Proceed only with valid dates
filtered_df = filtered_df.dropna(subset=['job card date'])

# Calculate the difference in days between current date and job card date
current_date = pd.to_datetime(datetime.now().date())
filtered_df['Days Difference'] = (current_date - filtered_df['job card date']).dt.days

# Define the categorization logic for WIP (Work in Progress)
def categorize_wip(days):
    if days <= 1:
        return '0-1 Days'
    elif days >= 2 and days <= 3:
        return '2-3 Days'
    elif days >= 4 and days <= 5:
        return '4-5 Days'
    else:
        return '5+ Days'

# Apply the categorization
filtered_df['WIP'] = filtered_df['Days Difference'].apply(categorize_wip)

# Separate RJC and AJC
filtered_df['Group'] = filtered_df['document type'].apply(lambda x: 'RJC Total' if 'RJC' in x else 'AJC Total')

# Create the pivot table
pivot_table = pd.pivot_table(
    filtered_df,
    index=['Group', 'WIP'],
    aggfunc='size',
    fill_value=0
).to_frame(name='Total').reset_index()

# Sort the pivot table
pivot_table_sorted = pivot_table.sort_values(by=['Group', 'WIP'])

# Prepare the formatted results
formatted_table = pd.DataFrame(columns=['Source', 'Total'])

group_order = ['RJC Total', 'AJC Total']
wip_order = ['0-1 Days', '2-3 Days', '4-5 Days', '5+ Days']

# Compute totals
for group in group_order:
    # Calculate the total for the current group
    group_total_value = pivot_table_sorted[pivot_table_sorted['Group'] == group]['Total'].sum()
    
    # Add the group name and its total to the formatted table
    formatted_table = pd.concat([formatted_table, pd.DataFrame({'Source': [group], 'Total': [group_total_value]})], ignore_index=True)

    for wip in wip_order:
        count = pivot_table_sorted[(pivot_table_sorted['Group'] == group) & (pivot_table_sorted['WIP'] == wip)]['Total'].values
        total_count = int(count[0]) if count.size > 0 else 0
        formatted_table = pd.concat([formatted_table, pd.DataFrame({'Source': [wip], 'Total': [total_count]})], ignore_index=True)

# Add the overall total
overall_total = pivot_table_sorted['Total'].sum()
formatted_table = pd.concat([formatted_table, pd.DataFrame({'Source': ['Overall'], 'Total': [overall_total]})], ignore_index=True)


# Define a function to add background colors inside the pivot table
def highlight_cells(row):
    # Blue for the rows that have 'Source' containing 'Total'
    if 'Total' in row['Source'] or row['Source'] == 'Overall':
        return ['background-color: #ADD8E6'] * len(row)
    else:
        return ['background-color: #FFD700'] * len(row)

# Apply the background colors and format to remove decimals
styled_table = formatted_table.style.apply(highlight_cells, axis=1).format(precision=0)

# Display the pivot table in Streamlit
st.write("Pivot Table: Count of WIP as on date")
st.write(styled_table)
