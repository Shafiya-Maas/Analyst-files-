from dependencies import*


# Read database configuration from config.ini
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
    
if 'refresh_data' not in st.session_state:
    st.session_state.refresh_data = False    

def get_db_connection():
    try:
        creds = config['mysql_devcs']
        return mysql.connector.connect(
            host=creds.get('host'),  # Use TCP/IP connection
            user=creds.get('user'),
            passwd=creds.get('password'),
            database=creds.get('database'),
            port=int(creds.get('port')),  # Ensure port is an integer
            use_pure=True
        )
    except mysql.connector.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

@st.cache_data
def load_parquet(start_date=None, end_date=None):
    if st.session_state.refresh_data:
        df = fetch_and_save_parquet(start_date=start_date, end_date=end_date)
        st.session_state.refresh_data = False
    elif os.path.exists("data.parquet"):
        df = pd.read_parquet("data.parquet")
    else:
        df = fetch_and_save_parquet(start_date=start_date, end_date=end_date)
    return df

        
def fetch_and_save_parquet(start_date=None, end_date=None):
    
    if start_date and end_date:
        date_condition = f"AND DATE(ADDTIME(a.log, '05:30:00')) BETWEEN '{start_date}' AND '{end_date}'"
    else:
        current_date = pd.to_datetime("today").date()
        three_months_ago = (pd.to_datetime("today") - pd.DateOffset(months=3)).date()
        date_condition = f"AND DATE(ADDTIME(a.log, '05:30:00')) BETWEEN '{three_months_ago}' AND '{current_date}'"

    query = f"""
    WITH LatestComments AS (
        SELECT user_id, 
               book_id, 
               comments, 
               category, 
               status AS comment_status, 
               log AS comment_log
        FROM admin_comments_tbl ac
        WHERE log = (
            SELECT MAX(log)
            FROM admin_comments_tbl ac2 
            WHERE ac2.book_id = ac.book_id
        )
    )
    SELECT  
        a.booking_id,
        a.vehicle_type,
        a.status AS booking_status,
        a.booking_status AS booking_status_code,
        a.axle_flag,
        a.flag,
        a.flag_unwntd,
        a.enquiry_flag,
        a.log AS raw_log_timestamp,
        DATE(ADDTIME(a.log, '05:30:00')) AS booking_date,
        b.b2b_check_in_report,
        b.b2b_swap_flag,
        a.service_status AS service_status_code,
        a.city,
        a.service_type,
        c.master_service,
        d.name AS crm_admin_name,
        e.user_source,
        f.activity AS activity_name,
        a.activity_status AS activity_status_code,
        lc.comments,
        g.b2b_shop_name,
        uv.vehicle_id AS user_vehicle_id,
        a.vech_id,
        uv.id AS vehicle_table_id,
        a.user_veh_id
    FROM go_bumpr.user_booking_tb a
    LEFT JOIN b2b.b2b_booking_tbl b 
        ON a.booking_id = b.gb_booking_id
    LEFT JOIN go_bumpr.go_axle_service_price_tbl c 
        ON a.service_type = c.service_type AND a.vehicle_type = c.type
    LEFT JOIN crm_admin d 
        ON d.crm_log_id = a.crm_update_id
    LEFT JOIN user_vehicle_table uv 
        ON uv.id = a.user_veh_id
    LEFT JOIN go_bumpr.user_source_tbl e 
        ON e.user_source = a.source
    LEFT JOIN go_bumpr.admin_activity_tbl f 
        ON f.id = a.activity_status
    LEFT JOIN b2b.b2b_mec_tbl g 
        ON g.b2b_shop_id = b.b2b_shop_id
    LEFT JOIN LatestComments lc 
        ON a.booking_id = lc.book_id
    WHERE 1=1
        {date_condition}
        AND a.mec_id NOT IN (400001, 200018, 200379, 203042, 400974)
        AND a.user_id NOT IN (21816, 41317, 859, 3132, 20666, 56511, 2792, 128, 19, 7176, 19470, 1, 951, 103699, 113453, 108783, 226, 252884, 189598, 133986, 270162, 298572, 287322, 53865, 289516, 14485, 1678, 30865, 125455, 338469, 9570, 388733, 276771, 392833, 378368, 309341, 299526, 304771, 1935, 22115, 44794, 1031939, 639065, 662228, 965020, 804253, 722759, 378258, 1088113, 1165855, 1165488, 1133076, 1288252, 304783)
        AND a.source NOT IN ('Sulekha Booking', 'Sbi Bookings', 'BTL Booking', 'RSA Bookings', 'nmsa_web', 'Uber')
        AND a.service_type NOT IN ('Breakdown Assistance', 'Bike Tyre Puncture', 'Car Tyre Puncture', 'Flat Tyre Assistance', 'Vehicle Towing', 'Puncture', 'Towing', 'Bike Breakdown', 'Bike Puncture', 'Deep Clean', 'IOCL Check-up')
        AND a.nmsa_flag != 1
        AND a.flag_unwntd != 1
    """

    db = get_db_connection()
    if db:
        try:
            df = pd.read_sql(query, db)
            df = df.fillna("")  # Replace NaNs to avoid save issues
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str)
            df.to_parquet("data.parquet", engine="pyarrow", compression="snappy")
            return df
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return pd.DataFrame()

        
        
df = load_parquet()
# st.dataframe(df)  

#Alternative Data Fetching Function
def fetch_data_once(force_refresh=False, start_date=None, end_date=None):
    if force_refresh or "shared_df" not in st.session_state:
        st.session_state.shared_df = fetch_and_save_parquet(start_date=start_date, end_date=end_date)
        st.session_state.last_refreshed = pd.Timestamp.now()
    return st.session_state.shared_df

        