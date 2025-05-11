# Add to top of your app
st.set_page_config(
    page_title="Pharma Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add clear instructions
st.sidebar.markdown("""
**How to Use:**
1. Type a drug name (e.g., Ibuprofen)
2. View results from 10+ medical APIs
3. No login required - completely free!
""")