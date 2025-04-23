from dependencies import*
from utils import fetch_data_once

def run():
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
            /* select box extern in filters */
            .st-gk {
                min-width: 280px !important;
            }
            /* select options extern in filters */
            .st-eb {
                flex-basis: 0%;
                min-width: 163px !important;
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

    # Show loading spinner while fetching data
    with st.spinner('Loading Dashboard...'):
        df, feedback_df = fetch_data_once()  # Unpack the tuple
    
    
    # st.dataframe(df)

    #st.caption(f"Last refreshed: {st.session_state.get('last_refreshed', 'Not set')}")

    def clean_vehicle_type(x):
        x = str(x).strip().lower()
        if '2w' in x:
            return '2w'
        elif '4w' in x:
            return '4w'
        else:
            return 'No Vehicle Available'
            
        # Get both DataFrames
        df1, df2 = load_parquet()
            
        # Clean vehicle_type in the appropriate DataFrame
        df1['vehicle_type'] = df1['vehicle_type'].apply(clean_vehicle_type)
        # or if you need to clean both:
        df2['vehicle_type'] = df2['vehicle_type'].apply(clean_vehicle_type)
        
        
            
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
    

    # Set current date and default start/end dates
    current_date = pd.to_datetime("today").date()
    start_date = current_date
    end_date = current_date    
       
        
    # Initialize session state for date inputs if not already set
    if 'start_date' not in st.session_state:
        st.session_state.start_date = start_date
    if 'end_date' not in st.session_state:
        st.session_state.end_date = end_date

    # Date picker inputs using session state
    col1, col2 = st.columns((2))

    with col1:
        st.session_state.start_date = st.date_input("Start Date", st.session_state.start_date, key="start_date_input")

    with col2:
        st.session_state.end_date = st.date_input("End Date", st.session_state.end_date, key="end_date_input")

    # Filter the dataframe based on the selected date range
    if st.session_state.start_date <= st.session_state.end_date:
        df_filtered = df[(df['Dates'] >= st.session_state.start_date) & (df['Dates'] <= st.session_state.end_date)].copy()
    else:
        st.warning("Start Date cannot be after End Date.")
        df_filtered = pd.DataFrame(columns=df.columns)
        

    # Function to apply additional filters
    def apply_filter(df, df_filtered, column_name, display_name, key, warning_message):
        if column_name in df.columns:
            options = df[column_name].replace(['0', '', ' '], f'No {display_name} Available').unique()
            selected_values = st.multiselect(display_name, options, key=key)
            if selected_values:
                df_filtered = df_filtered[df_filtered[column_name].isin(selected_values)]
        else:
            st.warning(warning_message)

        return df_filtered



    # Create columns for filters
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5, filter_col6, filter_col7, filter_col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])

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
        # First clean the vehicle types in your main DataFrame
        df['vehicle_type'] = df['vehicle_type'].apply(clean_vehicle_type)
        
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
        

    with filter_col8:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Refresh🔄", key="refresh_button"):
            fetch_data_once(force_refresh=True)        
            st.rerun()
            
    st.markdown("<hr style='margin: 0; padding: 0;'>", unsafe_allow_html=True)


    def highlight_cells_with_grand_total(row):
        is_grand_total = row.name[0] == 'Grand Total' if isinstance(row.name, tuple) else row.name == 'Grand Total'
        return ['background-color: rgba(0, 0, 0, 0.01); font-weight: bold;' if is_grand_total else '' for _ in row]

    # Function to display a pivot table in Streamlit
    def display_pivot_table(tab, tab_name, df, index_cols, column_cols, value_col, aggfunc, warning_message, filter_condition=None):
        with tab:
            st.header(tab_name)

            # Apply filter condition if provided
            if filter_condition:
                df = df.query(filter_condition)

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
                'Grand Total': 'Leads'
                
            })
            
            # Define column orders for different tabs
            if tab_name == "Service":  # Tab 1
                # Get all status columns that exist in the dataframe
                status_columns = [col for col in pivot_table_df.columns 
                                 if col not in ['Service', 'Type', 'Leads']]
                
                # Define priority order for status columns
                status_priority = {
                    'Goaxled': 1,
                    'End To End Conversion': 2,
                    'Follow-up': 3,
                    'Cancelled': 4,
                    'Others': 5,
                    'Idle': 6,
                    'Duplicate': 7
                }
                
                # Sort status columns - existing ones first in priority order, then others alphabetically
                sorted_status = sorted(status_columns, key=lambda x: (
                    status_priority.get(x, 99),  # Default to high number for unprioritized statuses
                    x.lower()  # Secondary sort alphabetically
                ))
                
                desired_order = ['Service', 'Type', 'Leads'] + sorted_status

            elif tab_name == "Person":  # Tab 2
                status_columns = [col for col in pivot_table_df.columns 
                                 if col not in ['Name', 'Leads']]
                
                status_priority = {
                    'Goaxled': 1,
                    'End To End Conversion': 2,
                    'Follow-up': 3,
                    'Cancelled': 4,
                    'Others': 5,
                    'Idle': 6,
                    'Duplicate': 7
                }
                
                sorted_status = sorted(status_columns, key=lambda x: (
                    status_priority.get(x, 99),
                    x.lower()
                ))
                
                desired_order = ['Name', 'Leads'] + sorted_status

            elif tab_name == "Source":  # Tab 3
                status_columns = [col for col in pivot_table_df.columns 
                                 if col not in ['Source', 'Leads']]
                
                status_priority = {
                    'Goaxled': 1,
                    'End To End Conversion': 2,
                    'Follow-up': 3,
                    'Cancelled': 4,
                    'Others': 5,
                    'Idle': 6,
                    'Duplicate': 7
                }
                
                sorted_status = sorted(status_columns, key=lambda x: (
                    status_priority.get(x, 99),
                    x.lower()
                ))
                
                desired_order = ['Source', 'Leads'] + sorted_status
            else:
                desired_order = pivot_table_df.columns.tolist()

            # Safely reorder columns - only include columns that exist
            existing_columns = [col for col in desired_order if col in pivot_table_df.columns]
            pivot_table_df = pivot_table_df[existing_columns]
            
            # Convert the pivot table to HTML
            pivot_table_html = pivot_table_df.to_html(index=False, escape=False, classes="styled-table")

            # Custom CSS to style the table and hide the index column
            custom_css = """
            <style>
                .styled-table {
                    width: 100% !important;
                    display: block !important;
                    overflow-x: auto !important; /* Enable horizontal scrolling only when needed */
                    margin: 1rem 0;
                    font-size: 15px;
                    border: none !important;
                    border-collapse: collapse !important; /* Ensure no gaps between cells */
                    margin-top: -75px !important;
                    }

                .styled-table th {
                    padding: 12px !important;
                    text-align: center;
                    background-color: #F8FAFF !important;
                    color: #464B7C !important;
                    border: none !important; /* Remove all borders in header */
                    }

                .styled-table td {
                    padding: 10px !important;
                    text-align: center;
                    border-top: none !important;
                    border-bottom: none !important;
                    border-right: none !important; /* Remove vertical column lines */
                    }
                
                .styled-table tbody tr:nth-child(even) {
                    background-color: rgba(0, 0, 0, 0.01) !important;
                    }

                .styled-table tbody tr:last-child td {
                    background-color: rgba(97, 98, 100, 0.1) !important;
                    color: #464B7C !important;
                    font-weight: bold !important;
                    border-bottom: none !important; /* Remove bottom border for total row */
                    }

                .styled-table th:first-child,
                .styled-table td:first-child {
                    display: none; /* Hide the first column (index) */
                    }
                /* Add vertical line to last column with header row color */
                .styled-table td:last-child,
                .styled-table th:last-child {
                    border-right: 1px solid #D1D5DB !important; /* Adjust the color to match your first visible column */
                    border-bottom: 1px solid #D1D5DB !important; /* Adjust the color to match your first visible column */

                    }
            </style>
            """


            # Combine the custom CSS and the HTML table
            full_html = f"{custom_css}\n{pivot_table_html}"

            # Display the styled table in Streamlit
            st.markdown(full_html, unsafe_allow_html=True)


    st.markdown('<p style="font-weight: bold; margin-bottom: 10px; font-size: 22px;">Conversion Core</p>', unsafe_allow_html=True)
    # Create tabs for different pivot tables
    tab1, tab2, tab3, tab4 = st.tabs(["Service", "Person", "Source", "Non Conversion"])

    # Display pivot tables
    display_pivot_table(
        tab1, "", df_filtered,
        index_cols=['master_service', 'vehicle_type'],
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
        
        
