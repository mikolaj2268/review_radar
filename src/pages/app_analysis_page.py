# app_analysis_page.py
import re
from typing import Counter
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta
from src.functions.app_analysis_functions import (
    get_db_connection,
    create_tables,
    search_and_select_app,
    check_and_fetch_reviews,
    display_reviews,
    preprocess_data,
    plot_content_length_distribution,
    plot_score_distribution
)
from src.database_connection.db_utils import get_reviews_for_app, get_app_data

def app_analysis_page():
    st.title("App Reviews Analysis")

    # Connect to the database
    conn = get_db_connection()
    create_tables(conn)

    # Sidebar filters
    st.sidebar.title("Filters")

    # Application search
    search_query = st.sidebar.text_input("Search for an application")

    # Application selection logic
    selected_app = None
    selected_app_id = None

    if search_query:
        search_results = search_and_select_app(search_query)
        if search_results:
            app_options = [f"{app['title']} (ID: {app['appId']})" for app in search_results]
            selected_app_option = st.sidebar.selectbox("Select an application from search results", app_options)
            
            if selected_app_option:
                selected_index = app_options.index(selected_app_option)
                chosen_app = search_results[selected_index]
                selected_app = chosen_app['title']
                selected_app_id = chosen_app['appId']
        else:
            st.sidebar.write(f"No apps found matching '{search_query}'.")
    else:
        st.sidebar.write("Please enter an application name to search.")

    # Date range selection (below the app selection)
    start_date_input = st.sidebar.date_input(
        "Start date",
        value=datetime.now() - timedelta(days=30),
        key="start_date_input",
    )
    end_date_input = st.sidebar.date_input(
        "End date",
        value=datetime.now(),
        key="end_date_input",
    )

    # Convert date inputs to datetime objects
    start_date = datetime.combine(start_date_input, datetime.min.time())
    end_date = datetime.combine(end_date_input, datetime.max.time())

    # "Download Reviews and Perform Analysis" button in the sidebar
    perform_analysis_button = st.sidebar.button("Download reviews and perform analysis")

    # "Stop Downloading and Perform Analysis" button in the sidebar
    stop_download_button = st.sidebar.button("Stop downloading and perform analysis")

    # Initialize session state variables
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'stop_download' not in st.session_state:
        st.session_state.stop_download = False

    if selected_app and selected_app_id:
        if perform_analysis_button:
            # Reset stop_download flag
            st.session_state.stop_download = False

            # Check existing reviews and fetch missing ones
            check_and_fetch_reviews(conn, selected_app, selected_app_id, start_date, end_date)

            # Display reviews
            st.session_state.analysis_result = display_reviews(conn, selected_app, start_date, end_date)
        elif stop_download_button:
            # Set stop_download flag to True to interrupt the downloading process
            st.session_state.stop_download = True
            st.info("Stopping download and performing analysis with existing data...")

            # Display reviews with existing data
            st.session_state.analysis_result = display_reviews(conn, selected_app, start_date, end_date)
    elif perform_analysis_button or stop_download_button:
        st.warning("Please select an application before proceeding.")

    # Display analysis result if available and not empty
    if st.session_state.analysis_result is not None and not st.session_state.analysis_result.empty:
        st.write(f"### Reviews for **{selected_app}**:")
        st.dataframe(st.session_state.analysis_result)
    else:
        st.write("No analysis performed yet or no reviews found for the selected date range.")
    
    # get the data for the selected app
    app_data = get_app_data(conn, selected_app)
    # preprocess the data
    app_data = preprocess_data(app_data)
    # content length distribution

    # Add date slider for filtering by date
    st.sidebar.write("Filter by Date:")
    min_date = app_data['date'].min()
    max_date = app_data['date'].max()
    if min_date < max_date:
        selected_date_range = st.sidebar.slider(
            "Select Date Range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)
        )
    else:
        st.sidebar.warning("Not enough data to display the date range slider.")
        selected_date_range = (min_date, max_date)
    #display the dates
    st.write(f"Selected Date Range: {selected_date_range[0]} to {selected_date_range[1]}")
    # AttributeError: 'float' object has no attribute 'date'

    # Filter the data based on selected date range
    filtered_data = app_data[(app_data['date'] >= selected_date_range[0]) & (app_data['date'] <= selected_date_range[1])]

        # Add checkboxes for filtering by scores
    st.sidebar.write("Filter by Scores:")
    score_filters = {
        1: st.sidebar.checkbox("1 Star", value=True),
        2: st.sidebar.checkbox("2 Stars", value=True),
        3: st.sidebar.checkbox("3 Stars", value=True),
        4: st.sidebar.checkbox("4 Stars", value=True),
        5: st.sidebar.checkbox("5 Stars", value=True),
    }

    # Add multiselect for filtering by app version
    st.sidebar.write("Filter by App Version:")
    app_data['app_version'] = app_data['app_version'].fillna('Unknown')
    app_versions = sorted(app_data['app_version'].unique(), reverse=True)
    selected_versions = st.sidebar.multiselect("Select App Versions", app_versions, default=app_versions)

    # Filter the data based on selected scores
    selected_scores = [score for score, selected in score_filters.items() if selected]
    filtered_data = app_data[app_data['score'].isin(selected_scores)]

    # Plot the distribution of scores in streamlit
    score_fig = plot_score_distribution(filtered_data)
    st.plotly_chart(score_fig)
    
    # plot the distribution of content length in streamlit
    fig = plot_content_length_distribution(filtered_data)
    st.plotly_chart(fig)

    conn.close()