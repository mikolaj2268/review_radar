import streamlit as st
from datetime import datetime
from src.database_connection.db_utils import (
    get_db_connection,
    get_app_names,
    get_reviews_for_app,
    get_app_id
)

def choose_app_page():
    st.title("Choose App")

    # Establish database connection
    conn = get_db_connection()

    # Input for searching apps
    search_query = st.text_input("Search for an application")

    # Track if the user has completed any actions
    action_completed = False

    if search_query:
        # Fetch app names from the database
        app_names = get_app_names(conn)

        # Filter matching apps
        matching_apps = [
            app for app in app_names if search_query.lower() in app.lower()
        ]

        if matching_apps:
            # Dropdown for matching apps
            selected_app = st.selectbox("Select an application", matching_apps)

            if selected_app:
                # Show reviews for the selected app
                reviews_df = get_reviews_for_app(conn, selected_app)

                if not reviews_df.empty:
                    st.write(f"### Reviews for **{selected_app}**:")
                    st.dataframe(reviews_df)
                else:
                    st.write(f"No reviews found for **{selected_app}**.")
        else:
            st.write("No matching applications found in the database.")
            # Option to fetch app data if it's not in the database
            app_id = get_app_id(search_query)
            if app_id:
                st.write(f"App ID for '{search_query}': {app_id}")
                if st.button(f"Add '{search_query}' to database"):
                    st.success(f"Data for '{search_query}' has been successfully added to the database.")
                    action_completed = True
            else:
                st.write("No matching app found on Google Play.")
    else:
        st.write("Please enter an application name to search.")
    action_completed = True
    # Show "Go to Home Page" button if an action is completed
    if action_completed:
        if st.button("Go to Home Page"):
            st.experimental_set_query_params(page="Home")


# Temporary main function for standalone testing
if __name__ == "__main__":
    choose_app_page()