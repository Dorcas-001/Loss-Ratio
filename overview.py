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

st.markdown('<h1 class="main-title">KPI METRICS VIEW DASHBOARD</h1>', unsafe_allow_html=True)



# Filepaths and sheet names
filepath_premiums = "WRITTEN PREMIUM 2024 (1).xlsx"
sheet_name_new_business = "NEW BUSINES"
sheet_name_endorsements = "ENDORSMENTS"
filepath_visits = "VisitLogs_25Oct2024 (1).xlsx"

# Read the premium data
df_new_business = pd.read_excel(filepath_premiums, sheet_name=sheet_name_new_business)
df_endorsements = pd.read_excel(filepath_premiums, sheet_name=sheet_name_endorsements)

# Read the visit logs
df_visits = pd.read_excel(filepath_visits)


# Function to calculate days since start
current_date = datetime.now()

def calculate_days(row):
    start_date = row['Start Date']
    if pd.notnull(start_date):
        days = (current_date - pd.to_datetime(start_date)).days
    else:
        days = None
    return days

# Calculate 'Days Since Start' for each row
df_new_business['Days Since Start'] = df_new_business.apply(calculate_days, axis=1)

# Calculate 'days_on_cover'
df_new_business["days_on_cover"] = (df_new_business["End Date"] - df_new_business['Start Date']).dt.days

# Prioritize 'renewed' cover type values
def prioritize_renewed(df):
    df_sorted = df.sort_values(by=['Client Name', 'Cover Type'], ascending=[True, False])
    df_deduped = df_sorted.drop_duplicates(subset=['Client Name'], keep='first')
    return df_deduped

df_new_business = prioritize_renewed(df_new_business)


# Ensure Visit Date is in datetime format
df_visits['Visit Date'] = pd.to_datetime(df_visits['Visit Date'])

# Merge new business data with visit data on Client Name
df_merged = pd.merge(df_visits, df_new_business[['Client Name', 'Start Date']], on='Client Name', how='inner')

# Filter visits to include only those within the start date range
df_filtered_visits = df_merged[df_merged['Visit Date'] >= df_merged['Start Date']]


# Aggregate visit data by 'Client Name'
df_visits_agg = df_filtered_visits.groupby('Client Name').agg({
    'Visit ID': 'count',  # Count of visits
    'Total Amount': 'sum',  # Sum of visit close amounts
    'Pharmacy Claim Amount': 'sum',  # Sum of pharmacy claim amounts
    'Total Amount': 'sum',  # Sum of total amounts
    'Visit Date': ['min', 'max'] 
}).reset_index()


# Flatten the column names after aggregation
df_visits_agg.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df_visits_agg.columns]

# Extract 'Month' and 'Year' from the minimum visit date
df_visits_agg['Month'] = df_visits_agg['Visit Date min'].dt.strftime('%B')
df_visits_agg['Year'] = df_visits_agg['Visit Date min'].dt.year


# Merge the new business and endorsement data on 'Client Name'
df_premiums = pd.concat([df_new_business, df_endorsements])
# Assuming df_premiums is your DataFrame
print("Column names in the DataFrame:")
print(df_premiums.columns.tolist())

drop_cols = ['Unnamed: 14', 'Unnamed: 15','NAMES', 'DAYS','Intermediary name', 'First issued quote date', 'Aging', 'Scheme Name','Annual Premium', 'Prorated Premium', 'CBHI', 'Admin','5% CBHI', 'Admin fees', 'Total insured Premium', 'Fund Amount','Basic Premium']
df_premiums.drop(columns=drop_cols, inplace = True)



# Merge the aggregated visit data with the premium data
df_combined = pd.concat([df_visits_agg, df_premiums])


# Convert 'Start Date' to datetime
df_combined["Start Date"] = pd.to_datetime(df_combined["Start Date"])
df_combined["End Date"] = pd.to_datetime(df_combined["End Date"])

df = df_combined




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
startDate = df["Start Date"].min()
endDate = df["Start Date"].max()

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
    date1 = pd.to_datetime(display_date_input(col1, "Start Date", startDate, startDate, endDate))

with col2:
    date2 = pd.to_datetime(display_date_input(col2, "End Date", endDate, startDate, endDate))



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
cover = st.sidebar.multiselect("Select Cover Type", options=df['Cover Type'].unique())
segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())


# Apply filters to the DataFrame
if 'Start Year' in df.columns and year:
    df = df[df['Start Year'].isin(year)]
if 'Start Month' in df.columns and month:
    df = df[df['Start Month'].isin(month)]
if 'Cover Type' in df.columns and cover:
    df = df[df['Cover Type'].isin(cover)]
if 'Client Segment' in df.columns and segment:
    df = df[df['Client Segment'].isin(segment)]
if 'Client Name' in df.columns and client_name:
    df = df[df['Client Name'].isin(client_name)]

# Determine the filter description
filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
if cover:
    filter_description += f"{', '.join(map(str, cover))} "
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




# Filter the concatenated DataFrame to include only endorsements
df_hares = df[df['Client Segment'] == 'Hares']
df_elephants = df[df['Client Segment'] == 'Elephant']
df_tiger = df[df['Client Segment'] == 'Tigers']
df_whale = df[df['Client Segment'] == 'Whale']

df_new = df[df['Cover Type'] == 'New Insured']
df_renew = df[df['Cover Type'] == 'Renew/Insured']

df

if not df.empty:

    scale=1_000_000  # For millions

    df["No. of staffs"] = pd.to_numeric(df["No. of staffs"], errors='coerce').fillna(0).astype(int)
    df["Dependents"] = pd.to_numeric(df["Dependents"], errors='coerce').fillna(0).astype(int)

    # Scale the sums

    total_hares = (df_hares['Total Premium'].sum())/scale
    total_tiger = (df_tiger['Total Premium'].sum())/scale
    total_elephant = (df_elephants['Total Premium'].sum())/scale
    total_whale = (df_whale['Total Premium'].sum())/scale

    total_new = (df_new["Total Premium"].sum())/scale
    total_renew = (df_renew["Total Premium"].sum())/scale

    total_clients = df["Client Name"].nunique()
    total_mem = df["No. of staffs"].sum()
    total_dependents = df["Dependents"].sum()
    total_lives = df["Total lives"].sum()
    average_dep = total_mem/total_dependents

    total_days_on_cover = df["days_on_cover"].sum()

    total_new_premium = (df["Total Premium_new"].sum())/scale
    total_endorsement = (df["Total Premium_endorsements"].sum())/scale
    total_premium = (df["Total Premium"].sum())/scale
    total_days = df["Days Since Start"].sum()
    total_days_on_cover = df['days_on_cover'].sum()
    total_amount = (df["Total Amount sum"].sum())/scale
    average_pre = (df["Total Premium"].mean())/scale
    average_days = df["Days Since Start"].mean()
    average_premium_per_life = total_premium/total_mem

    earned_premium = (total_premium * total_days)/total_days_on_cover
    loss_ratio_amount = total_amount / earned_premium
    loss_ratio= (total_amount / earned_premium) *100

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
    display_metric(cols2, "Total Premium", F"{total_premium: .0F} M")
    display_metric(cols3, "Total New Business Premium", F"{total_new_premium: .0F} M")
    display_metric(cols1, "Total Endorsement", F"{total_endorsement: .0F} M")
    display_metric(cols2, "Total New Premium", F"{total_new: .0F} M")
    display_metric(cols3, "Total Renewals", F"{total_renew: .0F} M")

    st.markdown('<h2 class="custom-subheader">For Loss Ratio</h2>', unsafe_allow_html=True)    
  
    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Total visit Amount", f"{total_amount:.0f} M")
    display_metric(cols2, "Total Days Since Start", f"{total_days:.0f} days")
    display_metric(cols3, "Total Days on Cover", f"{total_days_on_cover:.0f} days")
    display_metric(cols1, "Earned Premium", f"{earned_premium: .0f} M")
    display_metric(cols2, "Loss Ratio", f"{loss_ratio_amount: .0f} M")
    display_metric(cols3, "Percentage Loss Ratio", f"{loss_ratio: .0f} %")


    # Calculate key metrics
    st.markdown('<h2 class="custom-subheader">For Expected Lives Covered</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Total Lives Covered", f"{total_lives:.0f}")
    display_metric(cols2, "Total Principal Members", total_mem)
    display_metric(cols3, "Total Dependents", total_dependents)
    display_metric(cols1, "Average Dependents Per Principal Member", f"{average_dep:.0f}")
    display_metric(cols2, "Average Premium Per Principal Member", f"{average_premium_per_life:.0f}")


    df