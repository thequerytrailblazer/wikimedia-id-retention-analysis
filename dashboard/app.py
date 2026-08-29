import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Wikimedia Indonesia - Retention Analytics",
    layout="wide"
)

# ------------------------------------------------------------------------------
# 2. DATA LOADING & PREPROCESSING
# ------------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/retention_cleaned.csv")
    df['start_date'] = pd.to_datetime(df['start_date'])
    return df

try:
    df_merged = load_data()
except Exception as e:
    st.error("Failed to load data/retention_cleaned.csv. Please ensure the file exists in the designated directory.")
    st.stop()

# ------------------------------------------------------------------------------
# 3. SIDEBAR FILTERS
# ------------------------------------------------------------------------------
st.sidebar.header("Analytics Filters")

# Date Filter
min_date = df_merged['start_date'].min().date()
max_date = df_merged['start_date'].max().date()

start_date_input, end_date_input = st.sidebar.date_input(
    "Event Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Cohort Filter
cohort_options = ["All"] + list(df_merged['user_cohort'].dropna().unique())
selected_cohort = st.sidebar.selectbox("Filter User Cohort", options=cohort_options)

# Filter Dataframe based on Sidebar Inputs
filtered_df = df_merged[
    (df_merged['start_date'].dt.date >= start_date_input) &
    (df_merged['start_date'].dt.date <= end_date_input)
]

if selected_cohort != "All":
    filtered_df = filtered_df[filtered_df['user_cohort'] == selected_cohort]

# ------------------------------------------------------------------------------
# 4. HEADER & KPI METRICS
# ------------------------------------------------------------------------------
st.title("Wikimedia Indonesia Program Analytics (2025–2026)")
st.markdown("Retention analytics dashboard and participant dynamics for Wikidata training sessions.")

st.divider()

# Compute Key Metrics
total_events = filtered_df['course'].nunique()
total_enrollments = len(filtered_df)
total_unique_users = filtered_df['username'].nunique()

# Calculate Retention
user_event_count = filtered_df.groupby('username')['course'].count()
repeat_users = (user_event_count > 1).sum()
retention_rate = (repeat_users / total_unique_users * 100) if total_unique_users > 0 else 0

# Display Metrics in 4 Columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Events", f"{total_events}", help="Total number of unique training courses held.")
col2.metric("Total Enrollments", f"{total_enrollments}", help="Total number of registrations across all events.")
col3.metric("Unique Participants", f"{total_unique_users}", help="Total number of distinct individual participants.")
col4.metric("Overall Retention Rate", f"{retention_rate:.1f}%", help="Percentage of participants who attended more than one event.")

st.divider()

# ------------------------------------------------------------------------------
# 5. VISUALIZATIONS SECTION
# ------------------------------------------------------------------------------
st.subheader("Cohort Retention & Participation Trends")

# Explanatory Guide Expander
with st.expander("Dashboard Documentation & Terminology Guide"):
    st.markdown("""
    **User Cohort Key Concepts:**
    * **New User:** Participants joining Wikimedia Indonesia training sessions for the first time.
    * **Existing User:** Participants who have registered or attended training sessions previously.

    **Chart Interpretation Guide:**
    * **Bar Chart (Retention Level per Cohort):** Displays how many participants from each cohort attended **only 1 event** versus those who returned for **more than 1 event** (retained participants).
    * **Donut Chart (Repeat Participants Composition):** Filters exclusively for retained participants (>1 event) to highlight whether participant retention is driven by new or existing members.
    * **Line Chart (Participation Trend Over Time):** Tracks participation volume across dates to reveal attendance fluctuations between cohorts.
    """)

tab1, tab2 = st.tabs(["Cohort Retention Overview", "Time Series Trend"])

with tab1:
    col_chart1, col_chart2 = st.columns(2)
    
    # Aggregation for Retention Bar Chart
    df_bar = filtered_df.groupby(['user_cohort', 'username'])['course'].count().reset_index()
    df_bar['participation_type'] = np.where(df_bar['course'] > 1, 'More than 1 event', 'Only 1 event')
    df_bar_summary = df_bar.groupby(['user_cohort', 'participation_type']).size().reset_index(name='count')

    with col_chart1:
        fig_bar = px.bar(
            df_bar_summary,
            x='user_cohort',
            y='count',
            color='participation_type',
            barmode='group',
            text='count',
            title='Retention Level per User Cohort',
            labels={'user_cohort': 'User Cohort', 'count': 'Unique Users', 'participation_type': 'Participation'},
            color_discrete_map={'Only 1 event': '#4C72B0', 'More than 1 event': '#55A868'}
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(template='plotly_white')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        # Aggregation for Donut Chart (Repeat Participants Only)
        df_repeat = df_bar[df_bar['participation_type'] == 'More than 1 event']
        df_pie_summary = df_repeat['user_cohort'].value_counts().reset_index()
        df_pie_summary.columns = ['user_cohort', 'count']

        fig_pie = px.pie(
            df_pie_summary,
            values='count',
            names='user_cohort',
            title='Repeat Participants Composition',
            hole=0.4,
            color='user_cohort',
            color_discrete_map={'Existing User': '#4C72B0', 'New User': '#E15759'}
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(template='plotly_white')
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    # Time Series Line Chart
    df_timeseries = filtered_df.groupby(['start_date', 'user_cohort']).size().reset_index(name='participant_count')
    
    fig_line = px.line(
        df_timeseries,
        x='start_date',
        y='participant_count',
        color='user_cohort',
        markers=True,
        title='Participation Trend Over Time',
        labels={'start_date': 'Event Date', 'participant_count': 'Participants', 'user_cohort': 'User Cohort'},
        color_discrete_map={'Existing User': '#4C72B0', 'New User': '#E15759'}
    )
    fig_line.update_traces(line=dict(width=2.5), marker=dict(size=7))
    fig_line.update_layout(template='plotly_white', hovermode='x unified')
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# ------------------------------------------------------------------------------
# 6. DATA EXPLORER & DOWNLOAD
# ------------------------------------------------------------------------------
st.subheader("Cleaned Dataset Explorer")
st.dataframe(filtered_df, use_container_width=True)

# Download CSV Button
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Filtered Data (CSV)",
    data=csv_data,
    file_name="filtered_retention_data.csv",
    mime="text/csv"
)