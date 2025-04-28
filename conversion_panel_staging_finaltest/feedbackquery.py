from dependencies import*


# Read database configuration from config.ini
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
    
if 'refresh_data' not in st.session_state:
    st.session_state.refresh_data = False    

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

def load_parquet2():
    if st.session_state.refresh_data:
        df = load_feedback_data()
        st.session_state.refresh_data = False
    elif os.path.exists("data2.parquet"):
        df = pd.read_parquet("data2.parquet")
    else:
        df = load_feedback_data()
    return df        
        

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
	 (b.b2b_swap_flag = 0
     AND b.b2b_check_in_report = 1
     AND g.booking_status = 2
     AND g.axle_flag = 1
     AND g.flag_unwntd = 1)
     OR
     (g.service_status IN ('Completed', 'inprogress'))
)

)
SELECT * FROM LatestBookings as l Limit 1000;

"""

    db = get_db_connection2()
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
        
df = load_parquet2()
# st.dataframe(df)  


def fetch_data_two(force_refresh=False):
    if force_refresh or "shared_df2" not in st.session_state:
        st.session_state.shared_df2 = load_feedback_data()
        st.session_state.last_refreshed = pd.Timestamp.now()
    return st.session_state.shared_df2
        
