import streamlit as st

# MUST be the first Streamlit call
st.set_page_config(layout="wide")


from dependencies import *
import core
import graph


# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

def get_db_connection():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
    
    if "mysql_devcsv" not in config:
        raise KeyError("Missing [mysql_devcsv] section in config.ini")

    try:
        creds = config['mysql_devcs']
        connection = mysql.connector.connect(
            host=creds.get('host'),
            user=creds.get('user'),
            passwd=creds.get('password'),
            database=creds.get('database'),
            port=int(creds.get('port')),
            use_pure=True
        )
        return connection
    except mysql.connector.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def authenticate_user(agent_id, password_new):
    db = get_db_connection()
    if db is None:
        return None
    
    try:
        # First check if user exists and has admin_crm=1
        admin_query = """
        SELECT * FROM crm_admin 
        WHERE agent_id = %s AND password_new = %s AND admin_crm = 1
        """
        with db.cursor(dictionary=True) as cursor:
            cursor.execute(admin_query, (agent_id, password_new))
            admin_user = cursor.fetchone()
            
            if admin_user:
                return admin_user
            
            # If no admin user found, check if credentials are correct but not admin
            basic_query = """
            SELECT * FROM crm_admin 
            WHERE agent_id = %s AND password_new = %s
            """
            cursor.execute(basic_query, (agent_id, password_new))
            basic_user = cursor.fetchone()
            
            if basic_user:
                st.error("Access denied: You don't have access to Login")
            else:
                st.error("Invalid username or password")
                
            return None
    except Exception as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        db.close()

def encode_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as file:
            return base64.b64encode(file.read()).decode()
    return None

# Apply CSS styles
st.markdown("""
    <style>
        .block-container { max-width: 100% !important; min-height: 100vh; overflow: hidden !important; padding: 0 !important; margin: 0 !important; }
        header, footer { visibility: hidden; height: 0px; }
        .stButton>button { background-color: #0d6efd; color: white; font-size: 18px; padding: 12px; width: 70%; border: none; border-radius: 5px; cursor: pointer; text-align: center; }
        .stButton>button:hover { background-color: #0056b3; }
        .st-emotion-cache-in76mr {width: 471px; }
        .st-emotion-cache-ocqkz7 { align-items: anchor-center; text-align: left; }
        .st-emotion-cache-ztmtrv { gap: 0rem; }
        
        /* Style for input fields */
        div[data-testid="stTextInput"] {
            width: 70% !important;
            margin: left;
        }
    </style>
""", unsafe_allow_html=True)

def display_login_page():
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        image_path = os.path.join("login", "login_image.png")
        encoded_image = encode_image(image_path)
        if encoded_image:
            st.markdown(
                f"""
                <style>
                    .image-container {{
                        width: 100%;
                        height: 100vh;
                        overflow: hidden;
                        text-align: left;
                    }}
                    .image-container img {{
                        width: 85%;
                        height: 100%;
                        object-fit: fill;
                    }}
                </style>
                <div class="image-container">
                    <img src="data:image/png;base64,{encoded_image}" />
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error("Login image not found!")

    with col2:
        logo_path = "logo/mytvs-logo.webp"
        new_logo_path = "logo/mytvs-logo.png"

        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img.save(new_logo_path, "PNG")

        image_base64 = encode_image(new_logo_path)
        if image_base64:
            st.markdown(f"""
                <div style='text-align: left; margin-left:0rem;'>
                    <h1><img src="data:image/png;base64,{image_base64}" width='150'></h1>
                    <h2>LOGIN</h2>
                </div>
            """, unsafe_allow_html=True)
            
        username = st.text_input("Username", key="username_input", placeholder="Enter User Name")
        password = st.text_input("Password", type="password", key="password_input", placeholder="Enter Password")
        
        with st.container():
            col3, col4 = st.columns([1, 1])
            with col3:
                st.markdown("<div style='text-align: left;'><input type='checkbox' id='remember_me'> <label for='remember_me'>Remember Me</label></div>", unsafe_allow_html=True)
            with col4:
                st.markdown("<div style='text-align: left;'><a href='#' style='text-decoration: none;'>Forgot password?</a></div>", unsafe_allow_html=True)

        if st.button("Login"):
            user = authenticate_user(username, password)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["user"] = user
                st.session_state["current_page"] = "Home"
                st.success("Login Successful! Redirecting...")
                st.rerun()

def logout():
    if "db_connection" in st.session_state and st.session_state["db_connection"]:
        st.session_state["db_connection"].close()

    keys_to_clear = ["authenticated", "user", "user_type", "db_connection", "current_page"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.clear()        
    st.cache_data.clear()
    
    if os.path.exists("data.parquet"):
        os.remove("data.parquet")

    st.rerun()

# Main application logic
if not st.session_state["authenticated"]:
    display_login_page()
    st.stop()

# Display sidebar and navigation for authenticated users
if st.session_state["authenticated"] and st.session_state["user"] is not None:
    st.sidebar.write(f"Logged in as: {st.session_state['user']['agent_id']}")
    
    st.session_state["current_page"] = st.sidebar.radio(
        "Navigation",
        ["Home", "Core Conversion Panel"],
        index=0 if st.session_state["current_page"] == "Home" else 1
    ) 

    if st.sidebar.button("Logout"):
        logout()

# Display the selected page
if st.session_state["current_page"] == "Home":
    graph.run()
elif st.session_state["current_page"] == "Core Conversion Panel":
    core.run()