import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Wikimedia Indonesia - Retention & Content Analytics",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/8/81/Wikimedia-logo.svg",
    layout="wide"
)

# ------------------------------------------------------------------------------
# 2. DATA LOADING & PREPROCESSING
# ------------------------------------------------------------------------------
@st.cache_data
def load_data():
    df_merged = pd.read_csv("data/retention_cleaned.csv")
    df_merged['start_date'] = pd.to_datetime(df_merged['start_date'])
    
    df_content = pd.read_csv("data/content_by_event_type.csv")
    df_event_breakdown = pd.read_csv("data/event_level_breakdown.csv")
    df_user_profiles = pd.read_csv("data/user_retention_profiles.csv")
    
    return df_merged, df_content, df_event_breakdown, df_user_profiles

try:
    df_merged, df_content, df_event_breakdown, df_user_profiles = load_data()
except Exception as e:
    st.error(f"Failed to load datasets from data/ directory: {e}")
    st.stop()

# ------------------------------------------------------------------------------
# 3. SIDEBAR FILTERS (WITH TRY-CATCH GUARDRAILS)
# ------------------------------------------------------------------------------
st.sidebar.header("Analytics Filters")

# Extract safe min/max date bounds
try:
    min_date = df_merged['start_date'].min().date()
    max_date = df_merged['start_date'].max().date()
except Exception:
    st.sidebar.error("Invalid date column structure in dataset.")
    st.stop()

# Interactive Date Picker with Tuple unpacking error handling
try:
    date_selection = st.sidebar.date_input(
        "Event Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Handle partial user input interaction
    if isinstance(date_selection, (tuple, list)) and len(date_selection) == 2:
        start_date_input, end_date_input = date_selection
    else:
        st.sidebar.warning("Please select both start and end dates in the date range picker.")
        st.stop()
        
except Exception:
    start_date_input, end_date_input = min_date, max_date

# Cohort Filter
try:
    cohort_options = ["All"] + list(df_merged['user_cohort'].dropna().unique())
    selected_cohort = st.sidebar.selectbox("Filter User Cohort", options=cohort_options)
except Exception:
    st.sidebar.error("Failed to populate user cohort options.")
    selected_cohort = "All"

# Filter Dataframe based on Sidebar Inputs
try:
    filtered_df = df_merged[
        (df_merged['start_date'].dt.date >= start_date_input) &
        (df_merged['start_date'].dt.date <= end_date_input)
    ]

    if selected_cohort != "All":
        filtered_df = filtered_df[filtered_df['user_cohort'] == selected_cohort]

    if filtered_df.empty:
        st.warning("No participant records match the selected filter criteria.")
        st.stop()
except Exception as e:
    st.error(f"Error filtering dataset: {e}")
    st.stop()

# ------------------------------------------------------------------------------
# 4. HEADER & KPI METRICS
# ------------------------------------------------------------------------------
logo_url = "https://upload.wikimedia.org/wikipedia/commons/9/96/Ikon_Data_dan_Teknologi_WMID_-_Warna.svg"

st.markdown(
    f"""
    <h1 style="display: flex; align-items: center; gap: 12px; margin-bottom: 0px;">
        <img src="{logo_url}" width="42" style="vertical-align: middle;">
        <span>Wikimedia Indonesia Program Analytics (2025–2026)</span>
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown("Retention analytics dashboard and participant dynamics for Wikidata training sessions.")

st.divider()

# Compute Key Metrics within error boundary
try:
    total_events = filtered_df['course'].nunique()
    total_enrollments = len(filtered_df)
    total_unique_users = filtered_df['username'].nunique()

    user_event_count = filtered_df.groupby('username')['course'].count()
    repeat_users = (user_event_count > 1).sum()
    retention_rate = (repeat_users / total_unique_users * 100) if total_unique_users > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events", f"{total_events}", help="Total number of unique training courses held.")
    col2.metric("Total Enrollments", f"{total_enrollments}", help="Total number of registrations across all events.")
    col3.metric("Unique Participants", f"{total_unique_users}", help="Total number of distinct individual participants.")
    col4.metric("Overall Retention Rate", f"{retention_rate:.1f}%", help="Percentage of participants who attended more than one event.")
except Exception as e:
    st.error("Failed to calculate key performance indicators.")

st.divider()

# ------------------------------------------------------------------------------
# 5. VISUALIZATIONS SECTION
# ------------------------------------------------------------------------------
st.subheader("Program Analytics & Content Impact")

with st.expander("Dashboard Documentation & Terminology Guide"):
    st.markdown("""
    **User Cohort Key Concepts:**
    * **New User:** Participants joining Wikimedia Indonesia training sessions for the first time ($\le 7$ days account age at first event).
    * **Existing User:** Participants who registered accounts $> 7$ days prior to their first event.

    **Event Typology Concepts:**
    * **Wikilatih:** Introductory training workshops focused on onboarding first-time contributors.
    * **Datathon:** Intensive editing competitions driving large-scale data volume.
    * **Kopdar:** Regional community gatherings focused on networking and retention.
    * **Pemagangan:** Structured internships for sustained skill development.
    """)

tab1, tab2, tab3, tab4 = st.tabs([
    "Cohort Retention Overview", 
    "Time Series Trend", 
    "Event Typology & Retention", 
    "Content Productivity per Editor"
])

# TAB 1: RETENTION OVERVIEW
with tab1:
    col_chart1, col_chart2 = st.columns(2)
    
    try:
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
            df_repeat = df_bar[df_bar['participation_type'] == 'More than 1 event']
            df_pie_summary = df_repeat['user_cohort'].value_counts().reset_index()
            df_pie_summary.columns = ['user_cohort', 'count']

            if not df_pie_summary.empty:
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
            else:
                st.info("No repeat participants available for selected criteria.")
    except Exception as e:
        st.error("Error generating Cohort Retention Overview charts.")

# TAB 2: TIME SERIES TREND (RETRIEVED FROM NOTEBOOK)
with tab2:
    try:
        df_timeseries = filtered_df.groupby(['start_date', 'user_cohort']).size().reset_index(name='participant_count')

        fig_line = px.line(
            df_timeseries,
            x='start_date',
            y='participant_count',
            color='user_cohort',
            markers=True,
            title='Participation Trend Over Time (New Users vs Existing Users)',
            labels={'start_date': 'Event Start Date', 'participant_count': 'Participant Count', 'user_cohort': 'User Cohort'},
            color_discrete_map={'Existing User': '#4C72B0', 'New User': '#E15759'}
        )
        fig_line.update_traces(line=dict(width=2.5), marker=dict(size=7))
        fig_line.update_layout(template='plotly_white', hovermode='x unified')
        st.plotly_chart(fig_line, use_container_width=True)
    except Exception as e:
        st.error("Error rendering Participation Trend Over Time chart.")

# TAB 3: EVENT TYPOLOGY & RETENTION
with tab3:
    col_type1, col_type2 = st.columns(2)
    
    with col_type1:
        try:
            cohort_by_type = pd.crosstab(
                filtered_df['event_type'], 
                filtered_df['user_cohort'], 
                normalize='index'
            ) * 100
            
            fig_type_comp = px.bar(
                cohort_by_type.reset_index(),
                x='event_type',
                y=['New User', 'Existing User'],
                title='Cohort Composition Breakdown by Event Format (%)',
                labels={'value': 'Percentage (%)', 'event_type': 'Event Format', 'variable': 'User Cohort'},
                barmode='stack',
                color_discrete_map={'New User': '#E15759', 'Existing User': '#4C72B0'},
                template='plotly_white'
            )
            st.plotly_chart(fig_type_comp, use_container_width=True)
        except Exception as e:
            st.error("Error rendering Cohort Composition breakdown.")

    with col_type2:
        try:
            df_sorted = filtered_df.sort_values(by=['username', 'start_date']).reset_index(drop=True)
            first_user_events = df_sorted.groupby('username').first().reset_index()
            user_event_counts = filtered_df.groupby('username')['start_date'].nunique().reset_index()
            user_event_counts.rename(columns={'start_date': 'total_events_attended'}, inplace=True)

            user_retention_profiles = pd.merge(first_user_events, user_event_counts, on='username')
            user_retention_profiles['is_repeat_user'] = user_retention_profiles['total_events_attended'] > 1

            repeat_rate_by_type = user_retention_profiles.groupby(['event_type', 'user_cohort']).agg(
                total_first_timers=('username', 'count'),
                repeat_users=('is_repeat_user', 'sum'),
                repeat_rate_pct=('is_repeat_user', lambda x: (x.sum() / x.count()) * 100)
            ).reset_index()

            fig_repeat = px.bar(
                repeat_rate_by_type,
                x='event_type',
                y='repeat_rate_pct',
                color='user_cohort',
                barmode='group',
                title='Returner Repeat Rate (%) by First Attended Event Format',
                labels={'repeat_rate_pct': 'Repeat Rate (%)', 'event_type': 'First Event Format', 'user_cohort': 'Cohort'},
                color_discrete_map={'New User': '#E15759', 'Existing User': '#4C72B0'},
                text_auto='.1f',
                template='plotly_white'
            )
            st.plotly_chart(fig_repeat, use_container_width=True)
        except Exception as e:
            st.error("Error rendering Repeat Rate chart.")

# TAB 4: CONTENT PRODUCTIVITY PER EDITOR
with tab4:
    try:
        fig_content = px.bar(
            df_content,
            x='event_type',
            y=['claims_per_editor', 'labels_per_editor', 'items_per_editor'],
            title='Normalized Content Output Metrics per Editor by Event Format (Log Scale)',
            labels={'value': 'Average Actions per Editor', 'event_type': 'Event Format', 'variable': 'Metric'},
            barmode='group',
            log_y=True,
            template='plotly_white'
        )
        st.plotly_chart(fig_content, use_container_width=True)
    except Exception as e:
        st.error("Error rendering Content Productivity chart.")

st.divider()

# ------------------------------------------------------------------------------
# 6. DATA EXPLORER & DOWNLOAD
# ------------------------------------------------------------------------------
st.subheader("Data Explorer")

explorer_tab1, explorer_tab2 = st.tabs(["Participant Activity Dataset", "Content Output by Event Type"])

with explorer_tab1:
    try:
        st.dataframe(filtered_df, use_container_width=True)
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Participant Data (CSV)",
            data=csv_data,
            file_name="filtered_retention_data.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error("Failed to render participant data table.")

with explorer_tab2:
    try:
        st.dataframe(df_content, use_container_width=True)
        csv_content = df_content.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Content Metrics (CSV)",
            data=csv_content,
            file_name="content_by_event_type.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error("Failed to render content output table.")

# ------------------------------------------------------------------------------
# 7. COPYRIGHT & LICENSING FOOTER
# ------------------------------------------------------------------------------
st.divider()

st.caption(
    """
    **Copyright & Licensing Information**  
    * **Data Attribution:** Datasets sourced from the [Wikimedia Outreach Dashboard - Wikimedia Indonesia Data and Technology Campaign 2025](https://outreachdashboard.wmflabs.org/campaigns/data_dan_teknologi_wikimedia_indonesia_2025/overview) and [Wikidata](https://www.wikidata.org/).  
    * **Data & Analytics License:** Licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).  
    * **Application Source Code:** Licensed under the [MIT License](https://opensource.org/licenses/MIT).  
    * © 2025–2026 HA | [The Query Trailblazer](https://github.com/thequerytrailblazer).
    """
)