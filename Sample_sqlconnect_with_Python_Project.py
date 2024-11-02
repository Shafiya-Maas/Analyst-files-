import mysql.connector
import warnings
import pandas as pd
import numpy as np
import streamlit as st 
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

# Local database connection details
db_host = 'localhost'
db_user = 'root'
db_password = 'Year@2024'
db_name = 'world'

# Connect to MySQL database with error handling
try:
    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_password,
        database=db_name,
        use_pure=True
    )
    cur = db.cursor()
    query = """SELECT * FROM city"""
    cur.execute(query)
    result = cur.fetchall()

    # Load data into a DataFrame
    df = pd.DataFrame(result, columns=[desc[0] for desc in cur.description])

    cur.close()
    db.close()
except mysql.connector.Error as err:
    st.error(f"Error: {err}")
    st.stop()

# Set page configuration
st.set_page_config(page_title="Sample SQL connect with Python", page_icon=":bar_chart:", layout="wide")

# Title
st.title("📊 City Population Census")

# Sidebar filter for District
all_districts = df["District"].unique()
selected_districts = st.sidebar.multiselect(
    "Select Districts (Choose an option)",
    options=all_districts,
    default=None  # Show "Choose an option" initially
)

# Filter the DataFrame based on selected District values or show all if none selected
filtered_df = df[df["District"].isin(selected_districts)] if selected_districts else df

# KPIs
total_population = filtered_df["Population"].sum()
average_population = filtered_df["Population"].mean()
num_districts = filtered_df["District"].nunique()

# Custom function for KPI with background color
def display_kpi(label, value, background_color):
    st.markdown(
        f"""
        <div style="background-color: {background_color}; padding: 10px; border-radius: 8px; text-align: center;">
            <h4 style="color: white;">{label}</h4>
            <p style="font-size: 24px; font-weight: bold; color: white;">{value}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Display KPIs
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    display_kpi("Total Population", f"{total_population:,}", "#4CAF50")  # Green background

with kpi2:
    display_kpi("Average Population per District", f"{average_population:,.2f}", "#2196F3")  # Blue background

with kpi3:
    display_kpi("Number of Districts", num_districts, "#FF5722")  # Orange background

# Create pivot table
pivot_table = filtered_df.pivot_table(index='District', values='Population', aggfunc='sum', fill_value=0)

# Creating two columns for layout
col1, col2 = st.columns(2)

# Display the pivot table in the left column
with col1:
    st.write("### Population by District")
    st.dataframe(pivot_table)

# Plotting charts in the right column
with col2:
    st.write("### Population Plots by District")
    
    # Bar Chart
    fig1, ax1 = plt.subplots()
    sns.barplot(x=pivot_table.index, y="Population", data=pivot_table.reset_index(), ax=ax1, palette="viridis")
    ax1.set_xlabel("District")
    ax1.set_ylabel("Population")
    ax1.set_title("Population by District (Bar Chart)")
    plt.xticks(rotation=90)
    st.pyplot(fig1)

    # Line Plot
    fig2, ax2 = plt.subplots()
    sns.lineplot(x=pivot_table.index, y="Population", data=pivot_table.reset_index(), ax=ax2, marker='o')
    ax2.set_xlabel("District")
    ax2.set_ylabel("Population")
    ax2.set_title("Population by District (Line Plot)")
    plt.xticks(rotation=90)
    st.pyplot(fig2)

    # Pie Chart
    fig3, ax3 = plt.subplots()
    ax3.pie(pivot_table['Population'], labels=pivot_table.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("viridis", len(pivot_table)))
    ax3.set_title("Population Distribution by District (Pie Chart)")
    st.pyplot(fig3)
