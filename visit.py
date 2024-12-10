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

st.markdown('<h1 class="main-title">EXPECTED CLAIMS VIEW</h1>', unsafe_allow_html=True)




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



    total_clients = df["Client Name"].nunique()
    total_visits = df["Visit ID"].nunique()

    total_close = df_close["Visit ID"].nunique()
    total_ope = df_open["Visit ID"].nunique()
    total_closed_per = (total_close/total_visits)*100
    total_open_per = (total_ope/total_visits)*100








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
    display_metric(cols2, "Total Expected Claims", total_visits)
    display_metric(cols3, "Total Expected Claim Amount", F"{total_amount:,.0F} M")
    display_metric(cols1, "Average Expected Claim Amount Per Client", F"{average_amount:,.1F} M")
    display_metric(cols2, "Percentage Closed Visit", F"{total_closed_per:,.0F} %")
    display_metric(cols3, "Percentage Open Visit", F"{total_open_per:,.0F} %")

    st.markdown('<h2 class="custom-subheader">For Visit Type</h2>', unsafe_allow_html=True)    
  
    cols1,cols2, cols3 = st.columns(3)
    display_metric(cols1, "Expected Claim Amount", F"{total_amount:,.0F} M")
    display_metric(cols2, "Expected Claim Amount for Outpatient", f"{total_out:,.0f} M")
    display_metric(cols3, "Expected Claim Amount for Dental", f"{total_dental:,.0f} M")
    display_metric(cols1, "Expected Claim Amount for Optical", f"{total_optical:,.0f} M")
    display_metric(cols2, "Expected Claim Amount for Inpatient", f"{total_in:,.0f} M")
    display_metric(cols3, "Expected Claim Amount for Wellness", f"{total_wellness:,.0f} M")

    cols1, cols2 = st.columns(2)

    custom_colors = ["#009DAE", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

   
        # Group by day and count the occurrences
    area_chart_count = df.groupby(df["Visit Date"].dt.strftime("%Y-%m-%d")).size().reset_index(name='Count')
    area_chart_amount = df.groupby(df["Visit Date"].dt.strftime("%Y-%m-%d"))['Total Amount'].sum().reset_index(name='Total Amount')

    # Merge the count and amount data
    area_chart = pd.merge(area_chart_count, area_chart_amount, on='Visit Date')

    # Sort by the PreAuth Created Date
    area_chart = area_chart.sort_values("Visit Date")

    with cols1:
        # Create the dual-axis area chart
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig2.add_trace(
            go.Scatter(x=area_chart['Visit Date'], y=area_chart['Count'], name="Number of Visits", fill='tozeroy', line=dict(color='#e66c37')),
            secondary_y=False,
        )

        fig2.add_trace(
            go.Scatter(x=area_chart['Visit Date'], y=area_chart['Total Amount'], name="Total Visit Amount", fill='tozeroy', line=dict(color='#009DAE')),
            secondary_y=True,
        )



        # Set x-axis title
        fig2.update_xaxes(title_text="Visit Date", tickangle=45)  # Rotate x-axis labels to 45 degrees for better readability

        # Set y-axes titles
        fig2.update_yaxes(title_text="<b>Number Of Expected Claims</b>", secondary_y=False)
        fig2.update_yaxes(title_text="<b>Total Expected Claim Amount</b>", secondary_y=True)

        st.markdown('<h3 class="custom-subheader">Number of Expected Claim and Expected Claim Amount Over Time</h3>', unsafe_allow_html=True)

        st.plotly_chart(fig2, use_container_width=True)



    # Group data by "Start Month Year" and "Visit Type" and calculate the average Total Amount
    yearly_avg_premium = df.groupby(['Year', 'Visit Type'])['Total Amount'].mean().unstack().fillna(0)

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
            yaxis_title="Average Expected Claim Amount",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Yearly Expected Claim Amount by Product per Employer Group</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)


    # Group data by "Start Month" and "Channel" and sum the Total Amount sum
    monthly_premium = df.groupby(['Month', 'Visit Type'])['Total Amount'].mean().unstack().fillna(0)

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


            # Set layout for the Total Amount sum chart
        fig_monthly_premium.update_layout(
                barmode='group',  # Grouped bar chart
                xaxis_title="Month",
                yaxis_title="Expected Claim Amount",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50),
            )

            # Display the Total Amount sum chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Avearge Monthly Expected Claim and Expected Claim Amount by Visit Type</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)

    # Group by Client Name and Client Segment, then sum the Total Amount
    df_grouped = df.groupby(['Client Name', 'Visit Type'])['Total Amount'].sum().nlargest(15).reset_index()

    # Get the top 10 clients by Total Amount
    top_10_clients = df_grouped.groupby('Client Name')['Total Amount'].sum().reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Client Name'].isin(top_10_clients['Client Name'])]

    # Sort the client_df by Total Amount in descending order
    client_df = client_df.sort_values(by='Total Amount', ascending=False)

    with cls2:
        # Create the bar chart
        fig = go.Figure()


                # Add bars for each Client Segment
        for idx, Client_Segment in enumerate(client_df['Visit Type'].unique()):
                    Client_Segment_data = client_df[client_df['Visit Type'] == Client_Segment]
                    fig.add_trace(go.Bar(
                        x=Client_Segment_data['Client Name'],
                        y=Client_Segment_data['Total Amount'],
                        name=Client_Segment,
                        text=[f'{value/1e6:.0f}M' for value in Client_Segment_data['Total Amount']],
                        textposition='auto',
                        marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
                    ))

        fig.update_layout(
                    barmode='stack',
                    yaxis_title="Expected Claim Amount",
                    xaxis_title="Client Name",
                    font=dict(color='Black'),
                    xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                    yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                    margin=dict(l=0, r=0, t=30, b=50)
                )

                # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 10 Clients by Expected Claim Amount and Visit Type</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)


    # Create the layout columns
    cls1, cls2 = st.columns(2)
    
    # Calculate the Total Amount by Client Segment
    int_owner = df.groupby("Visit Type")["Total Amount"].sum().reset_index()
    int_owner.columns = ["Visit Type", "Total Amount"]    

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Expected Claim Amount by Visit Type</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Visit Type", values="Total Amount", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

# Calculate the Total Amount by Client Segment
    int_owner = df.groupby("Visit Status")["Total Amount"].sum().reset_index()
    int_owner.columns = ["Visit Status", "Total Amount"]    

    with cls2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Expected Claim Amount by Visit Status</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Visit Status", values="Total Amount", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)


    # Create the layout columns
    cls1, cls2 = st.columns(2)


    # Group by Client Name and sum the Total Amount
    df_grouped = df.groupby('Provider Name')['Total Amount'].sum().nlargest(15).reset_index()

    # Sort the client_df by Total Amount in descending order
    client_df = df_grouped.sort_values(by='Total Amount', ascending=False)

    with cls2:
            # Create the bar chart
            fig = go.Figure()

            # Add bars for each Client
            fig.add_trace(go.Bar(
                x=client_df['Provider Name'],
                y=client_df['Total Amount'],
                text=[f'{value/1e6:.0f}M' for value in client_df['Total Amount']],
                textposition='auto',
                marker_color="#009DAE"  # Use custom colors
            ))

            fig.update_layout(
                yaxis_title="Expected Claim Amount",
                xaxis_title="Provider Name",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )


            # Display the chart in Streamlit
            st.markdown('<h3 class="custom-subheader">Top 10 Popular Service Providers by Expected Claim Amount</h3>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)

    # Group by Client Name and sum the Total Amount
    df_grouped = df.groupby('Client Name')['Total Amount'].sum().nlargest(15).reset_index()

    # Sort the client_df by Total Amount in descending order
    client_df = df_grouped.sort_values(by='Total Amount', ascending=False)

    with cls1:
            # Create the bar chart
            fig = go.Figure()

            # Add bars for each Client
            fig.add_trace(go.Bar(
                x=client_df['Client Name'],
                y=client_df['Total Amount'],
                text=[f'{value/1e6:.0f}M' for value in client_df['Total Amount']],
                textposition='auto',
                marker_color="#009DAE"  # Use custom colors
            ))

            fig.update_layout(
                yaxis_title="Expected Claim Amount",
                xaxis_title="Client Name",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )


            # Display the chart in Streamlit
            st.markdown('<h3 class="custom-subheader">Top 10 Clients by Expected Claim Amount</h3>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)

