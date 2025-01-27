import streamlit as st
import sys
from src.pages import home_page, app_analysis_page

st.set_page_config(page_title="Review Radar", layout="wide")
PAGES = {
    "Home": home_page.home_page,
    "App Analysis": app_analysis_page.app_analysis_page,
}

def main():

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

    logo_path = "assets/images/1-rm-bg-white.png"
    st.sidebar.image(logo_path, use_container_width=True)


    selection = st.sidebar.selectbox(
        "Select a page", ["Home", "App Analysis"]
    ) 
    if selection in PAGES:
        page = PAGES[selection] 
        page()
    else:
        st.write(f"{selection} page is not implemented yet.")

if __name__ == "__main__":
    sys.path.append("src")
    main()
