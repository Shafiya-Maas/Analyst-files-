from dependencies import*
from utils import *
import json

def run():
    if 'refresh_data' not in st.session_state:
        st.session_state.refresh_data = False
        
    st.markdown(
            """
            <style>
            /* Hide Streamlit default header */
            header {
                visibility: hidden;
                height: 0;
            }

            /* Adjust Streamlit container padding */
            .block-container {
                padding-top: 3rem;
                padding-bottom: 1rem;
                max-width: 100% !important;
                padding-left: 2rem !important;
                padding-right: 5rem !important;
                margin-left: 0px !important;
                margin-right: 0px !important;
                overflow: scroll !important;
                padding: 10px !important;
            }

            /* === Navbar === */
            .navbar {
                width: 100%;
                height: 60px;  /* Reduced height */
                background: #FFFFFF;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 15px;  /* Reduced padding */
                box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.1);
                position: fixed;
                top: 0;
                left: 0;
                z-index: 1000;
            }
            
            .navbar-title {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin-left: 50px;
                margin-top: 15px;
            }
            
            .navbar-filter {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 16px;
                color: #555;
            }

            /* === Streamlit Select Inputs === */
            div[data-baseweb="select"] {
                font-size: 15px;
                height: auto !important;
                transition: height 0.3s ease;
                -webkit-box-flex: 1;
                flex-grow: 1;
                overflow-x: auto;
                overflow-y: auto;
                max-height: 47px;
                height: 41px;
                white-space: nowrap;
            }
            
            /* Fix text input fields */
            input[type="text"], input[data-baseweb="input"], input.stTextInput {
                font-size: 18px;
                padding: 2px;
            }

            /* === Tabs Styling === */
            div.stTabs [data-baseweb="tab-list"] {
                display: flex;
                gap: 2px;
                border-bottom: none;
            }
            
            /* Default tab style */
            div.stTabs [data-baseweb="tab"] {
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
                background: #F8FAFC;
                color: #030229;
                transition: 0.3s ease-in-out;
                position: relative;
            }
            

            /* Active tab (selected) */
            div.stTabs [aria-selected="true"] {
                background: #213F99 !important;
                color: white !important;
                border-bottom: none !important;
            }

            /* Triangle indicator for active tab */
            div.stTabs [aria-selected="true"]::after {
                content: "";
                position: absolute;
                bottom: -10px;
                left: 50%;
                transform: translateX(-50%);
                width: 0;
                height: 0;
                border-left: 10px solid transparent;
                border-right: 10px solid transparent;
                border-top: 10px solid #213F99;
            }

            /* Hover effect for inactive tabs */
            div.stTabs [aria-selected="false"]:hover {
                background: #030229;
                color: white;
            }

            /* Improve Table Cell Styling */
            table th, table td, #T_641c7 th, #T_641c7 td {
                padding: 12px !important;
                font-size: 16px !important;
                text-align: center !important;
                min-width: 150px !important; /* Prevent column shrinkage */
            }

            /* Sticky table headers */
            table thead, #T_641c7 thead {
                position: sticky;
                top: 0;
                background: white;
                z-index: 10;
            }
            /* date filter padding */
            .st-emotion-cache-1vj2wxa {
                padding-top: 11px; 
            }
            /* date filter reducing down got hidden on top */
            .st-emotion-cache-1jw5mmu {
                margin-top: 1rem;
            
            }
            [data-testid="stSelectbox"] > div {
                width: auto !important;
                min-width: 280px !important;
                max-width: 100% !important;
            }
            ul[data-testid="stSelectboxVirtualDropdown"] {
                width: auto !important;
                min-width: 280px !important;
                max-width: fit-content !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    # Navbar with "Conversion Panel" title
    st.markdown(
            """
            <div class="navbar">
                <div class="navbar-title">Conversion Panel</div>
                <div class="navbar-filter"></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    
    # Set current date and default start/end dates
    current_date = pd.to_datetime("today").date()
    start_date = current_date
    end_date = current_date    
       
        
    # Initialize session state for date inputs if not already set
    if 'start_date' not in st.session_state:
        st.session_state.start_date = start_date
    if 'end_date' not in st.session_state:
        st.session_state.end_date = end_date
    
    
    # Initialize session state variables for refresh functionality
    if 'refreshing' not in st.session_state:
        st.session_state.refreshing = False
    if 'dashboard1_cache' not in st.session_state:
        st.session_state.dashboard1_cache = fetching_core_dashboard_panel()
    
    # Define the refresh function
    def refresh_data():
        st.session_state.refreshing = True
    
    # Create placeholders for dynamic content
    table_placeholder = st.empty()
    button_placeholder = st.empty()
    
    # Perform the refresh operation if refreshing is True
    if st.session_state.refreshing:
        with st.spinner("Refreshing data..."):
            # Clear the table placeholder
            table_placeholder.empty()
            # Fetch new data
            st.session_state.dashboard1_cache = fetching_core_dashboard_panel()
        st.session_state.refreshing = False
    
    # Create layout with 3 columns
    col1, col2, col3 = st.columns((2, 2, 1))
    
    with col1:
        st.session_state.start_date = st.date_input("Start Date", st.session_state.start_date, key="start_date_input")
    
    with col2:
        st.session_state.end_date = st.date_input("End Date", st.session_state.end_date, key="end_date_input")
    
    with col3:
        # Display the refresh button
        st.markdown("""
        <style>
            /* Smaller refresh button */
            .refresh-btn {
                height: 30px !important;
                width: 100px !important;
                padding: 0.25rem 0.5rem !important;
                font-size: 14px !important;                
            }
        </style>
        """, unsafe_allow_html=True)
        st.button("Refresh 🔄", key="refresh_button", on_click=refresh_data, disabled=st.session_state.refreshing)
        
    

    # Show loading spinner while fetching data
    #with st.spinner('Loading dashboard...'):
    # Load the data first
    if "dashboard1_cache" not in st.session_state:
        st.session_state["dashboard1_cache"] = fetching_core_dashboard_panel()
        
    df = st.session_state.get("dashboard1_cache", pd.DataFrame())
        
    #Trim unwanted spaces left side of all values in DB columns
    # Now process the dataframe safely
    if not df.empty:
        # Convert all object columns to string first
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
        
        # Now safely strip whitespace
        df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        
    #st.write("Available columns:", df.columns.tolist())  # Show all columns in the DataFrame

    #st.dataframe(df)
    
    # After loading the DataFrame
    if 'user_source' in df.columns:
        df = df[df['user_source'] != 'Re-Engagement Bookings']
    else:
        st.warning("user_source column not found - skipping filter")

    #st.caption(f"Last refreshed: {st.session_state.get('last_refreshed', 'Not set')}")

    def clean_vehicle_type(x):
        x = str(x).strip().lower()  # Remove ALL whitespace and convert to lowercase
        if x == '2w':
            return '2w'
        elif x == '4w':
            return '4w'
        else:
            return 'No Vehicle Available'
    
    
            
            
    # Data Preparation
    if df is not None:
        df['master_service'] = df['master_service'].astype(str).replace(['0', '', ' '], 'No Service Available')
        df['service_type'] = df['service_type'].astype(str).replace(['0', '', ' '], 'No Service Available')
        df['crm_admin_name'] = df['crm_admin_name'].astype(str).replace(['0', '', ' '], 'No Name Available')
        df['user_source'] = df['user_source'].astype(str).replace(['0', '', ' '], 'No Service Available')
        df['activity_name'] = df['activity_name'].astype(str).replace(['0', '', ' '], 'Unknown Status')
        df['city'] = df['city'].str.strip().str.title().replace(['0', '', ' '],'No city Available')
        df['comments'] = df['activity_name'].astype(str).replace(['0', "", ' '],'Unknown Status')

            
            # Define conditions and results
    condition = [
        (df['comments'].isin([
            'Customer called for a status update', 'Done with Local shop', 'Duplicate Booking',
            'Just Enquiry/checking the App', 'Just for Quotation', 'Post Service Escalationn',
            'Price not satisfied/Quotes are too high', 'Testing', 'Wrong Number'
        ])),
        (df['comments'].isin([
            'All RNRs are exhausted ', 'Currentlyservice is not needed', 'Not in Chennai/Bangalore/Hyderabad/Trichy',
            'Not Interested', 'Reminded in Whatsapp Images not received', 'Vehicle Sold / No Vehicle'
        ]))
    ]
    results = ['Cancelled Booking', 'Other Booking']  # Define your results here

    # Apply np.select
    df['Activity_Status_Final'] = np.select(condition, results, default='Unknown Status')

    # Ensure that the final column is of string type
    df['Activity_Status_Final'] = df['Activity_Status_Final'].astype(str)        


    conditions = [
        # Highest priority conditions first
        (df['flag'] == 1),  # Cancelled
        (df['flag_unwntd'] == 1),  # Duplicate
        ((df['booking_status_code'] == 2) & (df['axle_flag'] == 1) & (df['flag'] == 0)) | (df['service_status_code'] == 'Completed'),  # Goaxle (now includes 'Completed')
        (df['b2b_check_in_report'] == 1),  # End To End Conversion
        (df['service_status_code'].isin(['In Progress', 'Completed'])),  # End To End Conversion
        (df['booking_status_code'].isin([3, 4, 5, 6])) & (df['flag'] == 0),  # follow-up
        (df['booking_status_code'] == 1) & (df['flag'] == 0),  # Idle
        (df['booking_status_code'] == 0) & (df['flag'] != 1),  # Others
        ]   

    results = [
        'Cancelled',
        'Duplicate',
        'Goaxled',  # Now covers 'Completed' as well
        'End To End Conversion',
        'End To End Conversion',
        'Follow-up',
        'Idle',
        'Others'
    ]

    df['new_status'] = np.select(conditions, results, default='Unknown Status')
    df['new_status'] = df['new_status'].astype(str)
    
    
    df['Dates'] = pd.to_datetime(df['booking_date'], format='%Y-%m-%d').dt.date
    # Rest of your code...
    

    
    # Filter the dataframe based on the selected date range
    if st.session_state.start_date <= st.session_state.end_date:
        df_filtered = df[(df['Dates'] >= st.session_state.start_date) & (df['Dates'] <= st.session_state.end_date)].copy()
    else:
        st.warning("Start Date cannot be after End Date.")
        df_filtered = pd.DataFrame(columns=df.columns)
        
    
    # Function to apply additional filters
    def apply_filter(df, df_filtered, column_name, display_name, key, warning_message):
        if column_name in df.columns:
            options = sorted(df[column_name].replace(['0', '', ' '], f'No {display_name} Available').unique())
            selected_values = st.multiselect(display_name, options, key=key)
            if selected_values:
                df_filtered = df_filtered[df_filtered[column_name].isin(selected_values)]
        else:
            st.warning(warning_message)

        return df_filtered



    # Create columns for filters
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5, filter_col6, filter_col7 = st.columns([1, 1, 1, 1, 1, 1, 1])

    # Apply filters in respective columns
    with filter_col1:
        df_filtered = apply_filter(
            df, 
            df_filtered, 
            'city', 
            'City', 
            'city_multiselect', 
            "The 'city' column is missing."
        )

    # With this:
    with filter_col2:        
        df_filtered = apply_filter(
            df, 
            df_filtered, 
            'vehicle_type', 
            'Vehicle Type', 
            'vehicle_type_multiselect', 
            "The 'vehicle_type' column is missing."
        )
        
    
    with filter_col3:
        df_filtered = apply_filter(
            df, 
            df_filtered, 
            'master_service', 
            'Master Service', 
            'master_service_multiselect', 
            "The 'master_service' column is missing."
        )

    with filter_col4:
        df_filtered = apply_filter(
            df, 
            df_filtered, 
            'service_type', 
            'Service Type', 
            'service_type_multiselect', 
            "The 'service_type' column is missing."
        )

    with filter_col5:
        df_filtered = apply_filter(
            df, 
            df_filtered, 
            'crm_admin_name', 
            'Person', 
            'name_multiselect', 
            "The 'crm_admin_name' column is missing."
        )

    with filter_col6:
        df_filtered = apply_filter(
            df, 
            df_filtered, 
            'user_source', 
            'All Bookings', 
            'all_bookings_multiselect', 
            "The 'user_source' column is missing."
        )
        
        
    # Function to clear all filters
    def clear_multi():
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        st.session_state.vehicle_type_multiselect = []
        st.session_state.master_service_multiselect = []
        st.session_state.service_type_multiselect = []
        st.session_state.name_multiselect = []
        st.session_state.all_bookings_multiselect = []
        st.session_state.city_multiselect = []

    # Clear Filters button in filter_col8
    with filter_col7:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some vertical space for alignment
        st.button("Clear filters", on_click=clear_multi)
        

    
    
    # convert datetime into string  
    df['Dates'] = df['Dates'].astype(str)
    # or before using json.dumps
    df = df.astype(str)
    
    
    
    
    def highlight_cells_with_grand_total(row):
        is_grand_total = row.name[0] == 'Grand Total' if isinstance(row.name, tuple) else row.name == 'Grand Total'
        return ['background-color: rgba(0, 0, 0, 0.01); font-weight: bold;' if is_grand_total else '' for _ in row]

    # Function to display a pivot table in Streamlit
    def display_pivot_table(tab, tab_name, df, index_cols, column_cols, value_col, aggfunc, warning_message, filter_condition=None):
        with tab:
            #st.header(tab_name)
    
            # Apply filter condition if provided
            if filter_condition:
                df = df.query(filter_condition)
            
            if not all(col in df.columns for col in index_cols + column_cols + [value_col]):
                st.warning(warning_message)
                return
    
            if df.empty:
                st.warning(warning_message)
                return
    
            # Create pivot table
            pivot_table_df = df.pivot_table(
                index=index_cols,
                columns=column_cols,
                values=value_col,
                aggfunc=aggfunc,
                margins=True,
                margins_name='Grand Total'
            ).fillna(0).astype(int).reset_index()
    
            # Rename the index columns
            pivot_table_df = pivot_table_df.rename(columns={
                'master_service': 'Service',
                'vehicle_type': 'Type',
                'crm_admin_name': 'Name',
                'user_source': 'Source',
                'Activity_Status_Final': 'Activity status',
                'Grand Total': 'Total Leads'
                
            })
            
            
            
            # Convert pivot table to HTML
            pivot_table_html = pivot_table_df.to_html(index=False, escape=False, classes="styled-table")
    
            # Custom CSS styling
            custom_css = """
            <style>
            .styled-table {
                width: 100% !important;
                overflow-x: auto !important;
                margin: 1rem 0;
                font-size: 15px;
                border: none !important;
                border-collapse: collapse !important;
                max-height: 900px;  /* Adjust based on your preferred height */
                
            }
            
            /* Freeze the header row */
                .styled-table thead tr {
                    position: sticky;
                    top: 0;
                    background-color: #F8FAFF !important;  /* Match your header background */
                    z-index: 10;  /* Ensures header stays above table body */
                    box-shadow: 0 2px 2px -1px rgba(0,0,0,0.1);  /* Optional: subtle shadow */
            }
            
            .styled-table th {
                padding: 12px !important;
                text-align: center;
                background-color: #F8FAFF !important;
                color: #464B7C !important;
                border: none !important;
                border-right: 1px solid #D1D5DB !important; /* Add vertical line between headers */
                border-bottom: 1px solid #D1D5DB !important; /* Add bottom border to headers */
            }
        
            .styled-table td {
                padding: 10px !important;
                text-align: center;
                border-top: none !important;
                border-bottom: none !important;
                border-right: 1px solid #D1D5DB !important; /* Add vertical line between cells */
                border-bottom: 1px solid #D1D5DB !important; /* Bottom border for all cells */
            }
            
            .styled-table tbody {
                    border-bottom: 1px solid #D1D5DB !important; /* Add bottom border to body */
            }
            .styled-table tbody tr:nth-child(even) {
                background-color: rgba(0, 0, 0, 0.01) !important;
                border-bottom: 1px solid #D1D5DB !important;
            }
        
            .styled-table tbody tr:last-child td {
                background-color: rgba(97, 98, 100, 0.1) !important;
                color: #464B7C !important;
                font-weight: bold !important;
            }
        
            .styled-table th:first-child,
            .styled-table td:first-child {
                display: none;
            }
        
            /* Remove right border for last column if you want */
            .styled-table td:last-child,
            .styled-table th:last-child {
                border-right: none !important;
            }
            </style>
            """
            
            # Convert full DataFrame to a JSON string for use in JS
            try:
                json_str = json.dumps(df.astype(str).to_dict(orient='records'))
            except Exception as e:
                st.error(f"Error converting data to JSON: {e}")
                json_str = "[]"
                
                
            full_html = f"""
                        {custom_css}
                        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
                        
                        <script>
                            const fullData = {json_str};  // Streamlit JSON data object
                            console.log(fullData);
                        
                            document.addEventListener("DOMContentLoaded", function() {{
                                const table = document.querySelector('.styled-table');
                                if (!table) return;
                        
                                // Get column headers to determine field names dynamically
                                const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.innerText.trim().toLowerCase().replace(/ /g, '_'));
                        
                                table.addEventListener('click', function(e) {{
                                    const clickedCell = e.target.closest("td");
                                    if (!clickedCell) return;
                        
                                    const clickedRow = clickedCell.parentElement;
                                    const cellIndex = Array.from(clickedRow.children).indexOf(clickedCell);
                                    const fieldName = headers[cellIndex];
                                    const cellValue = clickedCell.innerText.trim();
                        
                                    const serviceCell = clickedRow.querySelectorAll('td')[0];
                                    const comments = clickedRow.querySelectorAll('td')[1].innerText.trim();
                                    const masterService = serviceCell.innerText.trim();
                        
                                    const isGrandTotal = clickedRow.innerText.toLowerCase().includes("grand total");
                        
                                    const matchedRows = fullData.filter(row => {{
                                        const serviceMatch = isGrandTotal || (
                                            row.master_service && row.master_service.trim().toLowerCase() === masterService.toLowerCase()
                                        );
                                    
                                        const crmMatch = isGrandTotal || (
                                            row.crm_admin_name && row.crm_admin_name.trim().toLowerCase() === masterService.toLowerCase()
                                        );
                                    
                                        const userSourceMatch = isGrandTotal || (
                                            row.user_source && row.user_source.trim().toLowerCase() === masterService.toLowerCase()
                                        );
                                    
                                        const CommentsMatch = isGrandTotal ||   (row.comments == comments);

                                        
                                        // Match if any field matches the clicked value
                                        const isMatch = serviceMatch || crmMatch || userSourceMatch || CommentsMatch;
                                        
                                        if (fieldName === "idle") {{
                                            return isMatch && row.flag === "0" && row.booking_status_code === "1";
                                        }}
                                        if (fieldName === "cancelled") {{
                                            return isMatch && row.flag === "1";
                                        }}
                                        if (fieldName === "follow-up") {{
                                            return isMatch && ['3','4','5','6'].includes(row.booking_status_code) && row.flag === "0";
                                        }}
                                        if (fieldName === "duplicate") {{
                                            return isMatch && row.flag_unwntd === "1";
                                        }}
                                        if (fieldName === "goaxled") {{
                                            return isMatch && (
                                                (row.booking_status_code === "2" && row.axle_flag === "1" && row.flag === "0") ||
                                                row.service_status_code === 'Completed'
                                            );
                                        }}
                                        if (fieldName === "conversion") {{
                                            return isMatch && (
                                                row.b2b_check_in_report === "1" ||
                                                ['In Progress', 'Completed'].includes(row.service_status_code)
                                            );
                                        }}
                                        if (fieldName === "others") {{
                                            return isMatch && row.booking_status_code === "0" && row.flag !== "1";
                                        }}
                                        if (fieldName === "total_leads") {{
                                            return isMatch;
                                        }}
                                        if (fieldName === "4w") {{
                                            return row.vehicle_type && row.vehicle_type.trim().toLowerCase() === fieldName && CommentsMatch;
                                        }}
                                        
                                        
                                        // General fallback match: match clicked cell value to the same field in fullData
                                        
                                        if (fieldName in row) {{
                                            return row[fieldName] && row[fieldName].toString().trim().toLowerCase() === cellValue.toLowerCase();
                                        }}

    
                                    }});
                                    
                                    if (matchedRows.length > 0) {{
                                        let content = `
                                            <div style="max-height:400px; overflow-y:auto;">
                                                <table style="width:100%; border-collapse: collapse; border: 1px solid #dee2e6;">
                                                    <thead>
                                                        <tr>
                                                            <th style="padding: 8px; background-color: #f8f9fa; border: 1px solid #dee2e6;">#S.NO.</th>
                                                            <th style="padding: 8px; background-color: #f8f9fa; border: 1px solid #dee2e6;">Booking ID</th>
                                                            <th style="padding: 8px; background-color: #f8f9fa; border: 1px solid #dee2e6;">Service Type</th>
                                                            <th style="padding: 8px; background-color: #f8f9fa; border: 1px solid #dee2e6;">Service Center</th>
                                                            <th style="padding: 8px; background-color: #f8f9fa; border: 1px solid #dee2e6;">log</th>
                                                            <th style="padding: 8px; background-color: #f8f9fa; border: 1px solid #dee2e6;">Source</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>`;
                                        
                                        matchedRows.forEach((row, index) => {{
                                            content += `
                                                <tr>
                                                    <td style="padding: 6px; border: 1px solid #dee2e6;">${{index + 1}}</td>
                                                    <td style="padding: 6px; border: 1px solid #dee2e6;">${{row.booking_id || '-'}}</td>
                                                    <td style="padding: 6px; border: 1px solid #dee2e6;">${{row.master_service || '-'}}</td>
                                                    <td style="padding: 6px; border: 1px solid #dee2e6;">${{row.b2b_shop_name || '-'}}</td>
                                                    <td style="padding: 6px; border: 1px solid #dee2e6;">${{row.raw_log_timestamp || '-'}}</td>
                                                    <td style="padding: 6px; border: 1px solid #dee2e6;">${{row.user_source || '-'}}</td>
                                                </tr>`;
                                        }});
                                                                
                                        content += `
                                                    </tbody>
                                                </table>
                                            </div>`;
                        
                                        Swal.fire({{
                                            title: 'Booking Details',
                                            html: content,
                                            width: 800,
                                            confirmButtonText: 'Close'
                                        }});
                                    }} else {{
                                        Swal.fire({{
                                            icon: 'info',
                                            title: 'No Matches Found',
                                            text: 'No data matched the clicked value.'
                                        }});
                                    }}
                                }});
                            }});
                        </script>
                        
                        {pivot_table_html}
            """
                        
                        
            # Render in Streamlit
            components.html(full_html, height=600, scrolling=True)


    st.markdown('<p style="font-weight: bold; margin-bottom: 10px; font-size: 22px;">Conversion Core</p>', unsafe_allow_html=True)
    # Create tabs for different pivot tables    
    tab1, tab2, tab3, tab4 = st.tabs(["Service", "Person", "Source", "Non Conversion"])

    # Display pivot tables
    display_pivot_table(
        tab1, "", df_filtered,
        index_cols=['master_service'],
        column_cols=['new_status'],
        value_col='booking_id',
        aggfunc='count',
        warning_message="No data available for Service-Based Conversion.",
        filter_condition="vehicle_type != 'pv'"
    )

    display_pivot_table(
        tab2, "", df_filtered,
        index_cols=['crm_admin_name'],
        column_cols=['new_status'],
        value_col='booking_id',
        aggfunc='count',
        warning_message="No data available for Person-Based Conversion.",
        filter_condition="vehicle_type != 'pv'"
    )

    display_pivot_table(
        tab3, "", df_filtered,
        index_cols=['user_source'],
        column_cols=['new_status'],
        value_col='booking_id',
        aggfunc='count',
        warning_message="No data available for Source-Based Conversion.",
        filter_condition="vehicle_type != 'pv'"
    )

    # Non-Conversion Data (Multiple Categories)
    with tab4:
        non_conversion_types = {
            "Cancelled": "Activity_Status_Final == 'Cancelled Booking'",
            "Other Booking": "Activity_Status_Final == 'Other Booking'",
        }

        for title, condition in non_conversion_types.items():
            st.subheader(f"Non Conversion - {title}")
            display_pivot_table(
                tab4,
                "",    # No title needed since we have subheader
                df_filtered,
                index_cols=['Activity_Status_Final', 'comments'],
                column_cols=['vehicle_type'],
                value_col='booking_id',
                aggfunc='count',
                warning_message=f"No data available for {title}.",
                filter_condition=f"vehicle_type != 'pv' & {condition}"
            )
        
    #st.dataframe(df_filtered)
        
        
