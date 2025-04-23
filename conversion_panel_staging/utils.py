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

def get_db_connection2():
    try:
        creds = config['mysql_dev']
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
    
# Modify your load_parquet function to handle multiple datasets
def load_parquet():
    if st.session_state.refresh_data:
        df1 = fetch_and_save_parquet()
        df2 = load_feedback_data()
        st.session_state.refresh_data = False
    elif os.path.exists("data.parquet") and os.path.exists("data2.parquet"):
        df1 = pd.read_parquet("data.parquet")
        df2 = pd.read_parquet("data2.parquet")
    else:
        df1 = fetch_and_save_parquet()
        df2 = load_feedback_data()
    
    # Save second dataset if it's new
    if not os.path.exists("data2.parquet"):
        df2.to_parquet("data2.parquet", engine="pyarrow", compression="snappy")
    
    return df1, df2


def fetch_and_save_parquet():
    query="""WITH LatestComments AS (
    SELECT user_id, 
           book_id, 
           comments, 
           category, 
           status AS comment_status, 
           log AS comment_log
    FROM admin_comments_tbl ac
    WHERE log = (SELECT MAX(com_id) 
                 FROM admin_comments_tbl ac2 
                 WHERE ac2.book_id = ac.book_id)
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
    ON a.service_type = c.service_type 
    AND a.vehicle_type = c.type
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
WHERE
    DATE(ADDTIME(a.log, '05:30:00'))>= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)
    AND a.mec_id NOT IN (400001, 200018, 200379, 203042, 400974)
    AND a.user_id NOT IN (21816, 41317, 859, 3132, 20666, 56511, 2792, 128, 19, 7176, 19470, 1, 951, 103699, 113453, 108783, 226, 252884, 189598, 133986, 270162, 298572, 287322, 53865, 289516, 14485, 1678, 30865, 125455, 338469, 9570, 388733, 276771, 392833, 378368, 309341, 299526, 304771, 1935, 22115, 44794, 1031939, 639065, 662228, 965020, 804253, 722759, 378258, 1088113, 1165855, 1165488, 1133076, 1288252, 304783)
    AND a.source NOT IN ('Sulekha Booking', 'Sbi Bookings', 'BTL Booking', 'RSA Bookings', 'nmsa_web', 'Uber')
    AND e.user_source NOT IN ('Re-Engagement Bookings')
    AND a.service_type NOT IN ('Breakdown Assistance', 'Bike Tyre Puncture', 'Car Tyre Puncture', 'Flat Tyre Assistance', 'Vehicle Towing', 'Puncture', 'Towing', 'Bike Breakdown', 'Bike Puncture', 'Deep Clean', 'IOCL Check-up')
	AND a.nmsa_flag != 1
    AND a.flag_unwntd != 1;

     """

    db = get_db_connection()
    if db:
        try:
            df = pd.read_sql(query, db)
            df.fillna("") # Replace NaN with empty string to avoid issues
                
            for col in df.select_dtypes(include=['object']).columns:
                df[col]=df[col].astype(str)

            df.to_parquet("data.parquet", engine="pyarrow", compression="snappy")
            return df
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return pd.DataFrame()
        else:        
            return pd.DataFrame()
        

 # Add this new function for your second query
def load_feedback_data():
    query = """WITH LatestBookings AS (
	SELECT DISTINCT
        b.gb_booking_id,
        b.b2b_vehicle_type,
        b.b2b_swap_flag,
        b.b2b_service_type,
        g.booking_id AS g_booking_id,
        g.mec_id,
        g.vehicle_type AS g_vehicle_type,
        g.service_type AS g_service_type,
        g.status AS g_status,
        g.flag AS g_flag,
        g.booking_status AS g_booking_status,
        g.source AS g_source,
        g.log AS g_log,
        g.axle_flag AS g_axle_flag,
        g.city AS g_city,
        g.locality,
        g.flag_unwntd AS g_flag_unwntd,
        g.flag_duplicate,
        g.service_status AS g_service_status,
        f.b2b_booking_id,
        f.city AS f_city,
        f.veh_type,
        f.service_type AS f_service_type,
        f.service_status AS f_service_status,
        f.crm_goaxle_id,
        f.log AS f_log,
        s.b2b_acpt_flag,
        cm.crm_log_id,
        cm.name AS cm_name,
        cm.flag AS cm_flag,
        cm.crm_flag,
        cm.cre_flag,
        c.b2b_log,
        ms.master_service AS ms_master_service

    FROM
        b2b.b2b_booking_tbl AS b
            LEFT JOIN go_bumpr.user_booking_tb AS g ON b.gb_booking_id = g.booking_id
            LEFT JOIN go_bumpr.go_axle_service_price_tbl AS ms ON ms.service_type = g.service_type AND g.vehicle_type = ms.type
            LEFT JOIN go_bumpr.feedback_track AS f ON f.b2b_booking_id = b.b2b_booking_id
            JOIN b2b.b2b_status s ON s.b2b_booking_id = b.b2b_booking_id
            LEFT JOIN go_bumpr.crm_admin cm ON cm.crm_log_id = f.crm_goaxle_id
            LEFT JOIN b2b.b2b_mec_tbl AS m ON m.b2b_shop_id = b.b2b_shop_id
            LEFT JOIN b2b.b2b_checkin_report AS c ON b.b2b_booking_id = c.b2b_booking_id
WHERE 
(
    (c.b2b_log >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)
     AND b.b2b_swap_flag = 0
     AND b.b2b_check_in_report = 1)
    OR
    (g.service_status IN ('Completed', 'inprogress')
     AND g.booking_status = 2
     AND g.axle_flag = 1
     AND g.flag_unwntd = 1)
)

)
SELECT * FROM LatestBookings;
"""
    
    db = get_db_connection()
    if db:
        try:
            df = pd.read_sql(query, db)
            df.fillna("") # Replace NaN with empty string
                
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str)

            return df
        except Exception as e:
            st.error(f"Error executing second query: {e}")
            return pd.DataFrame()
    return pd.DataFrame()


# Modify your fetch_data_once function
def fetch_data_once(force_refresh=False):
    if force_refresh or "shared_df" not in st.session_state or "shared_df2" not in st.session_state:
        st.session_state.shared_df = fetch_and_save_parquet()
        st.session_state.shared_df2 = load_feedback_data()
        st.session_state.last_refreshed = pd.Timestamp.now()
    return st.session_state.shared_df, st.session_state.shared_df2

# Update your main code to handle both datasets
df1, df2 = load_parquet()
# Or if using fetch_data_once:
# df1, df2 = fetch_data_once()       