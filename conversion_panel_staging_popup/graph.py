from dependencies import*
from utils import *
from feedbackquery import *


def run():
    
    if 'refresh_data' not in st.session_state:
        st.session_state.refresh_data = False
        
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
    /*graph alignment */
    .st-emotion-cache-ocqkz7 {
    align-items: anchor-center;
    text-align: left;
    margin-bottom: 22px;
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
        df = load_parquet()
        feedback_df = load_parquet2()

    #st.dataframe(df)
    #st.dataframe(feedback_df)
    
    
    
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
            st.session_state.refresh_data = True  # This will trigger load_parquet2() to refresh
            #fetch_data_once(force_refresh=True)        
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
            height=300,
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
                height=300,
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
        
        st.write("")
        st.write("")
        
        
    col1, col2 = st.columns(2)

    with col1:
        # Graph 3: MTD Bookings Trend (Line Chart) with labels
        if filtered_df is not None:
            month_start = date(today.year, today.month, 1)
            month_dates = pd.date_range(month_start, today)
            
            # Get bookings by date
            bookings_mtd = filtered_df.copy()
            bookings_mtd['Dates'] = pd.to_datetime(bookings_mtd['Dates'])
            bookings_mtd = bookings_mtd[bookings_mtd['Dates'].isin(month_dates)]
            bookings_by_date = bookings_mtd['Dates'].value_counts().sort_index().reset_index()
            bookings_by_date.columns = ['Date', 'Count']
            bookings_by_date['Date'] = pd.to_datetime(bookings_by_date['Date'])
            
            # Create line chart with enhanced labels
            fig3 = go.Figure()
            
            # Add line trace with markers and labels
            fig3.add_trace(go.Scatter(
                x=bookings_by_date['Date'],
                y=bookings_by_date['Count'],
                mode='lines+markers+text',
                name='Bookings',
                line=dict(width=3, color='#1f77b4'),
                marker=dict(size=10, color='#1f77b4'),
                text=bookings_by_date['Count'],
                textposition='top center',
                textfont=dict(
                    size=12,
                    color='#1f77b4'
                ),
                hovertemplate='Date: %{x|%b %d}<br>Bookings: %{y}<extra></extra>'
            ))
            
            # Add styling
            fig3.update_layout(
                title='MTD Bookings Trend',
                height=350,
                margin=dict(t=50, b=20, l=20, r=20, pad=10),
                xaxis_title="Date",
                yaxis_title="Number of New Bookings",
                hovermode="x unified",
                showlegend=False,
                yaxis=dict(
                    rangemode='tozero',
                    zeroline=True,
                    zerolinewidth=1,
                    zerolinecolor='#ccc'
                )
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("No booking data available for MTD trends")

    with col2:
        # Graph 4: MTD Check-Ins Trend (Line Chart) with labels
        if filtered_feedback is not None:
            month_start = date(today.year, today.month, 1)
            month_dates = pd.date_range(month_start, today)
            
            # Get check-ins by date
            checkins_mtd = filtered_feedback.copy()
            checkins_mtd['b2b_log'] = pd.to_datetime(checkins_mtd['b2b_log'])
            checkins_mtd = checkins_mtd[checkins_mtd['b2b_log'].isin(month_dates)]
            checkins_by_date = checkins_mtd['b2b_log'].value_counts().sort_index().reset_index()
            checkins_by_date.columns = ['Date', 'Count']
            checkins_by_date['Date'] = pd.to_datetime(checkins_by_date['Date'])
            
            # Create line chart with enhanced labels
            fig4 = go.Figure()
            
            # Add line trace with markers and labels
            fig4.add_trace(go.Scatter(
                x=checkins_by_date['Date'],
                y=checkins_by_date['Count'],
                mode='lines+markers+text',
                name='Check-Ins',
                line=dict(width=3, color='#2ca02c'),
                marker=dict(size=10, color='#2ca02c'),
                text=checkins_by_date['Count'],
                textposition='top center',
                textfont=dict(
                    size=12,
                    color='#2ca02c'
                ),
                hovertemplate='Date: %{x|%b %d}<br>Check-Ins: %{y}<extra></extra>'
            ))
            
            # Add styling
            fig4.update_layout(
                title='MTD Check-Ins Trend',
                height=350,
                margin=dict(t=50, b=20, l=20, r=20, pad=10),
                xaxis_title="Date",
                yaxis_title="Number of New Check-Ins",
                hovermode="x unified",
                showlegend=False,
                yaxis=dict(
                    rangemode='tozero',
                    zeroline=True,
                    zerolinewidth=1,
                    zerolinecolor='#ccc'
                )
            )
            
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("No feedback data available for MTD check-ins")



    st.write("")
    st.write("")

    # Create clean executive performance heatmap
    if filtered_df is not None and 'crm_admin_name' in filtered_df.columns:
        # Create monthly data
        month_start = date(today.year, today.month, 1)
        month_dates = pd.date_range(month_start, today)
        
        # Get bookings by date and executive
        bookings_mtd = filtered_df.copy()
        bookings_mtd['Dates'] = pd.to_datetime(bookings_mtd['Dates'])
        bookings_mtd = bookings_mtd[bookings_mtd['Dates'].isin(month_dates)]
        
        # Clean executive names
        bookings_mtd['crm_admin_name'] = bookings_mtd['crm_admin_name'].str.strip()
        
        # Create pivot table
        executive_heatmap = pd.pivot_table(
            bookings_mtd,
            values='booking_id',
            index=pd.Grouper(key='Dates', freq='D'),
            columns='crm_admin_name',
            aggfunc='count',
            fill_value=0
        ).reset_index()
        
        # Sort executives by total bookings
        executive_totals = executive_heatmap.iloc[:, 1:].sum().sort_values(ascending=False)
        executive_heatmap = executive_heatmap[['Dates'] + executive_totals.index.tolist()]
        
        # Create heatmap with light colorscale
        fig_exec_heatmap = go.Figure(data=go.Heatmap(
            z=executive_heatmap.iloc[:, 1:].values,
            x=executive_heatmap.columns[1:],
            y=executive_heatmap['Dates'].dt.strftime('%b %d'),
            colorscale='YlOrRd',  # Light yellow-orange-red
            text=executive_heatmap.iloc[:, 1:].values,
            texttemplate='%{text}',
            hovertemplate='<b>%{x}</b><br>%{y}<br>Bookings: %{text}<extra></extra>',
            colorbar=dict(
                title='Bookings',
                titleside='right'
            )
        ))
        
        # Clean layout
        fig_exec_heatmap.update_layout(
            title='Executive MTD Bookings',
            height=600,
            xaxis_title="Executive",
            yaxis_title="Date",
            margin=dict(l=80, r=50, t=80, b=100),
            xaxis=dict(
                tickangle=45,
                tickfont=dict(size=10)
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12
            )
        )
        
        st.plotly_chart(fig_exec_heatmap, use_container_width=True)
        
    else:
        st.warning("No executive booking data available")
        
    st.write("")
    st.write("")
    
    # Create heatmap for executive check-ins from feedback data
    if filtered_feedback is not None and 'name' in filtered_feedback.columns:
        # Create monthly data
        month_start = date(today.year, today.month, 1)
        month_dates = pd.date_range(month_start, today)
        
        # Get check-ins by date and executive
        feedback_mtd = filtered_feedback.copy()
        feedback_mtd['b2b_log'] = pd.to_datetime(feedback_mtd['b2b_log'])
        feedback_mtd = feedback_mtd[feedback_mtd['b2b_log'].isin(month_dates)]
        
        # Clean executive names
        feedback_mtd['name'] = feedback_mtd['name'].str.strip()
        
        # Create pivot table
        executive_checkins = pd.pivot_table(
            feedback_mtd,
            values='b2b_log',  # Using log ID as count
            index=pd.Grouper(key='b2b_log', freq='D'),
            columns='name',
            aggfunc='count',
            fill_value=0
        ).reset_index()
        
        # Sort executives by total check-ins
        executive_totals = executive_checkins.iloc[:, 1:].sum().sort_values(ascending=False)
        executive_checkins = executive_checkins[['b2b_log'] + executive_totals.index.tolist()]
        
        # Create heatmap with light colorscale
        fig_checkins = go.Figure(data=go.Heatmap(
            z=executive_checkins.iloc[:, 1:].values,
            x=executive_checkins.columns[1:],
            y=executive_checkins['b2b_log'].dt.strftime('%b %d'),
            colorscale='Greens',  # Light green colorscale
            text=executive_checkins.iloc[:, 1:].values,
            texttemplate='%{text}',
            hovertemplate='<b>%{x}</b><br>%{y}<br>Check-ins: %{text}<extra></extra>',
            colorbar=dict(
                title='Check-ins',
                titleside='right'
            )
        ))
        
        # Clean layout
        fig_checkins.update_layout(
            title='Executive  Check-ins',
            height=600,
            xaxis_title="Executive",
            yaxis_title="Date",
            margin=dict(l=80, r=50, t=80, b=100),
            xaxis=dict(
                tickangle=45,
                tickfont=dict(size=10)
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12
            )
        )
        
        st.plotly_chart(fig_checkins, use_container_width=True)
        
    else:
        st.warning("No executive check-in data available in feedback file")


