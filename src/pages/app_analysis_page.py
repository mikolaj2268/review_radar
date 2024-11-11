# app_analysis_page.py

import streamlit as st
from datetime import datetime, timedelta
from src.functions.app_analysis_functions import (
    get_db_connection,
    create_tables,
    search_and_select_app,
    check_and_fetch_reviews,
    display_reviews
)

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

    # Close the database connection
    conn.close()