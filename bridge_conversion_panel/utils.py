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


@st.cache_data(ttl=5)
def fetching_core_dashboard_panel( start_date=None, end_date=None):
    return fetch_core_data(start_date=start_date, end_date=end_date)



def fetch_core_data(start_date=None, end_date=None):
    if start_date and end_date:
        # Convert strings to datetime and subtract 5.5 hours
        start = (pd.to_datetime(start_date) - timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        end = (pd.to_datetime(end_date) - timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        # Default to last 3 months
        current = datetime.now() - timedelta(hours=5, minutes=30)
        three_months_ago = current - pd.DateOffset(months=3)
        start = three_months_ago.strftime('%Y-%m-%d %H:%M:%S')
        end = current.strftime('%Y-%m-%d %H:%M:%S')

    date_condition = f"AND DATE(ADDTIME(a.log, '05:30:00')) BETWEEN '{start}' AND '{end}'"

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
    SELECT DISTINCT
        a.booking_id,
        CONCAT(
            UPPER(LEFT(TRIM(a.vehicle_type), 1)),
            LOWER(SUBSTRING(TRIM(a.vehicle_type), 2))
        )as vehicle_type,
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
             df.fillna(0, inplace=True)
             return df
         except Exception as e:
             st.error(f"Error executing query: {e}")
             return df
         
         finally:
             db.close()
             
    return pd.DataFrame()


if "dashboard1_cache" not in st.session_state:
        st.session_state["dashboard1_cache"] = fetching_core_dashboard_panel()
        
df = st.session_state.get("dashboard1_cache", pd.DataFrame())


        
        


        