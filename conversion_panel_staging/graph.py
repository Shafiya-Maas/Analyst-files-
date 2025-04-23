from dependencies import*
from utils import fetch_data_once


def run():
    # Custom CSS Styling
    st.markdown("""
    <style>
    .block-container {
        max-width: 1200px !important;
        padding-top: 0 !important;
        margin-top: -50px!important;
        overflow: auto !important;
    }
    header {
        visibility: hidden;
    }
    .stDeployButton {
        visibility: hidden;
    }
    .st-emotion-cache-1v0mbdj {
        overflow: hidden !important;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .stPlotlyChart {
        margin-top: -20px !important;
        margin-bottom: -20px !important;
        width: 100% !important;
        height: 100% !important;
    }
    .stPlotlyChart svg {
        max-height: none !important;
        height: 100% !important;
    }
    .stMultiSelect > div {
        max-width: 200px !important;
        min-width: 200px !important;
        overflow-y: auto !important;
        max-height: 50px !important;
        white-space: nowrap !important;
        text-overflow: ellipsis !important;
        padding: 0px -100px;
    }
    
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
    .metric-box {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMetric {
        font-family: sans-serif;
        margin: 0 !important;
        padding: 0 !important;
    }
    .stMetric > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    .stMetric label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
        margin-bottom: 5px !important;
    }
    .stMetric value {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #2c3e50 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    def create_metric_box(col, value, label, color):
        with col:
            box = f"""
            <div class="metric-box" style="background-color: {color}; height: 100%;">
                <div class="stMetric">
                    <div>
                        <label>{label}</label>
                        <value>{value}</value>
                    </div>
                </div>
            </div>
            """
            st.markdown(box, unsafe_allow_html=True)

    # Add spacing at the top
    st.write("")
    st.write("")


    # Show loading spinner while fetching data
    with st.spinner('Loading home page...'):
        # To this (if it returns two DataFrames):
        df, feedback_df = fetch_data_once()

    # st.dataframe(df)
    
    
    
    def get_week_dates():
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday() + 1)  # Sunday
        return [start_of_week + timedelta(days=i) for i in range(7)]  # Sunday to Saturday

    # Data Preparation
    df['Dates'] = pd.to_datetime(df['booking_date'], format='mixed', dayfirst=True, errors='coerce').dt.date
    if feedback_df is not None:
        feedback_df['b2b_log'] = pd.to_datetime(feedback_df['b2b_log'], errors='coerce').dt.date

    # Ensure required columns exist
    if 'Activity_Status_Final' not in df.columns:
        df['Activity_Status_Final'] = 'Unknown Status'
        
    if 'new_status' not in df.columns:
        df['new_status'] = 'Unknown Status'
        
    today = date.today()
    if 'initial_load' not in st.session_state:
        st.session_state.initial_load = True
        st.session_state.city_multiselect = []  # Make sure this is a list
        st.session_state.service_multiselect = []  # Make sure this is a list
        st.session_state.source_multiselect = []  # Make sure this is a list

    # Create filters
    col1, col2, col3, col4, col5 = st.columns(5)

    # Combine unique values from both DataFrames for each filter
    all_cities = sorted(set(df['city'].unique().tolist() + 
                           (feedback_df['g_city'].unique().tolist() 
                            if feedback_df is not None and 'g_city' in feedback_df.columns 
                            else [])))

    all_master_service = sorted(set(df['master_service'].unique().tolist() + 
                                  (feedback_df['ms_master_service'].unique().tolist() 
                                   if feedback_df is not None and 'ms_master_service' in feedback_df.columns 
                                   else [])))

    all_sources = sorted(set(df['user_source'].unique().tolist() + 
                            (feedback_df['g_source'].unique().tolist() 
                             if feedback_df is not None and 'g_source' in feedback_df.columns 
                             else [])))

    # City filter (col1)
    with col1:
        if 'city' in df.columns or (feedback_df is not None and 'g_city' in feedback_df.columns):
            df['city'] = df['city'].astype(str) if 'city' in df.columns else None
            selected_city = st.multiselect(
                "City",
                all_cities,
                default=[],
                key="city_multiselect"
            )
        else:
            selected_service = []


    # Service Type filter (col2)
    with col2:
        if 'master_service' in df.columns or (feedback_df is not None and 'ms_master_service' in feedback_df.columns):
            df['master_service'] = df['master_service'].astype(str) if 'master_service' in df.columns else None
            selected_service = st.multiselect(
                "Master Service",
                all_master_service,
                default=[],
                key="service_multiselect"
            )
        else:
            selected_service = []

    # Source filter (col3)
    with col3:
        if 'user_source' in df.columns or (feedback_df is not None and 'g_source' in feedback_df.columns):
            df['user_source'] = df['user_source'].astype(str) if 'user_source' in df.columns else None
            selected_source = st.multiselect(
                "Source",
                all_sources,
                default=[],
                key="source_multiselect"
            )
        else:
            selected_source = []

    # Apply filters to both DataFrames
    filtered_df = df.copy()
    filtered_feedback = feedback_df.copy() if feedback_df is not None else None

    # Apply city filter
    if st.session_state.city_multiselect:
        filtered_df = filtered_df[filtered_df['city'].isin(st.session_state.city_multiselect)]
        if feedback_df is not None and 'g_city' in feedback_df.columns:
            filtered_feedback = filtered_feedback[filtered_feedback['g_city'].isin(st.session_state.city_multiselect)]

    # Apply service type filter
    if st.session_state.service_multiselect:
        if 'master_service' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['master_service'].isin(st.session_state.service_multiselect)]
        if feedback_df is not None and 'ms_master_service' in feedback_df.columns:
            filtered_feedback = filtered_feedback[filtered_feedback['ms_master_service'].isin(st.session_state.service_multiselect)]

    # Apply source filter
    if st.session_state.source_multiselect:
        if 'user_source' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['user_source'].isin(st.session_state.source_multiselect)]
        if feedback_df is not None and 'g_source' in feedback_df.columns:
            filtered_feedback = filtered_feedback[filtered_feedback['g_source'].isin(st.session_state.source_multiselect)]
            
            
    def clear_multi():
        st.session_state.start_date_input = date.today() - timedelta(days=7)
        st.session_state.end_date_input = date.today()
        st.session_state.city_multiselect = []  # Make sure this is a list
        st.session_state.service_multiselect = []  # Add these if needed
        st.session_state.source_multiselect = []  # Add these if needed
            
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Clear filters", on_click=clear_multi)
            
    with col5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Refresh🔄", key="refresh_button"):
            fetch_data_once(force_refresh=True)        
            st.rerun()
    st.markdown("<hr style='margin: 0; padding: 0;'>", unsafe_allow_html=True)   


    st.markdown("<hr style='margin: 0; padding: 0;'>", unsafe_allow_html=True)

    # Calculate metrics for bookings based on filtered data
    today_bookings = len(filtered_df[filtered_df['Dates'] == today])
    this_week_dates = get_week_dates()
    this_week_bookings = len(filtered_df[filtered_df['Dates'].isin(this_week_dates)])
    this_month_start = date(today.year, today.month, 1)
    this_month_bookings = len(filtered_df[filtered_df['Dates'] >= this_month_start])

    # Calculate metrics for check-ins
    today_check_ins = len(filtered_feedback[filtered_feedback['b2b_log'] == today]) if feedback_df is not None else 0
    this_week_check_ins = len(filtered_feedback[filtered_feedback['b2b_log'].isin(this_week_dates)]) if feedback_df is not None else 0
    this_month_check_ins = len(filtered_feedback[filtered_feedback['b2b_log'] >= this_month_start]) if feedback_df is not None else 0

    # Metrics Section
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        create_metric_box(col1, today_bookings, "Today's Bookings", "#e3f2fd")
    with col2:
        create_metric_box(col2, this_week_bookings, "Weekly Bookings", "#e8f5e9")
    with col3:
        create_metric_box(col3, this_month_bookings, "Monthly Bookings", "#fff8e1")
    with col4:
        create_metric_box(col4, today_check_ins, "Today's Check-Ins", "#fce4ec")
    with col5:
        create_metric_box(col5, this_week_check_ins, "Weekly Check-Ins", "#e8eaf6")
    with col6:
        create_metric_box(col6, this_month_check_ins, "Monthly Check-Ins", "#e0f7fa")

    # Define conversion types
    non_conversion_types = {
        "Cancelled": "Activity_Status_Final == 'Cancelled Booking'",
        "Other Booking": "Activity_Status_Final == 'Other Booking'",
    }

    # Conversion Analysis Section
    conv_data = []
    for date_val in filtered_df['Dates'].unique():
        date_df = filtered_df[filtered_df['Dates'] == date_val]
        total = len(date_df)
        for source in date_df['user_source'].unique():
            source_df = date_df[date_df['user_source'] == source]
            non_conv_count = sum(len(source_df.query(cond)) for cond in non_conversion_types.values())
            conv_count = len(source_df) - non_conv_count
            conv_data.append({
                'Date': str(date_val),
                'Source': source,
                'Type': 'Conversion',
                'Count': conv_count,
                'Percentage': (conv_count / len(source_df)) * 100 if len(source_df) > 0 else 0
            })
            conv_data.append({
                'Date': str(date_val),
                'Source': source,
                'Type': 'Non-Conversion',
                'Count': non_conv_count,
                'Percentage': (non_conv_count / len(source_df)) * 100 if len(source_df) > 0 else 0
            })
    conv_df = pd.DataFrame(conv_data)

    # Non-Conversion Breakdown
    non_conv_breakdown = []
    for date_val in filtered_df['Dates'].unique():
        date_df = filtered_df[filtered_df['Dates'] == date_val]
        for name, cond in non_conversion_types.items():
            count = len(date_df.query(cond))
            non_conv_breakdown.append({
                'Date': str(date_val),
                'Non-Conversion Type': name,
                'Count': count,
                'Percentage': (count / len(date_df)) * 100 if len(date_df) > 0 else 0
            })
    non_conv_df = pd.DataFrame(non_conv_breakdown)

    # Get yesterday and today's dates
    yesterday = today - timedelta(days=1)
    recent_dates = [d for d in [yesterday, today] if d in filtered_df['Dates'].unique()]
    recent_data = filtered_df[filtered_df['Dates'].isin(recent_dates)]

    # Weekly Booking Analysis - Sunday to Saturday
    current_week_dates = get_week_dates()
    start_of_week = current_week_dates[0]
    end_of_week = current_week_dates[-1]

    col1, col2 = st.columns(2)

    with col1:
        # Graph 1: Bookings Trend (now as bar chart)
        service_this_week = filtered_df[filtered_df['Dates'].isin(current_week_dates)]
        service_counts = service_this_week.groupby('Dates').size().reset_index(name='Count')
        service_counts['Day'] = pd.to_datetime(service_counts['Dates']).dt.strftime('%a, %b %d') # Format without time
        
        fig2 = px.bar(
            service_counts,
            x='Day',
            y='Count',
            title=f"Bookings Weekly Chart",
            text='Count',
            color='Count',
            color_continuous_scale='Blues'
        )
        fig2.update_traces(
            textposition="outside",
            marker=dict(line=dict(width=1, color='DarkSlateGrey'))
        )
        # Calculate appropriate y-axis range
        max_count = service_counts['Count'].max()
        y_upper = max_count * 1.2  # Add 25% padding at the top
        
        fig2.update_layout(
            height=350,
            margin=dict(t=50, b=20, l=20, r=20, pad=10),  # Added padding
            xaxis_title="Date",
            yaxis_title="Number of Bookings",
            hovermode="x unified",
            showlegend=False,
            coloraxis_showscale=False,
            yaxis=dict(range=[0, y_upper])  # Set dynamic y-axis range
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Graph 2: Check-Ins Trend (now as bar chart)
        if feedback_df is not None:
            feedback_this_week = filtered_feedback[
                (filtered_feedback['b2b_log'] >= start_of_week) &
                (filtered_feedback['b2b_log'] <= end_of_week)
            ]
            feedback_counts = feedback_this_week['b2b_log'].value_counts().sort_index().reset_index()
            feedback_counts.columns = ['Date', 'Count']
            feedback_counts['Day'] = pd.to_datetime(feedback_counts['Date']).dt.strftime('%a, %b %d') # Format without time
            
            fig1 = px.bar(
                feedback_counts,
                x='Day',
                y='Count',
                title=f"Check-Ins Weekly Chart",
                text='Count',
                color='Count',
                color_continuous_scale='Greens'
            )
            fig1.update_traces(
                textposition="outside",
                marker=dict(line=dict(width=1, color='DarkSlateGrey'))
            )
            # Calculate appropriate y-axis range
            max_count = feedback_counts['Count'].max()
            y_upper = max_count * 1.2  # Add 25% padding at the top
            
            fig1.update_layout(
                height=350,
                margin=dict(t=40, b=20, l=20, r=20, pad=10),  # Added padding
                xaxis_title="Date",
                yaxis_title="Number of Check-Ins",
                hovermode="x unified",
                showlegend=False,
                coloraxis_showscale=False,
                yaxis=dict(range=[0, y_upper])  # Set dynamic y-axis range
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No feedback data available to display check-ins trend")


