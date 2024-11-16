import mysql.connector
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import streamlit as st 
import matplotlib.pyplot as plt
import seaborn as sns


# Connect to MySQL database
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="Year@2024",
    database="mytvs_fit",
    use_pure=True
)

# Retrieve only necessary columns from the city table
query = """SELECT * FROM vendors limit 100"""
df = pd.read_sql(query, db)

db.close()

# Set page configuration
st.set_page_config(page_title="Sample SQL connect with Python", page_icon=":bar_chart:", layout="wide")

# Title
st.title("📊 City Population Census")