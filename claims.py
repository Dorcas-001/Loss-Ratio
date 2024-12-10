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

st.markdown('<h1 class="main-title">ACTUAL CLAIMS VIEW</h1>', unsafe_allow_html=True)



filepath_visits = "Claims.xlsx"
sheet_name1 = "2023 claims"
sheet_name2 = "2024 claims"

# Read the Claims data
dfc_2023 = pd.read_excel(filepath_visits, sheet_name=sheet_name1)
dfc_2024 = pd.read_excel(filepath_visits, sheet_name=sheet_name2)

# Read the visit logs
df = pd.concat([dfc_2023, dfc_2024])


df['Claim Created Date'] = pd.to_datetime(df['Claim Created Date'], errors='coerce')

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
df = df[df['Month'].isin(month_order)]


# Sort months based on their order
sorted_months = sorted(df['Month'].dropna().unique(), key=lambda x: pd.to_datetime(x, format='%B').month)


# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted_months)
type = st.sidebar.multiselect("Select Claim Type", options=df['Claim Type'].unique())
status = st.sidebar.multiselect("Select Claim Status", options=df['Claim Status'].unique())
source = st.sidebar.multiselect("Select Claim Source", options=df['Source'].unique())
code = st.sidebar.multiselect("Select Diagnosis Code", options=df['ICD-10 Code'].unique())
client_name = st.sidebar.multiselect("Select Employer Name", options=df['Employer Name'].unique())
prov_name = st.sidebar.multiselect("Select Provider Name", options=df['Provider Name'].unique())


# Apply filters to the DataFrame
if 'Start Year' in df.columns and year:
    df = df[df['Start Year'].isin(year)]
if 'Start Month' in df.columns and month:
    df = df[df['Start Month'].isin(month)]
if 'Claim Type' in df.columns and type:
    df = df[df['Claim Type'].isin(type)]
if 'Claim Status' in df.columns and status:
    df = df[df['Claim Status'].isin(status)]
if 'Source' in df.columns and source:
    df = df[df['Source'].isin(source)]
if 'ICD-10 Code' in df.columns and code:
    df = df[df['ICD-10 Code'].isin(code)]
if 'Employer Name' in df.columns and client_name:
    df = df[df['Employer Name'].isin(client_name)]
if 'Provider Name' in df.columns and prov_name:
    df = df[df['Provider Name'].isin(prov_name)]


# Determine the filter description
filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
if type:
     filter_description += f"{', '.join(map(str, type))} "
if month:
    filter_description += f"{', '.join(month)} "
if not filter_description:
    filter_description = "All data"





# Get minimum and maximum dates for the date input
startDate = df["Claim Created Date"].min()
endDate = df["Claim Created Date"].max()

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
    date1 = pd.to_datetime(display_date_input(col1, "First Claim Created Date", startDate, startDate, endDate))

with col2:
    date2 = pd.to_datetime(display_date_input(col2, "Last Claim Created Date", endDate, startDate, endDate))


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





df_out = df[df['Claim Type'] == 'Outpatient']
df_dental = df[df['Claim Type'] == 'Dental']
df_wellness = df[df['Claim Type'] == 'Wellness']
df_optical = df[df['Claim Type'] == 'Optical']
df_phar = df[df['Claim Type'] == 'Pharmacy']
df_mat = df[df['Claim Type'] == 'Maternity']
df_pro = df[df['Claim Type'] == 'ProActiv']
df_in = df[df['Claim Type'] == 'Inpatient']



df_app = df[df['Claim Status'] == 'Approved']
df_dec = df[df['Claim Status'] == 'Declined']

if not df.empty:

    scale=1_000_000  # For millions

    total_claim_amount = (df["Claim Amount"].sum())/scale
    average_amount =(df["Claim Amount"].mean())/scale
    average_app_amount =(df["Approved Claim Amount"].mean())/scale

    total_out = (df_out['Approved Claim Amount'].sum())/scale
    total_dental = (df_dental['Approved Claim Amount'].sum())/scale
    total_wellness = (df_wellness['Approved Claim Amount'].sum())/scale
    total_optical = (df_optical['Approved Claim Amount'].sum())/scale
    total_in = (df_in['Approved Claim Amount'].sum())/scale
    total_phar = (df_phar['Approved Claim Amount'].sum())/scale
    total_pro = (df_pro['Approved Claim Amount'].sum())/scale
    total_mat = (df_mat['Approved Claim Amount'].sum())/scale

    total_app_claim_amount = (df_app["Claim Amount"].sum())/scale
    total_dec_claim_amount = (df_dec["Claim Amount"].sum())/scale



    total_clients = df["Employer Name"].nunique()
    total_claims = df["Claim ID"].nunique()

    total_app = df_app["Claim ID"].nunique()
    total_dec = df_dec["Claim ID"].nunique()
    total_app_per = (total_app/total_claims)*100
    total_dec_per = (total_dec/total_claims)*100





    percent_app = (total_app_claim_amount/total_claim_amount) *100





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
    st.markdown('<h2 class="custom-subheader">For all Claims in Numbers</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Number of Clients", total_clients)
    display_metric(cols2, "Number of Claims", total_claims)
    display_metric(cols3, "Number of Approved Claims", total_app)
    display_metric(cols1, "Number of Declined Claims",total_dec)
    display_metric(cols2, "Percentage Approved", F"{total_app_per: .0F} %")
    display_metric(cols3, "Percentage Declined", F"{total_dec_per: .0F} %")

    # Calculate key metrics
    st.markdown('<h2 class="custom-subheader">For all Claim Amounts</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3 = st.columns(3)

    display_metric(cols1, "Total Claims", total_claims)
    display_metric(cols2, "Total Claim Amount", f"{total_claim_amount:,.0f} M")
    display_metric(cols3, "Total Approved Claim Amount", f"{total_app_claim_amount:,.0f} M")
    display_metric(cols1, "Total Declined Claim Amount", f"{total_dec_claim_amount:,.0f} M")
    display_metric(cols2, "Average Claim Amount Per Client", F"{average_amount:,.0F} M")
    display_metric(cols3, "Average Approved Claim Amount Per Client", F"{average_app_amount: ,.0F} M")


    st.markdown('<h2 class="custom-subheader">For Approved Amounts by Claim Type</h2>', unsafe_allow_html=True)    
  
    cols1,cols2, cols3 = st.columns(3)
    display_metric(cols1, "Total Approved Claim Amount", F"{total_app_claim_amount:,.0F} M")
    display_metric(cols2, "Approved Claim Amount for Outpatient", f"{total_out:,.0f} M")
    display_metric(cols3, "Approved Claim Amount for Dental", f"{total_dental:,.0f} M")
    display_metric(cols1, "Approved Claim Amount for Optical", f"{total_optical:,.0f} days")
    display_metric(cols2, "Approved Claim Amount for Inpatient", f"{total_in:,.0f} M")
    display_metric(cols3, "Approved Claim Amount for Wellness", f"{total_wellness:,.0f} M")
    display_metric(cols1, "Approved Claim Amount for Maternity", f"{total_mat:,.0f} M")
    display_metric(cols2, "Approved Claim Amount for Pharmacy", f"{total_phar:,.0f} M")
    display_metric(cols3, "Approved Claim Amount for ProActiv", f"{total_pro:,.0f} M")

    cols1, cols2 = st.columns(2)

    custom_colors = ["#009DAE", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

   
        # Group by day and count the occurrences
    area_chart_count = df.groupby(df["Claim Created Date"].dt.strftime("%Y-%m-%d")).size().reset_index(name='Count')
    area_chart_amount = df.groupby(df["Claim Created Date"].dt.strftime("%Y-%m-%d"))['Approved Claim Amount'].sum().reset_index(name='Approved Claim Amount')

    # Merge the count and amount data
    area_chart = pd.merge(area_chart_count, area_chart_amount, on='Claim Created Date')

    # Sort by the PreAuth Created Date
    area_chart = area_chart.sort_values("Claim Created Date")

    with cols1:
        # Create the dual-axis area chart
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig2.add_trace(
            go.Scatter(x=area_chart['Claim Created Date'], y=area_chart['Count'], name="Number of Claims", fill='tozeroy', line=dict(color='#e66c37')),
            secondary_y=False,
        )

        fig2.add_trace(
            go.Scatter(x=area_chart['Claim Created Date'], y=area_chart['Approved Claim Amount'], name="Approved Claim Amount", fill='tozeroy', line=dict(color='#009DAE')),
            secondary_y=True,
        )



        # Set x-axis title
        fig2.update_xaxes(title_text="Claim Created Date", tickangle=45)  # Rotate x-axis labels to 45 degrees for better readability

        # Set y-axes titles
        fig2.update_yaxes(title_text="<b>Number Of Visits</b>", secondary_y=False)
        fig2.update_yaxes(title_text="<b>Approved Claim Amount</b>", secondary_y=True)

        st.markdown('<h3 class="custom-subheader">Number of Visits and Approved Claim Amount Over Time</h3>', unsafe_allow_html=True)

        st.plotly_chart(fig2, use_container_width=True)



    # Group data by "Start Month Year" and "Claim Type" and calculate the average Approved Claim Amount
    yearly_avg_premium = df.groupby(['Year', 'Claim Type'])['Approved Claim Amount'].mean().unstack().fillna(0)

    # Define custom colors

    with cols2:
        # Create the grouped bar chart
        fig_yearly_avg_premium = go.Figure()

        for idx, Client_Segment in enumerate(yearly_avg_premium.columns):
            fig_yearly_avg_premium.add_trace(go.Bar(
                x=yearly_avg_premium.index,
                y=yearly_avg_premium[Client_Segment],
                name=Client_Segment,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Year",
            yaxis_title="Average Approved Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Yearly Approved Claim Amount by Product per Employer Group</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)



    # Group data by "Start Month Year" and "Claim Type" and calculate the average Approved Claim Amount
    yearly_avg_premium = df.groupby(['Year', 'Claim Status'])['Approved Claim Amount'].mean().unstack().fillna(0)

    cols1, cols2 = st.columns(2)

    with cols1:
        # Create the grouped bar chart
        fig_yearly_avg_premium = go.Figure()

        for idx, Client_Segment in enumerate(yearly_avg_premium.columns):
            fig_yearly_avg_premium.add_trace(go.Bar(
                x=yearly_avg_premium.index,
                y=yearly_avg_premium[Client_Segment],
                name=Client_Segment,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Year",
            yaxis_title="Average Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Yearly Approved Claim Amount by Status per Employer Group</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)

    # Group data by "Start Month Year" and "Claim Type" and calculate the average Approved Claim Amount
    yearly_avg_premium = df.groupby(['Year', 'Source'])['Approved Claim Amount'].mean().unstack().fillna(0)


    with cols2:
        # Create the grouped bar chart
        fig_yearly_avg_premium = go.Figure()

        for idx, Client_Segment in enumerate(yearly_avg_premium.columns):
            fig_yearly_avg_premium.add_trace(go.Bar(
                x=yearly_avg_premium.index,
                y=yearly_avg_premium[Client_Segment],
                name=Client_Segment,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Year",
            yaxis_title="Average Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Yearly Approved Claim Amount by Source per Employer Group</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)


    # Group data by "Start Month" and "Channel" and sum the Approved Claim Amount sum
    monthly_premium = df.groupby(['Month', 'Claim Type'])['Approved Claim Amount'].mean().unstack().fillna(0)

    # Group data by "Start Month" to count the number of sales
    monthly_sales_count = df.groupby(['Month']).size()



    # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls1:

        fig_monthly_premium = go.Figure()

        for idx, Client_Segment in enumerate(monthly_premium.columns):
                fig_monthly_premium.add_trace(go.Bar(
                    x=monthly_premium.index,
                    y=monthly_premium[Client_Segment],
                    name=Client_Segment,
                    textposition='inside',
                    textfont=dict(color='white'),
                    hoverinfo='x+y+name',
                    marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
                ))


            # Set layout for the Approved Claim Amount sum chart
        fig_monthly_premium.update_layout(
                barmode='group',  # Grouped bar chart
                xaxis_title="Month",
                yaxis_title="Total Approved Claim Amount",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50),
            )

            # Display the Approved Claim Amount sum chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Avearge Monthly Visits and Approved Claim Amount by Claim Type</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)

    # Group by Employer Name and Client Segment, then sum the Claim Amount
    df_grouped = df.groupby(['Employer Name', 'Claim Status'])['Claim Amount'].sum().nlargest(10).reset_index()

    # Get the top 10 clients by Claim Amount
    top_10_clients = df_grouped.groupby('Employer Name')['Claim Amount'].sum().reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Employer Name'].isin(top_10_clients['Employer Name'])]
    # Sort the client_df by Claim Amount in descending order
    client_df = client_df.sort_values(by='Claim Amount', ascending=False)

    with cls2:
        # Create the bar chart
        fig = go.Figure()

        # Add bars for each Client Segment
        for idx, Client_Segment in enumerate(client_df['Claim Status'].unique()):
            Client_Segment_data = client_df[client_df['Claim Status'] == Client_Segment]
            fig.add_trace(go.Bar(
                x=Client_Segment_data['Employer Name'],
                y=Client_Segment_data['Claim Amount'],
                name=Client_Segment,
                text=[f'{value/1e6:.0f}M' for value in Client_Segment_data['Claim Amount']],
                textposition='auto',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        # Update layout
        fig.update_layout(
            barmode='stack',
            yaxis_title="Claim Amount",
            xaxis_title="Employer Name",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            legend=dict(
                title="Claim Status",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Client Claims Amount by Status</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)


    # Create the layout columns
    cls1, cls2 = st.columns(2)
    
    # Calculate the Approved Claim Amount by Client Segment
    int_owner = df.groupby("Claim Type")["Approved Claim Amount"].sum().reset_index()
    int_owner.columns = ["Claim Type", "Approved Claim Amount"]    

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Approved Claim Amount by Claim Type</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Claim Type", values="Approved Claim Amount", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

# Calculate the Approved Claim Amount by Client Segment
    int_owner = df.groupby("Claim Status")["Approved Claim Amount"].sum().reset_index()
    int_owner.columns = ["Claim Status", "Approved Claim Amount"]    

    with cls2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Approved Claim Amount by Claim Status</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Claim Status", values="Approved Claim Amount", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)


    # Create the layout columns
    cls1, cls2 = st.columns(2)

    # Group by Employer Name and sum the Approved Claim Amount
    df_grouped = df.groupby('Diagnosis')['Approved Claim Amount'].sum().nlargest(10).reset_index()

    # Sort the client_df by Approved Claim Amount in descending order
    client_df = df_grouped.sort_values(by='Approved Claim Amount', ascending=False)

    with cls1:
            # Create the bar chart
            fig = go.Figure()

            # Add bars for each Client
            fig.add_trace(go.Bar(
                x=client_df['Diagnosis'],
                y=client_df['Approved Claim Amount'],
                text=[f'{value/1e6:.0f}M' for value in client_df['Approved Claim Amount']],
                textposition='auto',
                marker_color="#009DAE"  # Use custom colors
            ))

            fig.update_layout(
                yaxis_title="Approved Claim Amount",
                xaxis_title="Diagnosis",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )


            # Display the chart in Streamlit
            st.markdown('<h3 class="custom-subheader">Top 10 Diagnosis by Approved Claim Amount</h3>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)


    # Group by Employer Name and sum the Approved Claim Amount
    df_grouped = df.groupby('ICD-10 Code')['Approved Claim Amount'].sum().nlargest(10).reset_index()

    # Sort the client_df by Approved Claim Amount in descending order
    client_df = df_grouped.sort_values(by='Approved Claim Amount', ascending=False)

    with cls2:
            # Create the bar chart
            fig = go.Figure()

            # Add bars for each Client
            fig.add_trace(go.Bar(
                x=client_df['ICD-10 Code'],
                y=client_df['Approved Claim Amount'],
                text=[f'{value/1e6:.0f}M' for value in client_df['Approved Claim Amount']],
                textposition='auto',
                marker_color="#009DAE" # Use custom colors
            ))

            fig.update_layout(
                yaxis_title="Approved Claim Amount",
                xaxis_title="ICD-10 Code",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )


            # Display the chart in Streamlit
            st.markdown('<h3 class="custom-subheader">Top 10 ICD-10 Code by Approved Claim Amount</h3>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)


    # Create the layout columns
    cls1, cls2 = st.columns(2)
    # Group by Employer Name and Client Segment, then sum the Approved Claim Amount
    df_grouped = df.groupby(['Employer Name', 'Claim Type'])['Approved Claim Amount'].sum().nlargest(15).reset_index()

    # Get the top 10 clients by Approved Claim Amount
    top_10_clients = df_grouped.groupby('Employer Name')['Approved Claim Amount'].sum().reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Employer Name'].isin(top_10_clients['Employer Name'])]

    # Sort the client_df by Approved Claim Amount in descending order
    client_df = client_df.sort_values(by='Approved Claim Amount', ascending=False)

    with cls1:
        # Create the bar chart
        fig = go.Figure()


                # Add bars for each Client Segment
        for idx, Client_Segment in enumerate(client_df['Claim Type'].unique()):
                    Client_Segment_data = client_df[client_df['Claim Type'] == Client_Segment]
                    fig.add_trace(go.Bar(
                        x=Client_Segment_data['Employer Name'],
                        y=Client_Segment_data['Approved Claim Amount'],
                        name=Client_Segment,
                        text=[f'{value/1e6:.0f}M' for value in Client_Segment_data['Approved Claim Amount']],
                        textposition='auto',
                        marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
                    ))

        fig.update_layout(
                    barmode='stack',
                    yaxis_title="Approved Claim Amount",
                    xaxis_title="Employer Name",
                    font=dict(color='Black'),
                    xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                    yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                    margin=dict(l=0, r=0, t=30, b=50)
                )

                # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 15 Clients by Approved Claim Amount and Claim Type</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)



    # Group by Employer Name and Client Segment, then sum the Approved Claim Amount
    df_grouped = df.groupby(['Employer Name', 'Source'])['Approved Claim Amount'].sum().nlargest(15).reset_index()

    # Get the top 10 clients by Approved Claim Amount
    top_10_clients = df_grouped.groupby('Employer Name')['Approved Claim Amount'].sum().reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Employer Name'].isin(top_10_clients['Employer Name'])]

    # Sort the client_df by Approved Claim Amount in descending order
    client_df = client_df.sort_values(by='Approved Claim Amount', ascending=False)

    with cls2:
        # Create the bar chart
        fig = go.Figure()


                # Add bars for each Client Segment
        for idx, Client_Segment in enumerate(client_df['Source'].unique()):
                    Client_Segment_data = client_df[client_df['Source'] == Client_Segment]
                    fig.add_trace(go.Bar(
                        x=Client_Segment_data['Employer Name'],
                        y=Client_Segment_data['Approved Claim Amount'],
                        name=Client_Segment,
                        text=[f'{value/1e6:.0f}M' for value in Client_Segment_data['Approved Claim Amount']],
                        textposition='auto',
                        marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
                    ))

        fig.update_layout(
                    barmode='stack',
                    yaxis_title="Approved Claim Amount",
                    xaxis_title="Employer Name",
                    font=dict(color='Black'),
                    xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                    yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                    margin=dict(l=0, r=0, t=30, b=50)
                )

                # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 15 Clients by Approved Claim Amount and Claim Source</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)



    # Create the layout columns
    cls1, cls2 = st.columns(2)

    # Group by Client Name and sum the Total Amount
    df_grouped = df.groupby('Employer Name')['Approved Claim Amount'].sum().nlargest(10).reset_index()

    # Sort the client_df by Total Amount in descending order
    client_df = df_grouped.sort_values(by='Approved Claim Amount', ascending=False)

    with cls1:
            # Create the bar chart
            fig = go.Figure()

            # Add bars for each Client
            fig.add_trace(go.Bar(
                x=client_df['Employer Name'],
                y=client_df['Approved Claim Amount'],
                text=[f'{value/1e6:.0f}M' for value in client_df['Approved Claim Amount']],
                textposition='auto',
                marker_color="#009DAE" # Use custom colors
            ))

            fig.update_layout(
                yaxis_title="Approved Claim Amount",
                xaxis_title="Employer Name",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )


            # Display the chart in Streamlit
            st.markdown('<h3 class="custom-subheader">Top 10 Employer Groups by Approved Claim Amount</h3>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)

    # Group by Client Name and sum the Total Amount
    df_grouped = df.groupby('Provider Name')['Approved Claim Amount'].sum().nlargest(10).reset_index()

    # Sort the client_df by Total Amount in descending order
    client_df = df_grouped.sort_values(by='Approved Claim Amount', ascending=False)

    with cls2:
            # Create the bar chart
            fig = go.Figure()

            # Add bars for each Client
            fig.add_trace(go.Bar(
                x=client_df['Provider Name'],
                y=client_df['Approved Claim Amount'],
                text=[f'{value/1e6:.0f}M' for value in client_df['Approved Claim Amount']],
                textposition='auto',
                marker_color="#009DAE"
            ))

            fig.update_layout(
                yaxis_title="Approved Claim Amount",
                xaxis_title="Provider Name",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )


            # Display the chart in Streamlit
            st.markdown('<h3 class="custom-subheader">Top 10 Popular Service Providers by Approved Claim Amount</h3>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)