import streamlit as st
from login import login_page
from loss_ratio import dashboard_page
import altair as alt
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Eden Care Loss Ratio Dashboard",
    page_icon=Image.open("logo.png"),
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"

    if st.session_state.current_page == "login":
        login_page()
    elif st.session_state.current_page == "loss_ratio":
        if st.session_state.authenticated:
            dashboard_page()
        else:
            st.session_state.current_page = "login"
            login_page()

if __name__ == "__main__":
    main()
