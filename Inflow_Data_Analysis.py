# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 14:36:37 2024

@author: K02090
"""

import pandas as pd
import streamlit as st


df = pd.read_csv("D:\\Project 1\\Transaction_Vs_Billing_data (3).csv")
print(df)

# Set page configuration
st.set_page_config(page_title="Inflow Source Data Analysis", page_icon=":bar_chart:", layout="wide")

# Title
st.title("Inflow Source Data Analysis")

