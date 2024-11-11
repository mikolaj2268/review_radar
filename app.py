import streamlit as st
import sys
from src.pages import home_page

# Dictionary mapping page names to functions
PAGES = {
    "Home": home_page.home_page,
    # Add other page functions here when they are implemented
    # "Add Application": add_application_page,
    # "Refresh Database": refresh_database_page,
}

def main():
    st.sidebar.title("Options")
    selection = st.sidebar.selectbox(
        "Select a page", ["Home", "App Analysis"]
    )  # Page selection
    if selection in PAGES:
        page = PAGES[selection]  # Get the function responsible for the selected page
        page()  # Call the selected page's function
    else:
        st.write(f"{selection} page is not implemented yet.")

if __name__ == "__main__":
    sys.path.append("src")  # Add src to the path to easily import modules
    main()
