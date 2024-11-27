import streamlit as st
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import chain
from matplotlib.ticker import FuncFormatter
from datetime import datetime


# Centered and styled main title using inline styles
st.markdown('''
    <style>
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
    </style>
''', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">VISIT LOG VIEW</h1>', unsafe_allow_html=True)




filepath_visits = "VisitLogs_25Oct2024 (1).xlsx"

# Read the visit logs
df = pd.read_excel(filepath_visits)

# Ensure Visit Date is in datetime format
df['Visit Date'] = pd.to_datetime(df['Visit Date'])



# Inspect the merged DataFrame

# Sidebar styling and logo
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content h2 {
        color: #007BFF; /* Change this color to your preferred title color */
        font-size: 1.5em;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-title {
        color: #e66c37;
        font-size: 1.2em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-header {
        color: #e66c37; /* Change this color to your preferred header color */
        font-size: 2.5em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-multiselect {
        margin-bottom: 15px;
    }
    .sidebar .sidebar-content .logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content .logo img {
        max-width: 80%;
        height: auto;
        border-radius: 50%;
    }
            
    </style>
    """, unsafe_allow_html=True)


# Get minimum and maximum dates for the date input
startDate = df["Visit Date"].min()
endDate = df["Visit Date"].max()

# Define CSS for the styled date input boxes
st.markdown("""
    <style>
    .date-input-box {
        border-radius: 10px;
        text-align: left;
        margin: 5px;
        font-size: 1.2em;
        font-weight: bold;
    }
    .date-input-title {
        font-size: 1.2em;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)


# Create 2-column layout for date inputs
col1, col2 = st.columns(2)


# Function to display date input in styled boxes
def display_date_input(col, title, default_date, min_date, max_date):
    col.markdown(f"""
        <div class="date-input-box">
            <div class="date-input-title">{title}</div>
        </div>
        """, unsafe_allow_html=True)
    return col.date_input("", default_date, min_value=min_date, max_value=max_date)

# Display date inputs
with col1:
    date1 = pd.to_datetime(display_date_input(col1, "Visit Date", startDate, startDate, endDate))

with col2:
    date2 = pd.to_datetime(display_date_input(col2, "Visit Date", endDate, startDate, endDate))



# Dictionary to map month names to their order
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}

# Sort months based on their order
sorted_months = sorted(df['Month'].dropna().unique(), key=lambda x: month_order[x])


# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted_months)
type = st.sidebar.multiselect("Select Visit Type", options=df['Visit Type'].unique())
status = st.sidebar.multiselect("Select Visit Status", options=df['Visit Status'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())


# Apply filters to the DataFrame
if 'Start Year' in df.columns and year:
    df = df[df['Start Year'].isin(year)]
if 'Start Month' in df.columns and month:
    df = df[df['Start Month'].isin(month)]
if 'Visit Type' in df.columns and type:
    df = df[df['Visit Type'].isin(type)]
if 'Visit Status' in df.columns and status:
    df = df[df['Visit Status'].isin(status)]
if 'Client Name' in df.columns and client_name:
    df = df[df['Client Name'].isin(client_name)]

# Determine the filter description
filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
# if cover:
#     filter_description += f"{', '.join(map(str, cover))} "
if month:
    filter_description += f"{', '.join(month)} "
if not filter_description:
    filter_description = "All data"


# Handle non-finite values in 'Start Year' column
df['Year'] = df['Year'].fillna(0).astype(int)  # Replace NaN with 0 or any specific value

# Handle non-finite values in 'Start Month' column
df['Month'] = df['Month'].fillna('Unknown')

# Create a 'Month-Year' column
df['Month-Year'] = df['Month'] + ' ' + df['Year'].astype(str)

# Function to sort month-year combinations
def sort_key(month_year):
    month, year = month_year.split()
    return (int(year), month_order.get(month, 0))  # Use .get() to handle 'Unknown' month

# Extract unique month-year combinations and sort them
month_years = sorted(df['Month-Year'].unique(), key=sort_key)

# Select slider for month-year range
selected_month_year_range = st.select_slider(
    "Select Month-Year Range",
    options=month_years,
    value=(month_years[0], month_years[-1])
)

# Filter DataFrame based on selected month-year range
start_month_year, end_month_year = selected_month_year_range
start_month, start_year = start_month_year.split()
end_month, end_year = end_month_year.split()

start_index = (int(start_year), month_order.get(start_month, 0))
end_index = (int(end_year), month_order.get(end_month, 0))

# Filter DataFrame based on month-year order indices
df = df[
    df['Month-Year'].apply(lambda x: (int(x.split()[1]), month_order.get(x.split()[0], 0))).between(start_index, end_index)
]





df_out = df[df['Visit Type'] == 'Outpatient']
df_dental = df[df['Visit Type'] == 'Dental']
df_wellness = df[df['Visit Type'] == 'Wellness']
df_optical = df[df['Visit Type'] == 'Optical']
df_in = df[df['Visit Type'] == 'Inpatient']


df_close = df[df['Visit Status'] == 'Close']
df_open = df[df['Visit Status'] == 'Open']

if not df.empty:

    scale=1_000_000  # For millions

    total_amount = (df["Total Amount"].sum())/scale
    average_amount =(df["Total Amount"].mean())/scale

    total_out = (df_out['Total Amount'].sum())/scale
    total_dental = (df_dental['Total Amount'].sum())/scale
    total_wellness = (df_wellness['Total Amount'].sum())/scale
    total_optical = (df_optical['Total Amount'].sum())/scale
    total_in = (df_in['Total Amount'].sum())/scale

    total_closed = (df_close["Total Amount"].sum())/scale
    total_open = (df_open["Total Amount"].sum())/scale

    total_closed_per = (total_closed/total_amount)*100
    total_open_per = (total_open/total_amount)*100

    total_clients = df["Client Name"].nunique()
    total_visits = df["Visit ID"].nunique()











    # Create 4-column layout for metric cards# Define CSS for the styled boxes and tooltips
    st.markdown("""
        <style>
        .custom-subheader {
            color: #e66c37;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            display: inline-block;
        }
        .metric-box {
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin: 10px;
            font-size: 1.2em;
            font-weight: bold;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            border: 1px solid #ddd;
            position: relative;
        }
        .metric-title {
            color: #e66c37; /* Change this color to your preferred title color */
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #009DAE;
            font-size: 1em;
        }

        </style>
        """, unsafe_allow_html=True)



    # Function to display metrics in styled boxes with tooltips
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)




    # Calculate key metrics
    st.markdown('<h2 class="custom-subheader">For all Sales</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Total Clients", total_clients)
    display_metric(cols2, "Total Visits", total_visits)
    display_metric(cols3, "Total Visit Amount", F"{total_amount: .0F} M")
    display_metric(cols1, "Average Visit Amount Per Client", F"{average_amount: .0F} M")
    display_metric(cols2, "Percentage Closed Visit", F"{total_closed_per: .0F} %")
    display_metric(cols3, "Percentage Open Visit", F"{total_open_per: .0F} %")

    st.markdown('<h2 class="custom-subheader">For Visit Type</h2>', unsafe_allow_html=True)    
  
    cols1,cols2, cols3 = st.columns(3)
    display_metric(cols1, "Total Visit Amount", F"{total_amount: .0F} M")
    display_metric(cols2, "Total Amount for Outpatient", f"{total_out:.0f} M")
    display_metric(cols3, "Total Amount for Dental", f"{total_dental:.0f} days")
    display_metric(cols1, "Total Amount for Optical", f"{total_optical:.0f} days")
    display_metric(cols2, "Total Amount for Inpatient", f"{total_in: .0f} M")
    display_metric(cols3, "Total Amount for Wellness", f"{total_wellness: .0f} M")

    cols1, cols2 = st.columns(2)

    custom_colors = ["#009DAE", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

   
        # Group by day and count the occurrences
    area_chart_count = df.groupby(df["Visit Date"].dt.strftime("%Y-%m-%d")).size().reset_index(name='Count')
    area_chart_amount = df.groupby(df["Date"].dt.strftime("%Y-%m-%d"))['Total Amount'].sum().reset_index(name='Total Amount')

    # Merge the count and amount data
    area_chart = pd.merge(area_chart_count, area_chart_amount, on='Date')

    # Sort by the PreAuth Created Date
    area_chart = area_chart.sort_values("Date")

    with cols1:
        # Create the dual-axis area chart
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig2.add_trace(
            go.Scatter(x=area_chart['Date'], y=area_chart['Count'], name="Number of PreAuth", fill='tozeroy', line=dict(color='#e66c37')),
            secondary_y=False,
        )

        fig2.add_trace(
            go.Scatter(x=area_chart['Date'], y=area_chart['Total Amount'], name="Total PreAuth Amount", fill='tozeroy', line=dict(color='#009DAE')),
            secondary_y=True,
        )



        # Set x-axis title
        fig2.update_xaxes(title_text="Day of the Month", tickangle=45)  # Rotate x-axis labels to 45 degrees for better readability

        # Set y-axes titles
        fig2.update_yaxes(title_text="<b>Number Of PreAuth</b>", secondary_y=False)
        fig2.update_yaxes(title_text="<b>Total PreAuth Amount</b>", secondary_y=True)

        st.markdown('<h2 class="custom-subheader">Number of PreAuths and PreAuth Amount Over Time (2023 & 2024)</h2>', unsafe_allow_html=True)

        st.plotly_chart(fig2, use_container_width=True)

        # Expander for Combined Data Table
        with st.expander("PreAuth Data Table", expanded=False):
            st.dataframe(area_chart.style.background_gradient(cmap='YlOrBr'))
