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

st.markdown('<h1 class="main-title">CLIENT SEGMENT VIEW</h1>', unsafe_allow_html=True)

filepath="WRITTEN PREMIUM 2024 (1).xlsx"
filepath1 = "VisitLogs_25Oct2024 (1).xlsx"
# Read all sheets into a dictionary of DataFrames
df0 = pd.read_excel(filepath)
df1=pd.read_excel(filepath1)



df = pd.concat([df0, df1])




# Ensure the 'Expected Close Date' column is in datetime format
df['Expected Close Date'] = pd.to_datetime(df['Expected Close Date'])
df['Last Contact Date'] = pd.to_datetime(df['Last Contact Date'])

df['Days Difference'] = df['Expected Close Date'] - df['Last Contact Date']


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
startDate = df["Expected Close Date"].min()
endDate = df["Expected Close Date"].max()

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
    date1 = pd.to_datetime(display_date_input(col1, "Expected Close Date", startDate, startDate, endDate))

with col2:
    date2 = pd.to_datetime(display_date_input(col2, "Expected Close Date", endDate, startDate, endDate))


# Dictionary to map month names to their order
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}

# Sort months based on their order
sorted_months = sorted(df['Start Month'].dropna().unique(), key=lambda x: month_order[x])


# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Start Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted_months)
product = st.sidebar.multiselect("Select Product", options=df['Product'].unique())
status = st.sidebar.multiselect("Select Status", options=df['Status'].unique())
segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
channel = st.sidebar.multiselect("Select Channel", options=df['Channel'].unique())

engage = st.sidebar.multiselect("Select Engagement", options=df['Engagement'].unique())
owner = st.sidebar.multiselect("Select Sales Person", options=df['Sales person'].unique())
broker = st.sidebar.multiselect("Select Broker/Intermediary", options=df['Broker'].unique())
client_name = st.sidebar.multiselect("Select Property", options=df['Property'].unique())






# Apply filters to the DataFrame
if 'Start Year' in df.columns and year:
    df = df[df['Start Year'].isin(year)]
if 'Start Month' in df.columns and month:
    df = df[df['Start Month'].isin(month)]
if 'Product' in df.columns and product:
    df = df[df['Product'].isin(product)]
if 'Status' in df.columns and status:
    df = df[df['Status'].isin(status)]
if 'Client Segment' in df.columns and segment:
    df = df[df['Client Segment'].isin(segment)]
if 'Broker' in df.columns and broker:
    df = df[df['Broker'].isin(broker)]
if 'Channel' in df.columns and broker:
    df = df[df['Channel'].isin(channel)]
if 'Sales person' in df.columns and owner:
    df = df[df['Sales person'].isin(owner)]
if 'Property' in df.columns and client_name:
    df = df[df['Property'].isin(client_name)]

# Determine the filter description
filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
if owner:
    filter_description += f"{', '.join(map(str, owner))} "
if month:
    filter_description += f"{', '.join(month)} "
if product:
    filter_description += f"{', '.join(product)} "
if not filter_description:
    filter_description = "All data"




df_proactiv = df[df['Product'] == 'ProActiv']
df_health = df[df['Product'] == 'Health']


df_closed = df[(df['Status_def'] == 'Closed 💪')]
df_lost = df[df['Status_def'] == 'Lost 😢']
df_progress = df[df['Status_def'] == 'In Progress']

df_whales= df[df['Client Segment'] == 'Whales']
df_tigers = df[df['Client Segment'] == 'Tigers']
df_elephants = df[df['Client Segment'] == 'Elephants']
df_hares = df[df['Client Segment'] == 'Hares']

df_proactiv_target = df[df['Product'] == 'ProActiv']
df_health_target = df[df['Product'] == 'Health']
df_renewals = df[df['Product'] == 'Renewals']

df_closed_health = df_closed[df_closed['Product'] == 'Health']
df_lost_pro = df_lost[df_lost['Product'] == 'ProActiv']
df_closed_pro = df_closed[df_closed['Product'] == 'ProActiv']
df_lost_health = df_lost[df_lost['Product'] == 'Health']

df_proactiv_target = df[df['Product'] == 'ProActiv']
df_health_target = df[df['Product'] == 'Health']
df_renewals = df[df['Product'] == 'Renewals']

df_whales_pro = df_whales[df_whales['Product'] == 'ProActiv']
df_tigers_pro = df_tigers[df_tigers['Product'] == 'ProActiv']
df_elephants_pro = df_elephants[df_elephants['Product'] == 'ProActiv']
df_hares_pro = df_hares[df_hares['Product'] == 'ProActiv']

df_whales_health = df_whales[df_whales['Product'] == 'Health']
df_tigers_health  = df_tigers[df_tigers['Product'] == 'Health']
df_elephants_health  = df_elephants[df_elephants['Product'] == 'Health']
df_hares_health  = df_hares[df_hares['Product'] == 'Health']

df["Basic Premium RWF"] = pd.to_numeric(df["Basic Premium RWF"], errors="coerce")

if not df.empty:

# Calculate the Basic Premium RWF for endorsements only

    scale=1_000_000  # For millions

    total_pre = (df["Basic Premium RWF"].sum())

    # Scale the sums
    total_pre_scaled = total_pre /scale 


    # Calculate Basic Premium RWFs for specific combinations
    total_proactiv= (df_proactiv['Basic Premium RWF'].sum()) / scale
    total_health = (df_health['Basic Premium RWF'].sum()) / scale
    


    # Calculate Basic Premium RWFs for specific combinations
    total_closed = (df_closed['Basic Premium RWF'].sum())/scale
    total_lost = (df_lost['Basic Premium RWF'].sum())/scale

    
    # Calculate Basic Premium RWFs for specific combinations
    total_closed_health = (df_closed_health['Basic Premium RWF'].sum())/scale
    total_closed_pro = (df_closed_pro['Basic Premium RWF'].sum())/scale

    # Calculate Basic Premium RWFs for specific combinations
    total_lost_health = (df_lost_health['Basic Premium RWF'].sum())/scale
    total_lost_pro = (df_lost_pro['Basic Premium RWF'].sum())/scale
    total_progess = (df_progress['Basic Premium RWF'].sum())/scale

    total_whales_pro = (df_whales_pro['Basic Premium RWF'].sum())/scale
    total_tigers_pro = (df_tigers_pro['Basic Premium RWF'].sum())/scale
    total_elephants_pro = (df_elephants_pro['Basic Premium RWF'].sum())/scale
    total_hares_pro = (df_hares_pro['Basic Premium RWF'].sum())/scale

    total_whales_health = (df_whales_health['Basic Premium RWF'].sum())/scale
    total_tigers_health = (df_tigers_health['Basic Premium RWF'].sum())/scale
    total_elephants_health = (df_elephants_health['Basic Premium RWF'].sum())/scale
    total_hares_health = (df_hares_health['Basic Premium RWF'].sum())/scale


    df["Employee Size"] = pd.to_numeric(df["Employee Size"], errors='coerce').fillna(0).astype(int)
    df["Dependents"] = pd.to_numeric(df["Targeted Lives (depentands) "], errors='coerce').fillna(0).astype(int)

    total_clients = df["Property"].nunique()
    total_mem = df["Employee Size"].sum()
    total_dependents = df["Dependents"].sum()
    total_lives = total_mem +total_dependents
    average_dep = total_mem/total_dependents
    average_pre = df["Basic Premium RWF"].mean()
    average_premium_per_life = total_pre/total_mem
    gwp_average = total_lives * average_premium_per_life / total_clients


    percent_closed_health = (total_closed_health/total_health)*100
    percent_closed_pro = (total_closed_pro/total_proactiv)*100
    percent_lost_health = (total_lost_health/total_health)*100
    percent_lost_pro = (total_lost_pro/total_proactiv)*100
    percent_closed = (total_closed/total_pre_scaled)*100
    percent_lost = (total_lost/total_pre_scaled)*100
    percent_progress = (total_progess/total_pre_scaled)*100


    # Scale the sums
    average_pre_scaled = average_pre/scale
    gwp_average_scaled = gwp_average/scale

    scaled = 1_000

    # Calculate key metrics
    lowest_premium = df['Basic Premium RWF'].min() /scaled
    highest_premium = df['Basic Premium RWF'].max() / scaling_factor
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

    # Function to display metrics in styled boxes
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<h3 class="custom-subheader">For All Sales</h3>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # Display metrics
    display_metric(col1, f"Total Expected Clients ({filter_description.strip()})", total_clients)
    display_metric(col2, f"Total Expected Sales ({filter_description.strip()})", f"RWF {total_pre_scaled:.0f} M")
    display_metric(col3, "Total Expected Principal Members", total_mem)

    # display_metric(col1, "Average Expected Sale Per Principal Member", f"RWF {average_pre_scaled:.0f}M")
    # display_metric(col2, "Average Expected Sale per Employer group", f"RWF {gwp_average_scaled:.0f} M")

    display_metric(col1, "Total Closed Sales", f"RWF {total_closed:.0f} M")
    display_metric(col2, "Total Lost Sales", f"RWF {total_lost:.0f} M",)
    display_metric(col3, "Percentage Closed Sales", value=f"{percent_closed:.1f} %")
    display_metric(col1, "Percentage Lost Sales", value=f"{percent_lost:.1f} %")
    display_metric(col2, "Percentage Sales in Progress", value=f"{percent_progress:.1f} %")

    st.markdown('<h3 class="custom-subheader">For Expected Health Insurance Sales by Client Segment</h3>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    display_metric(col1, "Expected Whales Sales", value=f"RWF {total_whales_health:.0f} M")
    display_metric(col2, "Expected Elephants Sales", value=f"RWF {total_elephants_health:.0f} M")
    display_metric(col3, "Expected Tigers Sales", value=f"RWF {total_tigers_health:.0f} M")
    display_metric(col4, "Expected Hares Sales", value=f"RWF {total_hares_health:.0f} M")


    st.markdown('<h3 class="custom-subheader">For Expected ProActiv Sales by Client Segment</h3>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    display_metric(col1, "Expected Whales Sales", value=f"RWF {total_whales_pro:.0f} M")
    display_metric(col2, "Expected Elephants Sales", value=f"RWF {total_elephants_pro:.0f} M")
    display_metric(col3, "Expected Tigers Sales", value=f"RWF {total_tigers_pro:.0f} M")
    display_metric(col4, "Expected Hares Sales", value=f"RWF {total_hares_pro:.0f} M")

   

   
    # Sidebar styling and logo
    st.markdown("""
        <style>
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .sidebar .sidebar-content h3 {
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

    
    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

    df["Expected Close Date"] = pd.to_datetime(df["Expected Close Date"], errors='coerce')
    df["Start Year"] = df["Expected Close Date"].dt.year

    colc1, colc2 = st.columns(2)
    # Sample function to format y-axis labels
    def millions(x, pos):
        'The two args are the value and tick position'
        return '%1.1fM' % (x * 1e-6)

    # Assuming df is already defined and contains the necessary data
    # Ensure 'Start Month' is in datetime format
    df['Expected Close Date'] = pd.to_datetime(df['Expected Close Date'], errors='coerce')

    # Group by day and Client Segment, then sum the Basic Premium RWF
    area_chart_total_insured = (
        df.groupby([df["Expected Close Date"].dt.strftime("%Y-%m-%d"), 'Client Segment'])['Basic Premium RWF']
        .sum()
        .reset_index(name='Basic Premium RWF')
    )

    # Sort by the Start Month
    area_chart_total_insured = area_chart_total_insured.sort_values("Expected Close Date")

    # Ensure 'Basic Premium RWF' is numeric
    area_chart_total_insured['Basic Premium RWF'] = pd.to_numeric(area_chart_total_insured['Basic Premium RWF'], errors='coerce')

    # Check if the DataFrame is empty before plotting
    if not area_chart_total_insured.empty:
  
            # Create the area chart for Basic Premium RWF
        fig1, ax1 = plt.subplots()

            # Pivot the DataFrame for easier plotting
        pivot_df_insured = area_chart_total_insured.pivot(index='Expected Close Date', columns='Client Segment', values='Basic Premium RWF').fillna(0)

            # Plot the stacked area chart
        pivot_df_insured.plot(kind='area', stacked=True, ax=ax1, color=custom_colors[:len(pivot_df_insured.columns)])

            # Remove the border around the chart
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)

            # Set x-axis title
        ax1.set_xlabel("Date", fontsize=9, color="gray")
        plt.xticks(rotation=45, fontsize=9, color="gray")

            # Set y-axis title
        ax1.set_ylabel("Basic Premium RWF", fontsize=9, color="gray")
        plt.yticks(fontsize=9, color="gray")

            # Format the y-axis
        formatter = FuncFormatter(millions)
        ax1.yaxis.set_major_formatter(formatter)

            # Set chart title
        st.markdown('<h3 class="custom-subheader">Total Expected Sales by Client Segment Over Time</h3>', unsafe_allow_html=True)

            # Display the chart in Streamlit
        st.pyplot(fig1)

    cols1,cols2 = st.columns(2)

    # Group data by "Start Month Year" and "Client Segment" and calculate the average Basic Premium RWF
    yearly_avg_premium = df.groupby(['Start Year', 'Client Segment'])['Basic Premium RWF'].sum().unstack().fillna(0)

    # Define custom colors

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
            xaxis_title="Start Year",
            yaxis_title="Basic Premium RWF",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Expected Yearly Sales by Client Segment</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)

    # Calculate the Basic Premium RWF by Client Segment
    int_premiums = df.groupby("Client Segment")["Basic Premium RWF"].sum().reset_index()
    int_premiums.columns = ["Client Segment", "Basic Premium RWF"]    

    with cols2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Expected Sales by Client Segment</h3>', unsafe_allow_html=True)

        # Create a donut chart
        fig = px.pie(int_premiums, names="Client Segment", values="Basic Premium RWF", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)

        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

 


    ccl1, ccl2 = st.columns(2)
    with ccl1:
        with st.expander("Yearly Average Sales by Client Segment"):
            st.dataframe(yearly_avg_premium.style.format(precision=2))
        


    cls1, cls2 = st.columns(2)

    # Group data by "Start Month" and "Channel" and sum the Basic Premium RWF
    monthly_premium = df.groupby(['Start Month', 'Client Segment'])['Basic Premium RWF'].sum().unstack().fillna(0)

    # Group data by "Start Month" to count the number of sales
    monthly_sales_count = df.groupby(['Start Month']).size()

    # Group by Expected Close Date Month and Intermediary and sum the Total lives
    monthly_lives = df.groupby(['Start Month', 'Client Segment'])['Total lives'].sum().unstack().fillna(0)

    # Define custom colors

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

        # Add a secondary y-axis for the count of sales
        fig_monthly_premium.add_trace(go.Scatter(
            x=monthly_sales_count.index,
            y=monthly_sales_count,
            mode='lines+markers',
            name='Number of Sales',
            yaxis='y2',
            line=dict(color='red', width=2),
            marker=dict(size=6, symbol='circle', color='red')
        ))

        # Set layout for the Basic Premium RWF chart
        fig_monthly_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Month",
            yaxis_title="Basic Premium RWF",
            yaxis2=dict(
                title="Number of Sales",
                overlaying='y',
                side='right'
            ),
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Basic Premium RWF chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Expected Monthly Sales by Client Segment</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)

    with cls2:
        fig_monthly_lives = go.Figure()

        for idx, Client_Segment in enumerate(monthly_lives.columns):
            fig_monthly_lives.add_trace(go.Bar(
                x=monthly_lives.index,
                y=monthly_lives[Client_Segment],
                name=Client_Segment,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        # Add a secondary y-axis for the count of sales
        fig_monthly_lives.add_trace(go.Scatter(
            x=monthly_sales_count.index,
            y=monthly_sales_count,
            mode='lines+markers',
            name='Number of Sales',
            yaxis='y2',
            line=dict(color='red', width=2),
            marker=dict(size=6, symbol='circle', color='red')
        ))

        # Set layout for the Total Lives chart
        fig_monthly_lives.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Month",
            yaxis_title="Total Lives Covered",
            yaxis2=dict(
                title="Number of Sales",
                overlaying='y',
                side='right'
            ),
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Total Lives chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Expected Lives Covered Monthly by Client Segment</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_lives, use_container_width=True)


    clm1, clm2 = st.columns(2)

    with clm1:
        # Create an expandable section for the table
        with st.expander("View Monthly Basic Premium RWF by Client Segment"):
            st.dataframe(monthly_premium.style.format(precision=2))

    with clm2:
        with st.expander("View Monthly Total Live covered by Client Segment"):
            st.dataframe(monthly_lives.style.format(precision=2))


    cul1, cul2 = st.columns(2)



    # Group by Property and Client Segment, then sum the Basic Premium RWF
    df_grouped = df.groupby(['Property', 'Client Segment'])['Basic Premium RWF'].sum().reset_index()

    # Get the top 10 clients by Basic Premium RWF
    top_10_clients = df_grouped.groupby('Property')['Basic Premium RWF'].sum().nlargest(15).reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Property'].isin(top_10_clients['Property'])]
    # Sort the client_df by Basic Premium RWF in descending order
    client_df = client_df.sort_values(by='Basic Premium RWF', ascending=False)

    with cul1:
        # Create the bar chart
        fig = go.Figure()

        # Add bars for each Client Segment
        for idx, Client_Segment in enumerate(client_df['Client Segment'].unique()):
            Client_Segment_data = client_df[client_df['Client Segment'] == Client_Segment]
            fig.add_trace(go.Bar(
                x=Client_Segment_data['Property'],
                y=Client_Segment_data['Basic Premium RWF'],
                name=Client_Segment,
                text=[f'{value/1e6:.0f}M' for value in Client_Segment_data['Basic Premium RWF']],
                textposition='auto',
                marker_color=custom_colors[idx % len(custom_colors)]
            ))

        fig.update_layout(
            barmode='group',
            yaxis_title="Basic Premium RWF",
            xaxis_title="Property",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 15 Expected Client Sales by Client Segment</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    culs1, culs2 = st.columns(2)
    with culs1:
        with st.expander("Client Premium by Client Segment"):
            st.dataframe(int_premiums.style.format(precision=2))



    # summary table
    st.markdown('<h3 class="custom-subheader">Month-Wise Sales By Client Segment Table</h3>', unsafe_allow_html=True)

    with st.expander("Summary_Table"):

        colors = ["#527853", "#F9E8D9", "#F7B787", "#EE7214", "#B99470"]
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("EarthyPalette", colors)
        # Create the pivot table
        sub_specialisation_Year = pd.pivot_table(
            data=df,
            values="Basic Premium RWF",
            index=["Client Segment"],
            columns="Start Month"
        )
        st.write(sub_specialisation_Year.style.background_gradient(cmap="YlOrBr"))
    

        
else:
    st.error("No data available for this selection")