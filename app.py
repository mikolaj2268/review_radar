import streamlit as st
import sys
from src.pages import home_page, app_analysis_page

st.set_page_config(page_title="Review Radar", layout="wide")
# Dictionary mapping page names to functions
PAGES = {
    "Home": home_page.home_page,
    "App Analysis": app_analysis_page.app_analysis_page,
}

def main():
    # custom CSS for the background color
    st.markdown(
        """
        <style>
        .main {
            background-color: #E4E2DD;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Insert logo at the top of the sidebar
    logo_path = "assets/images/1-rm-bg-white.png"  # Adjust to the path of your logo file
    st.sidebar.image(logo_path, use_container_width=True)


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
