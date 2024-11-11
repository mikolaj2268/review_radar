# main_app.py

import streamlit as st
from src.database_connection.db_utils import (
    get_db_connection,
    get_app_names,
    get_reviews_for_app,
    create_reviews_table,
    get_app_id
)
from src.functions.scraper import select_app, scrape_and_store_reviews
from datetime import datetime

def main():
    st.title("Google Play App Reviews Explorer")

    # Connect to the database
    conn = get_db_connection()
    create_reviews_table(conn)

    # Sidebar options
    st.sidebar.title("Options")
    page = st.sidebar.selectbox(
        "Select a page", ["Home", "Add Application", "Refresh Database"]
    )

    if page == "Home":
        st.header("Home")

        app_names = get_app_names(conn)
        search_query = st.text_input("Search for an application")

        if search_query:
            matching_apps = [
                app for app in app_names if search_query.lower() in app.lower()
            ]

            if matching_apps:
                selected_app = st.selectbox("Select an application", matching_apps)

                if selected_app:
                    reviews_df = get_reviews_for_app(conn, selected_app)

                    if not reviews_df.empty:
                        st.write(f"### Reviews for **{selected_app}**:")
                        st.dataframe(reviews_df)
                    else:
                        st.write(f"No reviews found for **{selected_app}**.")
            else:
                st.write("No matching applications found.")
        else:
            st.write("Please enter an application name to search.")

    elif page == "Add Application":
        st.header("Add Applications to Fetch Reviews")

        # Initialize app list in session state
        if "app_list" not in st.session_state:
            st.session_state.app_list = []

        # Add new app
        st.subheader("Add a New Application")
        new_app_name = st.text_input(
            "Enter the name of the app to add", key="new_app_name"
        )

        if new_app_name:
            search_results = select_app(new_app_name)
            if search_results:
                app_options = [
                    f"{app['title']} (ID: {app['appId']})" for app in search_results
                ]
                selected_index = st.selectbox(
                    "Select the app you want to add",
                    range(len(app_options)),
                    format_func=lambda x: app_options[x],
                    key="app_selectbox",
                )
                chosen_app = search_results[selected_index]
                if st.button("Add Selected App to List"):
                    # Check if app is already in the list
                    if (chosen_app["title"], chosen_app["appId"]) not in st.session_state.app_list:
                        st.session_state.app_list.append(
                            (chosen_app["title"], chosen_app["appId"])
                        )
                        st.success(f"Added '{chosen_app['title']}' to the list.")
                        # Inform the user to clear the input field manually if desired
                        st.info("You can clear the input field to add another app.")
                    else:
                        st.warning(f"'{chosen_app['title']}' is already in the list.")
            else:
                st.write(f"No apps found matching '{new_app_name}'.")
        else:
            st.write("Please enter an application name to search.")

        # Display current app list with remove buttons
        if st.session_state.app_list:
            st.subheader("Current App List")
            for idx, (app_name, app_id) in enumerate(st.session_state.app_list):
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.write(f"{idx + 1}. {app_name} (ID: {app_id})")
                with col2:
                    if st.button("Remove", key=f"remove_{app_id}"):
                        st.session_state.app_list.pop(idx)
                        st.success(f"Removed '{app_name}' from the list.")
        else:
            st.write("No apps selected yet.")

        # Confirm app list
        if st.session_state.app_list:
            proceed = st.checkbox("I accept this list and want to proceed")

            if proceed:
                # Date range inputs
                st.subheader("Select Date Range for Reviews")
                start_date_input = st.date_input(
                    "Start date (leave blank to fetch from the latest date in the database)",
                    key="start_date_input",
                )
                end_date_input = st.date_input(
                    "End date (leave blank for today's date)",
                    value=datetime.now(),
                    key="end_date_input",
                )

                # Convert date inputs to datetime objects or set to None
                start_date = (
                    datetime.combine(start_date_input, datetime.min.time())
                    if start_date_input
                    else None
                )
                end_date = (
                    datetime.combine(end_date_input, datetime.max.time())
                    if end_date_input
                    else None
                )

                # Fetch button
                if st.button("Fetch Reviews for All Apps in the List"):
                    st.write("Fetching reviews for selected apps:")
                    app_results = []  # To store results for each app
                    for app_name, app_id in st.session_state.app_list:
                        # Create a placeholder for progress messages
                        progress_placeholder = st.empty()

                        # Fetch reviews with progress messages
                        total_reviews_fetched, start_date_fetched, end_date_fetched = scrape_and_store_reviews(
                            app_name,
                            app_id,
                            conn,
                            progress_placeholder=progress_placeholder,
                            start_date=start_date,
                            end_date=end_date,
                            country="us",
                            language="en",
                        )
                        # Store results
                        app_results.append({
                            'app_name': app_name,
                            'start_date': start_date_fetched,
                            'end_date': end_date_fetched,
                            'total_reviews': total_reviews_fetched
                        })
                    st.success("Review fetching completed for all apps.")

                    # Display summary
                    st.subheader("Summary of Fetch:")
                    for result in app_results:
                        st.write(f"**{result['app_name']}**")
                        st.write(f"Date range: {result['start_date'].strftime('%Y-%m-%d')} to {result['end_date'].strftime('%Y-%m-%d')}")
                        st.write(f"Total new reviews fetched: {result['total_reviews']}")
                        st.write("---")

                    st.session_state.app_list = []  # Clear the app list after fetching
        else:
            st.write("Please add apps to the list before proceeding.")

    elif page == "Refresh Database":
        st.header("Refresh All Apps in the Database")

        if st.button("Refresh All Apps"):
            # Fetch distinct app names from the database
            apps_in_db = get_app_names(conn)

            if not apps_in_db:
                st.write("No apps found in the database to refresh.")
            else:
                st.write("Refreshing reviews for apps in the database:")
                app_results = []  # To store results for each app
                for app_name in apps_in_db:
                    # Create a placeholder for progress messages
                    progress_placeholder = st.empty()

                    app_id = get_app_id(app_name)
                    if app_id:
                        # Fetch reviews with progress messages
                        total_reviews_fetched, start_date, end_date = scrape_and_store_reviews(
                            app_name,
                            app_id,
                            conn,
                            progress_placeholder=progress_placeholder,
                            country="us",
                            language="en",
                        )

                        # Store results
                        app_results.append({
                            'app_name': app_name,
                            'start_date': start_date,
                            'end_date': end_date,
                            'total_reviews': total_reviews_fetched
                        })
                    else:
                        progress_placeholder.write(
                            f"**Could not find app ID for {app_name}. Skipping.**"
                        )
                st.success("All apps have been refreshed.")

                # Display summary
                st.subheader("Summary of Refresh:")
                for result in app_results:
                    st.write(f"**{result['app_name']}**")
                    st.write(f"Date range: {result['start_date'].strftime('%Y-%m-%d')} to {result['end_date'].strftime('%Y-%m-%d')}")
                    st.write(f"Total new reviews fetched: {result['total_reviews']}")
                    st.write("---")
        else:
            st.write("Click the button above to refresh all apps in the database.")

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
