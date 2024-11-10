# -*- coding: utf-8 -*-
"""
  ReviewRadar Application
  Created by Mikołaj Mroz and Michał Binda

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

import streamlit as st
from PIL import Image

from src.functions.gui import create_st_button, get_file_path

st.set_page_config(layout="wide")

def home_page():
    # Sidebar links
    st.sidebar.title("Navigation")
    st.sidebar.markdown("## Useful Links")
    database_link_dict = {
        "GitHub Repository": "https://github.com/mikolaj2268/review_radar",
        "Google Play API": "https://developers.google.com/android-publisher",
    }
    for link_text, link_url in database_link_dict.items():
        create_st_button(link_text, link_url, st_col=st.sidebar)



    st.sidebar.markdown("## Software-Related Links")
    software_link_dict = {
        "Pandas": "https://pandas.pydata.org",
        "NumPy": "https://numpy.org",
        "Streamlit": "https://streamlit.io",
    }
    for link_text, link_url in software_link_dict.items():
        create_st_button(link_text, link_url, st_col=st.sidebar)

    # Main content
    left_col, right_col = st.columns(2)  # 30% dla obrazu, 70% dla tekstu

    with right_col:
        # Add logo or main image
        img = Image.open("assets/logo/logo.png")  # Zamień na swoją ścieżkę
        st.image(img, width=250)

    with left_col:
        st.markdown(
            """
            # ReviewRadar
            ### Explore and analyze app reviews with ease
            **Created by Mikołaj Mróz and Michał Binda**
            
            Analyze user sentiment and app performance trends to make data-driven decisions.
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown(
        """
        ## About ReviewRadar
        ReviewRadar is a comprehensive tool designed to help developers and users analyze reviews of mobile applications available on Google Play. By leveraging sentiment analysis and trend detection, ReviewRadar enables you to:
        
        - **Analyze trends** in user feedback over time.
        - **Compare app ratings** with other apps or across different time periods.
        - **Identify critical issues** mentioned in reviews.
        - **Explore common themes** using keyword extraction.

        ReviewRadar integrates modern tools and APIs to ensure accurate and actionable insights for app developers and users alike.
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Section: Usage
    st.markdown(
        """
        ## Usage: 4 Easy Steps to Improve Your App
        1. **Go to App Analysis**: Navigate to the section and start your journey.
        2. **Search Your App**: Enter the name of the app and specify the date range.
        3. **Analyze the Reviews**: Dive into user feedback to understand their needs.
        4. **Improve Your App**: Use these insights to enhance your app and delight your customers!
        """
    )

    st.markdown("---")
    
    st.markdown(
        """
        ## Features
        - **Data Collection**: Automatically scrape reviews and ratings from Google Play.
        - **Sentiment Analysis**: Detect user sentiment using NLP techniques.
        - **Customizable Visualizations**: Generate insightful charts and graphs.
        - **Comparison Tool**: Compare reviews with stock performance data for apps like Netflix, Spotify, and more.
        """
    )

    st.markdown("---")

    st.markdown(
        """
        ## Authors
        **Mikołaj Mróz**
        - GitHub: [mikolaj2268](https://github.com/mikolaj2268)
        - Email: <mikolaj2268@gmail.com>\n
        **Michał Binda**
        - GitHub: [michal1701](https://github.com/michal1701)
        - Email: <mich.binda@gmail.com>
        """
    )

    st.markdown("---")

    st.markdown(
        """
        ## Acknowledgments
        - Google Play API
        - Open Source Libraries: Pandas, NumPy, Streamlit, Matplotlib
        """
    )


if __name__ == "__main__":
    home_page()