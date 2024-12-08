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
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from src.functions.app_analysis_functions import (
    get_db_connection,
    create_tables,
    search_and_select_app,
    check_and_fetch_reviews,
    display_reviews,
    preprocess_data,
    plot_score_distribution,
    generate_ngrams
)
from src.database_connection.db_utils import get_app_data

# Import sentiment analysis functions from model files
from src.models.textblob_model import analyze_sentiment_textblob
from src.models.vader_model import analyze_sentiment_vader
from src.models.roberta_model import analyze_sentiment_roberta
from src.models.distilbert_model import analyze_sentiment_distilbert


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

    selected_app = None
    selected_app_id = None
    selected_app_icon = None

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
                selected_app_icon = chosen_app.get('icon', None)
        else:
            st.sidebar.write(f"No apps found matching '{search_query}'.")
    else:
        st.sidebar.write("Please enter an application name to search.")

    # Define tabs
    tabs = st.tabs(["Data Downloading", "Sentiment Analysis", "Score Analysis", "Problems Identification"])

    with tabs[0]:
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

        if 'analysis_result' not in st.session_state:
            st.session_state.analysis_result = None
        if 'stop_download' not in st.session_state:
            st.session_state.stop_download = False

        if selected_app and selected_app_id:
            if perform_analysis_button:
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
                st.session_state.stop_download = True
                st.info("Stopping download and performing analysis with existing data...")
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
        if selected_app:
            app_data = get_app_data(conn, selected_app)
            if not app_data.empty:
                app_data = preprocess_data(app_data)
                app_data['at'] = pd.to_datetime(app_data['at']).dt.date

                # Date slider in sidebar
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

                analysis_data = st.session_state.get('analysis_data', None)
                analyzed_date_range = st.session_state.get('analyzed_date_range', None)

                can_filter_existing = False
                if analysis_data is not None and analyzed_date_range is not None:
                    # Check if selected_date_range is within analyzed_date_range
                    if selected_date_range[0] >= analyzed_date_range[0] and selected_date_range[1] <= analyzed_date_range[1]:
                        can_filter_existing = True

                # Filters for scores
                st.sidebar.write("Filter by Scores:")
                score_filters = {
                    1: st.sidebar.checkbox("1 Star", value=True),
                    2: st.sidebar.checkbox("2 Stars", value=True),
                    3: st.sidebar.checkbox("3 Stars", value=True),
                    4: st.sidebar.checkbox("4 Stars", value=True),
                    5: st.sidebar.checkbox("5 Stars", value=True),
                }
                selected_scores = [score for score, selected in score_filters.items() if selected]

                st.write("### Select Sentiment Analysis Model")
                model_options = ["TextBlob", "VADER", "DistilBERT", "RoBERTa"]
                selected_model = st.radio("Available models:", model_options)

                perform_analysis = st.button("Perform Analysis")

                def initialize_progress(total_steps):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    return progress_bar, status_text

                def update_progress(progress_bar, status_text, current_step, total_steps, status_message="Processing"):
                    progress = current_step / total_steps
                    progress_bar.progress(progress)
                    status_text.text(f"{status_message}: {current_step} / {total_steps}")

                def run_sentiment_analysis(model_function, model_name):
                    results = []
                    total_records = len(final_filtered_data)
                    progress_bar, status_text = initialize_progress(total_records)
                    for i, text in enumerate(final_filtered_data['content']):
                        res = model_function(text)
                        results.append(res)
                        update_progress(progress_bar, status_text, i+1, total_records, f"Processing {model_name}")
                    progress_bar.progress(1.0)
                    return results

                if can_filter_existing:
                    final_filtered_data = analysis_data[
                        (analysis_data['at'] >= selected_date_range[0]) &
                        (analysis_data['at'] <= selected_date_range[1]) &
                        (analysis_data['score'].isin(selected_scores))
                    ]
                else:
                    final_filtered_data = app_data[
                        (app_data['at'] >= selected_date_range[0]) &
                        (app_data['at'] <= selected_date_range[1]) &
                        (app_data['score'].isin(selected_scores))
                    ]

                if perform_analysis:
                    if not final_filtered_data.empty:
                        model_functions = {
                            "TextBlob": analyze_sentiment_textblob,
                            "VADER": analyze_sentiment_vader,
                            "RoBERTa": analyze_sentiment_roberta,
                            "DistilBERT": analyze_sentiment_distilbert,
                        }

                        if selected_model in model_functions:
                            model_function = model_functions[selected_model]

                            # Run sentiment analysis
                            sentiments = run_sentiment_analysis(model_function, selected_model)
                            sentiment_df = pd.DataFrame(sentiments)

                            # Before concatenation, remove duplicate columns
                            for col in sentiment_df.columns:
                                if col in final_filtered_data.columns:
                                    final_filtered_data.drop(columns=col, inplace=True)

                            final_filtered_data = final_filtered_data.reset_index(drop=True)
                            final_filtered_data = pd.concat([final_filtered_data, sentiment_df], axis=1)

                            # Store analysis results
                            st.session_state['analysis_data'] = final_filtered_data
                            st.session_state['selected_model'] = selected_model
                            st.session_state['selected_app_name'] = selected_app
                            st.session_state['selected_app_icon'] = selected_app_icon
                            st.session_state['analyzed_date_range'] = selected_date_range
                        else:
                            st.error("Selected model is not supported.")
                    else:
                        st.write("No data available for the selected filters.")

                if 'analysis_data' in st.session_state and st.session_state['analysis_data'] is not None:
                    analyzed_data = st.session_state['analysis_data']
                    selected_model = st.session_state['selected_model']
                    selected_app = st.session_state['selected_app_name']
                    selected_app_icon = st.session_state['selected_app_icon']
                    analyzed_date_range = st.session_state['analyzed_date_range']

                    if selected_date_range[0] >= analyzed_date_range[0] and selected_date_range[1] <= analyzed_date_range[1]:
                        displayed_data = analyzed_data[
                            (analyzed_data['at'] >= selected_date_range[0]) &
                            (analyzed_data['at'] <= selected_date_range[1]) &
                            (analyzed_data['score'].isin(selected_scores))
                        ]
                    else:
                        st.warning("You've selected a broader date range than previously analyzed. Please re-run the analysis.")
                        displayed_data = None

                    if displayed_data is not None and not displayed_data.empty:
                        st.write("Analysis Completed!")
                        date_range_str = f"{selected_date_range[0]} to {selected_date_range[1]}"
                        cols = st.columns([0.8, 0.2])
                        with cols[0]:
                            st.title(selected_app)
                            # Display date range and model name
                            st.markdown(
                                f"<p style='font-size:20px; font-weight:bold;'>Date Range: {date_range_str}<br>Model: {selected_model}</p>",
                                unsafe_allow_html=True
                            )
                        with cols[1]:
                            if selected_app_icon:
                                st.image(selected_app_icon, use_container_width=True)

                        model_prefix = selected_model.lower()
                        numeric_cols = displayed_data.select_dtypes(include=['float', 'int']).columns.tolist()
                        model_numeric_cols = [col for col in numeric_cols if col.startswith(model_prefix)]

                        label_col = [c for c in displayed_data.columns if c.endswith('_sentiment_label')]
                        label_col = label_col[0] if label_col else None

                        cols_to_show = ['content', 'score', 'at'] + model_numeric_cols
                        if label_col:
                            cols_to_show.append(label_col)
                        cols_to_show = [c for c in cols_to_show if c in displayed_data.columns]

                        st.write("### Sentiment Analysis Results")
                        st.dataframe(displayed_data[cols_to_show])

                        if label_col:
                            if selected_model == "TextBlob":
                                order = ['Negative', 'Neutral', 'Positive']
                            elif selected_model == "VADER":
                                order = ['Negative', 'Neutral', 'Positive']
                            elif selected_model == "RoBERTa":
                                order = ['Negative', 'Neutral', 'Positive']
                            elif selected_model == "DistilBERT":
                                displayed_data[label_col] = displayed_data[label_col].str.capitalize()
                                order = ['Negative', 'Positive']

                            sentiment_counts = displayed_data[label_col].value_counts().reindex(order).fillna(0)
                            sentiment_counts_df = sentiment_counts.reset_index()
                            sentiment_counts_df.columns = ['Sentiment', 'Count']

                            st.write("### Sentiment Distribution")
                            fig = px.bar(sentiment_counts_df, x='Sentiment', y='Count')
                            st.plotly_chart(fig)

                        st.write("### Average Sentiment Metrics Over Time")
                        selected_metrics = st.multiselect("Select metrics to plot over time:", model_numeric_cols, default=model_numeric_cols)
                        if selected_metrics:
                            metrics_over_time = (
                                displayed_data
                                .groupby('at', as_index=False)[selected_metrics]
                                .mean(numeric_only=True)
                            )
                            fig_line = px.line(metrics_over_time, x='at', y=selected_metrics)
                            st.plotly_chart(fig_line)
                        else:
                            st.write("No numeric metrics selected to plot.")
                    elif displayed_data is not None and displayed_data.empty:
                        st.write("No data available after applying these filters.")
            else:
                st.write("No reviews available for the selected app.")
        else:
            st.write("Please select an application to perform sentiment analysis.")

    with tabs[2]:
        if 'analysis_data' in st.session_state and st.session_state['analysis_data'] is not None:
            score_fig = plot_score_distribution(st.session_state['analysis_data'])
            st.plotly_chart(score_fig)
        else:
            st.write("No data available. Perform analysis first.")

    with tabs[3]:
        st.header("Problems Identification")
        # Generate and display word cloud
        if 'filtered_data' in locals() and not filtered_data.empty:
            combined_text = ' '.join(filtered_data['content'].dropna().tolist()).lower()
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(combined_text)

            # Display the word cloud using matplotlib
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

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

                fig = px.bar(issue_df, x='Issue', y='Count', title='Common Problems in App Reviews')
                st.plotly_chart(fig)
            else:
                st.write("No common problems identified based on the selected filters.")

            st.header("Most Frequent Words and Phrases")
            ngram_length = st.selectbox("Select phrase length:", [1, 2, 3, 4], index=0)

            combined_text = ' '.join(filtered_data['content'].dropna().tolist()).lower()
            ngrams = generate_ngrams(combined_text, ngram_length)
            ngram_counts = Counter(ngrams)
            ngram_df = pd.DataFrame(ngram_counts.items(), columns=['Phrase', 'Count']).sort_values(by='Count', ascending=False)

            if not ngram_df.empty:
                st.write(f"### Most Common {ngram_length}-Word Phrases")
                st.dataframe(ngram_df.head(10).reset_index(drop=True), use_container_width=True)

                fig = px.bar(ngram_df.head(10), x='Phrase', y='Count', title=f'Top 10 Most Common {ngram_length}-Word Phrases')
                st.plotly_chart(fig)

                selected_phrase = st.selectbox("Select a phrase to view related comments:", ngram_df['Phrase'].head(10).tolist())

                if selected_phrase:
                    st.write(f"Comments containing the phrase: **{selected_phrase}**")
                    related_comments = filtered_data[
                        filtered_data['content'].str.contains(selected_phrase, case=False, na=False)
                    ]
                    st.dataframe(related_comments[['content']].reset_index(drop=True), use_container_width=True)
            else:
                st.write(f"No {ngram_length}-word phrases found.")
        else:
            st.write("No data available. Perform analysis first.")

    conn.close()