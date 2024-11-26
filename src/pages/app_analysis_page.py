# src/pages/app_analysis_page.py

import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta
from collections import Counter
import torch
from transformers import pipeline
import tensorflow as tf
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import os
from tqdm import tqdm

from src.functions.app_analysis_functions import (
    get_db_connection,
    create_tables,
    search_and_select_app,
    check_and_fetch_reviews,
    display_reviews,
    preprocess_data,
    plot_score_distribution
)
from src.database_connection.db_utils import get_app_data

# Import sentiment analysis functions from model files
from src.models.textblob_model import analyze_sentiment_textblob
from src.models.vader_model import analyze_sentiment_vader
from src.models.roberta_model import analyze_sentiment_roberta


# Configure progress bar
def initialize_progress(total_steps):
    progress_bar = st.progress(0)
    status_text = st.empty()
    return progress_bar, status_text

def update_progress(progress_bar, status_text, current_step, total_steps, status_message="Processing"):
    progress = current_step / total_steps
    progress_bar.progress(progress)
    status_text.text(f"{status_message}: {current_step} / {total_steps}")

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

    # Define tabs
    tabs = st.tabs(["Data Downloading", "Sentiment Analysis", "Score Analysis", "Problems Identification"])

    with tabs[0]:
        st.header("Data Downloading")

        # Date range selection
        start_date_input = st.date_input(
            "Start date",
            value=datetime.now() - timedelta(days=30),
            key="start_date_input",
        )
        end_date_input = st.date_input(
            "End date",
            value=datetime.now(),
            key="end_date_input",
        )

        # Convert dates to datetime objects
        start_date = datetime.combine(start_date_input, datetime.min.time())
        end_date = datetime.combine(end_date_input, datetime.max.time())

        # Buttons to download reviews and perform analysis
        perform_analysis_button = st.button("Download reviews")
        stop_download_button = st.button("Stop downloading")

        # Initialize session state variables
        if 'analysis_result' not in st.session_state:
            st.session_state.analysis_result = None
        if 'stop_download' not in st.session_state:
            st.session_state.stop_download = False

        if selected_app and selected_app_id:
            if perform_analysis_button:
                # Reset stop_download flag
                st.session_state.stop_download = False

                # Define placeholders for messages
                status_placeholder = st.empty()
                missing_placeholder = st.empty()

                # Check and fetch missing reviews
                check_and_fetch_reviews(
                    conn,
                    selected_app,
                    selected_app_id,
                    start_date,
                    end_date,
                    status_placeholder,
                    missing_placeholder
                )

                # Display reviews
                st.session_state.analysis_result = display_reviews(conn, selected_app, start_date, end_date)
            elif stop_download_button:
                # Set stop_download flag to True
                st.session_state.stop_download = True
                st.info("Stopping download and performing analysis with existing data...")

                # Display reviews from existing data
                st.session_state.analysis_result = display_reviews(conn, selected_app, start_date, end_date)
        elif perform_analysis_button or stop_download_button:
            st.warning("Please select an application before proceeding.")

        # Display analysis results if available
        if st.session_state.analysis_result is not None and not st.session_state.analysis_result.empty:
            st.write(f"### Reviews for **{selected_app}**:")
            st.dataframe(st.session_state.analysis_result)
        else:
            st.write("No analysis performed yet or no reviews found for the selected date range.")

    with tabs[1]:
        st.header("Sentiment Analysis")

        if selected_app:
            # Retrieve data for the selected app
            app_data = get_app_data(conn, selected_app)

            if not app_data.empty:
                # Preprocess the data
                app_data = preprocess_data(app_data)

                # Convert 'at' column to datetime.date
                app_data['at'] = pd.to_datetime(app_data['at']).dt.date

                # Add date slider for filtering
                st.sidebar.write("Filter by Date:")
                min_date = app_data['at'].min()
                max_date = app_data['at'].max()

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

                # Display the selected date range
                st.write(f"Selected Date Range: {selected_date_range[0]} to {selected_date_range[1]}")

                # Filter data based on the selected date range
                filtered_data = app_data[
                    (app_data['at'] >= selected_date_range[0]) &
                    (app_data['at'] <= selected_date_range[1])
                ]

                # Filters for scores
                st.sidebar.write("Filter by Scores:")
                score_filters = {
                    1: st.sidebar.checkbox("1 Star", value=True),
                    2: st.sidebar.checkbox("2 Stars", value=True),
                    3: st.sidebar.checkbox("3 Stars", value=True),
                    4: st.sidebar.checkbox("4 Stars", value=True),
                    5: st.sidebar.checkbox("5 Stars", value=True),
                }

                # Filter data based on selected scores
                selected_scores = [score for score, selected in score_filters.items() if selected]
                filtered_data = filtered_data[filtered_data['score'].isin(selected_scores)]

                # Model selection and perform analysis button
                st.write("### Select Sentiment Analysis Model")
                model_options = ["TextBlob", "VADER", "RoBERTa"]
                selected_model = st.radio("Choose a sentiment analysis model:", model_options)

                perform_analysis = st.button("Perform Analysis")

                if perform_analysis:
                    if not filtered_data.empty:
                        total_records = len(filtered_data)
                        progress_bar, status_text = initialize_progress(total_records)
                        current_step = 0

                        # Perform sentiment analysis using the selected model
                        if selected_model == "TextBlob":
                            sentiments = []
                            for text in tqdm(filtered_data['content'], desc="Analyzing with TextBlob"):
                                sentiments.append(analyze_sentiment_textblob(text))
                                current_step += 1
                                update_progress(progress_bar, status_text, current_step, total_records, "Processing TextBlob")
                            filtered_data['sentiment'] = sentiments
                        elif selected_model == "VADER":
                            sentiments = []
                            for text in tqdm(filtered_data['content'], desc="Analyzing with VADER"):
                                sentiments.append(analyze_sentiment_vader(text))
                                current_step += 1
                                update_progress(progress_bar, status_text, current_step, total_records, "Processing VADER")
                            filtered_data['sentiment'] = sentiments
                        elif selected_model == "RoBERTa":
                            sentiments = []
                            for text in tqdm(filtered_data['content'], desc="Analyzing with RoBERTa"):
                                sentiments.append(analyze_sentiment_roberta(text))
                                current_step += 1
                                update_progress(progress_bar, status_text, current_step, total_records, "Processing RoBERTa")
                            filtered_data['sentiment'] = sentiments
                        else:
                            st.error("Selected model is not supported.")

                        # Update the progress bar to full
                        progress_bar.progress(1.0)
                        status_text.text("Analysis Completed!")

                        # Display sentiment analysis results
                        st.write("### Sentiment Analysis Results")
                        st.dataframe(filtered_data[['content', 'sentiment']])

                        # Plot sentiment distribution
                        sentiment_counts = filtered_data['sentiment'].value_counts()
                        fig = px.bar(
                            sentiment_counts,
                            x=sentiment_counts.index,
                            y=sentiment_counts.values,
                            labels={'x': 'Sentiment', 'y': 'Count'},
                            title='Sentiment Distribution'
                        )
                        st.plotly_chart(fig)
                    else:
                        st.write("No data available for the selected filters.")
            else:
                st.write("No reviews available for the selected app.")
        else:
            st.write("Please select an application to perform sentiment analysis.")

    with tabs[2]:
        st.header("Score Analysis")
        # Plot score distribution
        if 'filtered_data' in locals() and not filtered_data.empty:
            score_fig = plot_score_distribution(filtered_data)
            st.plotly_chart(score_fig)
        else:
            st.warning("No data available to plot the score distribution.")

    with tabs[3]:
        st.header("Problems Identification")
        # Identify common problems based on keywords
        if 'filtered_data' in locals() and not filtered_data.empty:
            keywords = ["crash", "bug", "error", "slow", "freeze", "issue"]
            filtered_data['issues'] = filtered_data['content'].apply(
                lambda x: ', '.join([kw for kw in keywords if kw in x.lower()])
            )
            issues = filtered_data['issues'].dropna().tolist()
            issue_counts = Counter(', '.join(issues).split(', '))
            issue_df = pd.DataFrame(issue_counts.items(), columns=['Issue', 'Count']).sort_values(by='Count', ascending=False)

            if not issue_df.empty:
                st.write("### Common Problems Identified")
                st.dataframe(issue_df)

                # Plot frequency of issues
                fig = px.bar(issue_df, x='Issue', y='Count', title='Common Problems in App Reviews')
                st.plotly_chart(fig)
            else:
                st.write("No common problems identified based on the selected filters.")
        else:
            st.write("No data available for problem identification based on the selected filters.")

    # Close the database connection
    conn.close()