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

st.markdown('<h1 class="main-title">KPI METRICS VIEW WITH EXPECTED CLAIM AMOUNT</h1>', unsafe_allow_html=True)



# Filepaths and sheet names
filepath_premiums = "JAN-NOV 2024 GWP.xlsx"
sheet_name_new_business = "2023"
sheet_name_endorsements = "2024"
filepath_visits = "VisitLogs_25Oct2024 (1).xlsx"

# Read the premium data
df_2023 = pd.read_excel(filepath_premiums, sheet_name=sheet_name_new_business)
df_2024 = pd.read_excel(filepath_premiums, sheet_name=sheet_name_endorsements)

# Read the visit logs
df_visits = pd.read_excel(filepath_visits)

df_premiums = pd.concat([df_2023, df_2024])

drop_cols=['Amount Received - Jan _ march', 'MONTH', 'Contract days', 'Cover days', 'Amount Received - April', 'Amount Received - May', 'Amount Received - June', 'Amount Received - JULY', 'Unnamed: 25', 'Unnamed: 26', 'Unnamed: 27']

df_premiums.drop(columns=drop_cols, inplace = True)

df_premiums["Start Date"] = pd.to_datetime(df_premiums["Start Date"])
df_premiums["Month"] = df_premiums["Start Date"].dt.strftime("%B")
df_premiums["Year"] = df_premiums["Start Date"].dt.year


# Split the DataFrame into two: one with endorsements and one without
df_endorsements = df_premiums[df_premiums['Cover Type'].str.contains('Endorsement', case=False, na=False)]
df_non_endorsements = df_premiums[~df_premiums['Cover Type'].str.contains('Endorsement', case=False, na=False)]

# Calculate 'Days Since Start' and 'days_on_cover' for non-endorsement rows
current_date = datetime.now()
df_non_endorsements['Days Since Start'] = (current_date - df_non_endorsements['Start Date']).dt.days
df_non_endorsements['days_on_cover'] = (df_non_endorsements['End Date'] - df_non_endorsements['Start Date']).dt.days


# Prioritize 'renewed' cover type values
def prioritize_renewal(df):
    # Identify clients with both 'new' and 'renewal' cover types
    clients_with_both = df.groupby('Client Name')['Cover Type'].nunique()
    clients_with_both = clients_with_both[clients_with_both == 2].index
    
    # Separate clients with both cover types from others
    df_clients_with_both = df[df['Client Name'].isin(clients_with_both)]
    df_other_clients = df[~df['Client Name'].isin(clients_with_both)]
    
    # Sort and deduplicate clients with both cover types, prioritizing 'renewal'
    df_clients_with_both_sorted = df_clients_with_both.sort_values(by=['Client Name', 'Cover Type'], ascending=[True, False])
    df_clients_with_both_deduped = df_clients_with_both_sorted.drop_duplicates(subset=['Client Name'], keep='first')
    
    # Combine the deduplicated clients with both cover types and the other clients
    df_result = pd.concat([df_clients_with_both_deduped, df_other_clients])
    
    return df_result

df_prioritized = prioritize_renewal(df_non_endorsements)

# Merge endorsements with premiums on Client Name
df_merged_endorsements = pd.merge(df_endorsements, df_prioritized[['Client Name', 'Start Date', 'End Date']], on='Client Name', suffixes=('_endorsement', '_premium'))

# Filter endorsements to include only those within the start and end date range of the premiums
df_filtered_endorsements = df_merged_endorsements[
    (df_merged_endorsements['Start Date_endorsement'] >= df_merged_endorsements['Start Date_premium']) & 
    (df_merged_endorsements['Start Date_endorsement'] <= df_merged_endorsements['End Date_premium'])
]

# Drop the additional date columns used for filtering
df_filtered_endorsements = df_filtered_endorsements.drop(columns=['Start Date_premium', 'End Date_premium'])

# Rename the date columns back to their original names
df_filtered_endorsements = df_filtered_endorsements.rename(columns={'Start Date_endorsement': 'Start Date', 'End Date_endorsement': 'End Date'})

# Combine the processed non-endorsement DataFrame with the filtered endorsements DataFrame
df_premiums = pd.concat([df_prioritized, df_filtered_endorsements])

# Reset the index of the resulting DataFrame
df_premiums.reset_index(drop=True, inplace=True)


df_visits['Visit Date'] = pd.to_datetime(df_visits['Visit Date'])
df_premiums['Start Date'] = pd.to_datetime(df_premiums['Start Date'])
df_premiums['End Date'] = pd.to_datetime(df_premiums['End Date'])

# Merge new business data with visit data on Client Name
df_merged = pd.merge(df_visits, df_premiums[['Client Name', 'Start Date', 'End Date']], on='Client Name', how='outer')


# Filter visits to include only those within the start and end date range
df_filtered_visits = df_merged[
    (df_merged['Visit Date'] >= df_merged['Start Date']) & 
    (df_merged['Visit Date'] <= df_merged['End Date'])
]


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

df_visits_agg['Visit Date min'] = pd.to_datetime(df_visits_agg['Visit Date min'], errors='coerce')

# Extract 'Month' and 'Year' from the minimum visit date
df_visits_agg['Month'] = df_visits_agg['Visit Date min'].dt.strftime('%B')
df_visits_agg['Year'] = df_visits_agg['Visit Date min'].dt.year

# Clean Client Name columns to ensure consistency
df_visits_agg['Client Name'] = df_visits_agg['Client Name'].str.strip().str.lower()
df_premiums['Client Name'] = df_premiums['Client Name'].str.strip().str.lower()

# Ensure Client Name columns are of the same data type
df_visits_agg['Client Name'] = df_visits_agg['Client Name'].astype(str)
df_premiums['Client Name'] = df_premiums['Client Name'].astype(str)

# Merge the aggregated visit data with the premium data on Client Name
df_combined = pd.merge(df_visits_agg, df_premiums, on='Client Name', how='outer')



# Merge the aggregated visit data with the premium data
df_combined = pd.concat([df_visits_agg, df_premiums])


# Convert 'Start Date' to datetime
df_combined["Start Date"] = pd.to_datetime(df_combined["Start Date"])
df_combined["End Date"] = pd.to_datetime(df_combined["End Date"])

df = df_combined

df["Client Name"] = df["Client Name"].str.upper()



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
product = st.sidebar.multiselect("Select Product", options=df['Product'].unique())

# segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
client_names = sorted(df['Client Name'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=client_names)

# Apply filters to the DataFrame
if 'Start Year' in df.columns and year:
    df = df[df['Start Year'].isin(year)]
if 'Start Month' in df.columns and month:
    df = df[df['Start Month'].isin(month)]
if 'Cover Type' in df.columns and cover:
    df = df[df['Cover Type'].isin(cover)]
if 'Product' in df.columns and product:
    df = df[df['Product'].isin(product)]
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


# Get minimum and maximum dates for the date input
startDate = df["Start Date"].min()
endDate = df["End Date"].max()

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




# # Filter the concatenated DataFrame to include only endorsements
# df_hares = df[df['Client Segment'] == 'Hares']
# df_elephants = df[df['Client Segment'] == 'Elephant']
# df_tiger = df[df['Client Segment'] == 'Tigers']
# df_whale = df[df['Client Segment'] == 'Whale']


df_new = df[df['Cover Type'] == 'New']
df_renew = df[df['Cover Type'] == 'Renewal']

df_endorsements = df[df['Cover Type'] == 'Endorsement']

if not df.empty:

    scale=1_000_000  # For millions


    # Scale the sums

    # total_hares = (df_hares['Total Premium'].sum())/scale
    # total_tiger = (df_tiger['Total Premium'].sum())/scale
    # total_elephant = (df_elephants['Total Premium'].sum())/scale
    # total_whale = (df_whale['Total Premium'].sum())/scale

    total_new = (df_new["Total"].sum())/scale
    total_renew = (df_renew["Total"].sum())/scale
    total_endorsements_amount = df_endorsements["Total"].sum()/scale
    total_pharm = df["Pharmacy Claim Amount sum"].sum()/scale

    total_clients = df["Client Name"].nunique()
    total_endorsements = df_endorsements["Client Name"].count()
    num_new = df_new["Client Name"].nunique()
    num_renew = df_renew["Client Name"].nunique()
    num_visits = df["Visit ID count"].sum()


    # total_new_premium = (df["Total Premium_new"].sum())/scale
    # total_endorsement = (df["Total Premium_endorsements"].sum())/scale
    total_premium = (df["Total"].sum())/scale
    total_days = df["Days Since Start"].sum()
    total_days_on_cover = df['days_on_cover'].sum()
    total_amount = (df["Total Amount sum"].sum())/scale
    average_pre = (df["Total"].mean())/scale
    average_days = df["Days Since Start"].mean()

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

    st.dataframe(df)

    # Function to display metrics in styled boxes with tooltips
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)


    # Calculate key metrics
    st.markdown('<h2 class="custom-subheader">For all Sales in Numbers</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Number of Clients", total_clients)
    display_metric(cols2, "Number of New Business", num_new)
    display_metric(cols3, "Number of Renewals", num_renew)
    display_metric(cols1, "Number of Endorsements",total_endorsements)
    display_metric(cols2, "Number of Visits", f"{num_visits:,.0f}")

    # Calculate key metrics
    st.markdown('<h2 class="custom-subheader">For all Sales Amount</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Total Premium", f"{total_premium:,.0f} M")
    display_metric(cols2, "Total New Business Premium", f"{total_new:,.0f} M")
    display_metric(cols3, "Total Renewal Premium", f"{total_renew:,.0f} M")
    display_metric(cols1, "Total Endorsement Premium", f"{total_endorsements_amount:,.0f} M")
    display_metric(cols2, "Total Expected Pharmacy Amount", f"{total_pharm:,.0f} M")
    display_metric(cols3, "Total Expected Claim Amount", f"{total_amount:,.0f} M")
    display_metric(cols1, "Average Premium per Client", f"{average_pre:,.0f} M")

    st.markdown('<h2 class="custom-subheader">For Loss Ratio</h2>', unsafe_allow_html=True)    
  
    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Days Since  Premium Start", f"{total_days:,.0f} days")
    display_metric(cols2, "Premium Duration (Days)", f"{total_days_on_cover:,.0f} days")
    display_metric(cols3, "Average Days Since  Premium Start per Client", f"{average_days:,.0f} days")
    display_metric(cols1, "Earned Premium", f"{earned_premium:,.0f} M")
    display_metric(cols2, "Loss Ratio", f"{loss_ratio_amount:,.0f} M")
    display_metric(cols3, "Percentage Loss Ratio", f"{loss_ratio: .0f} %")



