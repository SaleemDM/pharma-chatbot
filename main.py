# 1. IMPORTS FIRST (ALWAYS AT TOP)
import streamlit as st
import requests
import wikipedia
from datetime import datetime, timedelta

# 2. PAGE CONFIG (RIGHT AFTER IMPORTS)
st.set_page_config(
    page_title="Pharma Chatbot",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. CACHE SETUP
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_rxnav_info(drug_name):
    # Your existing RxNav function code
    ...

# 4. MAIN APP CODE
def main():
    st.title("💊 Pharma Chatbot")
    drug_query = st.text_input("Enter drug name:")
    
    if drug_query:
        # Rest of your app logic
        ...

if __name__ == "__main__":
    main()
