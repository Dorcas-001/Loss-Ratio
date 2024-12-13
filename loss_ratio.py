import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime




# Function to render the dashboard
def dashboard_page():
    st.title("Dashboard")
    st.write("Welcome to the loss ratio dashboard!")
    # Your dashboard code here
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.current_page = "login"



    # SIDEBAR FILTER
    logo_url = 'EC_logo.png'  
    st.sidebar.image(logo_url, use_column_width=True)

    page = st.sidebar.selectbox("Choose a dashboard", ["Home", "Overview for Expected Claims","Overview for Actual Claims", "Loss Ratio View (Expected Claims)","Loss Ratio View (Actual Claims)", "Expected Claims View", "Actual Claims View"])

    st.markdown(
        """
        <style>
        .reportview-container {
            background-color: #013220;
            color: white;
        }
        .sidebar .sidebar-content {
            background-color: #013220;
            color: white;
        }
        .main-title {
            color: #e66c37; /* Title color */
            text-align: center; /* Center align the title */
            font-size: 3rem; /* Title font size */
            font-weight: bold; /* Title font weight */
            margin-bottom: .5rem; /* Space below the title */
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1); /* Subtle text shadow */
        }
        div.block-container {
            padding-top: 2rem; /* Padding for main content */
        }
        .subheader {
            color: #e66c37;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            display: inline-block;
        }
        .section-title {
            font-size: 1.75rem;
            color: #004d99;
            margin-top: 2rem;
            margin-bottom: 0.5rem;
        }
        .text {
            font-size: 1.1rem;
            color: #333;
            padding: 10px;
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        .nav-item {
            font-size: 1.2rem;
            color: #004d99;
            margin-bottom: 0.5rem;
        }
        .separator {
            margin: 2rem 0;
            border-bottom: 2px solid #ddd;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if page == "Home":
        st.markdown('<h1 class="main-title">EDEN CARE LOSS RATIO DASHBOARD</h1>', unsafe_allow_html=True)
        st.image("scott-graham-5fNmWej4tAA-unsplash.jpg", caption='Eden Care Medical', use_column_width=True)
        st.markdown('<h2 class="subheader">Welcome to the Eden Care Loss Ratio Dashboard</h2>', unsafe_allow_html=True)
        
        # Introduction
        st.markdown('<div class="text">The Loss Ratio Dashboard provides a clear and insightful overview of our scheme loss ratio, highlighting reasons for variations and identifying areas that need attention. </div>', unsafe_allow_html=True)
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

        # User Instructions
        st.markdown('<h2 class="subheader">User Instructions</h2>', unsafe_allow_html=True)
        st.markdown('<div class="text">1. <strong>Navigation:</strong> Use the menu on the left to navigate between visits, claims and Preauthorisation dashboards.</div>', unsafe_allow_html=True)
        st.markdown('<div class="text">2. <strong>Filters:</strong> Apply filters on the left side of each page to customize the data view.</div>', unsafe_allow_html=True)
        st.markdown('<div class="text">3. <strong>Manage visuals:</strong> Hover over the visuals and use the options on the top right corner of each visual to download zoom or view on fullscreen</div>', unsafe_allow_html=True)
        st.markdown('<div class="text">3. <strong>Manage Table:</strong> click on the dropdown icon (<img src="https://img.icons8.com/ios-glyphs/30/000000/expand-arrow.png"/>) on table below each visual to get a full view of the table data and use the options on the top right corner of each table to download or search and view on fullscreen.</div>', unsafe_allow_html=True)    
        st.markdown('<div class="text">4. <strong>Refresh Data:</strong> The data will be manually refreshed on the last week of every quarter. </div>', unsafe_allow_html=True)
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    elif page == "Overview for Expected Claims":
        exec(open("overview.py").read())
    elif page == "Overview for Actual Claims":
        exec(open("overview_c.py").read())
    elif page == "Loss Ratio View (Expected Claims)":
        exec(open("loss_ratio_view.py").read())
    elif page == "Expected Claims View":
        exec(open("visit.py").read())
    elif page == "Actual Claims View":
        exec(open("claims.py").read())
    elif page == "Loss Ratio View (Actual Claims)":
        exec(open("loss.py").read())
    elif page == "Premium View":
        exec(open("premium.py").read())

if __name__ == "__main__":
    main()


