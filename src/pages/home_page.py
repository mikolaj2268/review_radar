# -*- coding: utf-8 -*-
"""
  ReviewRadar Application
  Created by Mikołaj Mroz

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

from functions.gui import create_st_button, get_file_path


def home_page():

    left_col, right_col = st.columns(2)

    # Add logo or main image
    img = Image.open(get_file_path("review_radar_logo.png", dir_path="./data"))
    right_col.image(img, output_format="PNG")

    left_col.markdown("# ReviewRadar")
    left_col.markdown("### Explore and analyze app reviews with ease")
    left_col.markdown("**Created by Mikołaj Mroz**")
    left_col.markdown("Analyze user sentiment and app performance trends to make data-driven decisions.")

    # Sidebar links
    database_link_dict = {
        "GitHub Repository": "https://github.com/mikolaj2268/review_radar",
        "Google Play API": "https://developers.google.com/android-publisher",
    }

    st.sidebar.markdown("## Useful Links")
    for link_text, link_url in database_link_dict.items():
        create_st_button(link_text, link_url, st_col=st.sidebar)

    st.markdown("---")

    # Main content
    st.markdown(
        """
        ### About ReviewRadar
        ReviewRadar is a comprehensive tool designed to help developers and users analyze reviews of mobile applications available on Google Play. By leveraging sentiment analysis and trend detection, ReviewRadar enables you to:
        
        - **Analyze trends** in user feedback over time.
        - **Compare app ratings** with other apps or across different time periods.
        - **Identify critical issues** mentioned in reviews.
        - **Explore common themes** using keyword extraction.

        ReviewRadar integrates modern tools and APIs to ensure accurate and actionable insights for app developers and users alike.
        """
    )

    # Features
    left_col, right_col = st.columns(2)

    left_col.markdown(
        """
        ### Features
        - **Data Collection**: Automatically scrape reviews and ratings from Google Play.
        - **Sentiment Analysis**: Detect user sentiment using NLP techniques.
        - **Customizable Visualizations**: Generate insightful charts and graphs.
        - **Comparison Tool**: Compare reviews with stock performance data for apps like Netflix, Spotify, and more.
        """
    )

    right_col.markdown(
        """
        ### Usage
        - **Home Page:** Welcome and overview of the application.
        - **Explore Reviews:** Analyze reviews and ratings for a selected app.
        - **Trends Analysis:** View trends in sentiment over time or after updates.
        - **Keyword Insights:** Identify frequently mentioned terms in user comments.
        - **Database Queries:** Query the database for specific insights or data export.
        """
    )

    st.markdown("---")

    # Contact and credits
    left_info_col, right_info_col = st.columns(2)

    left_info_col.markdown(
        """
        ### Author
        - **Mikołaj Mroz**
        - GitHub: [mikolaj2268](https://github.com/mikolaj2268)
        - Email: <mikolaj.mroz@example.com>
        """
    )

    right_info_col.markdown(
        """
        ### License
        - Apache License 2.0
        """
    )

    right_info_col.markdown(
        """
        ### Acknowledgments
        - Google Play API
        - Open Source Libraries: Pandas, NumPy, Streamlit, Matplotlib
        """
    )