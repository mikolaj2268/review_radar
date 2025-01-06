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

from src.functions.gui import create_st_button, get_file_path, create_st_button_with_color



def home_page():
    with st.sidebar:

        st.markdown("## Useful Links")
        database_link_dict = {
            "GitHub Repository": "https://github.com/mikolaj2268/review_radar",
            "Google Play API": "https://developers.google.com/android-publisher",
        }
        for link_text, link_url in database_link_dict.items():
            create_st_button_with_color(link_text, link_url, st_col=st.sidebar)

        st.markdown("## Models used to analyze sentiment")
        # Removed Pandas and NumPy, added model links
        software_link_dict = {
            "TextBlob": "https://textblob.readthedocs.io/en/dev/",
            "VADER Sentiment": "https://github.com/cjhutto/vaderSentiment",
            "DistilBERT Model": "https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english",
            "RoBERTa Model": "https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest?text=Covid+cases+are+increasing+fast%21"
        }
        for link_text, link_url in software_link_dict.items():
            create_st_button_with_color(link_text, link_url, st_col=st.sidebar)

    # Main content
    left_col, right_col = st.columns(2)  # 30% for image, 70% for text

    with right_col:
        # Add logo or main image
        img = Image.open("assets/images/WordCloud2.png") 
        st.image(img, width=650)

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
    st.markdown("## Usage: 4 Easy Steps to Improve Your App")

    # Create two columns for usage section
    left_col, right_col = st.columns([3, 1])

    with left_col:
        st.markdown(
            """
            1. **Go to App Analysis and Search Your App**: Navigate to the section and enter the name of the app.
            2. **Choose Date Range and Download the Data**: Specify the date range and click "Download Reviews".
            3. **Analyze the Reviews**: Dive into user feedback to understand their needs.
            4. **Improve Your App**: Use these insights to enhance your app and delight your customers!
            """
        )

    with right_col:
        st.image("assets/images/Usage_diagram.png", width=800)

    st.markdown("---")

    st.markdown(
        """
        ## Features
        - **Data Collection**: Automatically scrape reviews and ratings from Google Play.
        - **Sentiment Analysis**: Detect user sentiment using NLP techniques.
        - **Customizable Visualizations**: Generate insightful charts and graphs.
        """
    )

    st.markdown("---")

    # Sekcja autorów
    st.markdown("## Authors")

    # Mikołaj Mróz
    st.markdown("**Mikołaj Mróz**")
    create_st_button_with_color("GitHub: mikolaj2268", "https://github.com/mikolaj2268")
    create_st_button_with_color("Email: mikolaj2268@gmail.com", "mailto:mikolaj2268@gmail.com")
    st.write("")  # Dodanie przerwy

    # Michał Binda
    st.markdown("**Michał Binda**")
    create_st_button_with_color("GitHub: michal1701", "https://github.com/michal1701")
    create_st_button_with_color("Email: mich.binda@gmail.com", "mailto:mich.binda@gmail.com")




if __name__ == "__main__":
    home_page()