import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta
from collections import Counter
from transformers import pipeline
import tensorflow as tf
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from tqdm import tqdm
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from src.functions.app_analysis_functions import (
    get_db_connection,
    create_tables,
    search_and_select_app,
    check_and_fetch_reviews,
    display_reviews,
    preprocess_data,
    plot_score_distribution,
    generate_ngrams,
    preprocess_text_simple,
    plot_daily_average_rating
)
from src.database_connection.db_utils import get_app_data

from src.models.textblob_model import analyze_sentiment_textblob
from src.models.vader_model import analyze_sentiment_vader
from src.models.roberta_model import analyze_sentiment_roberta
from src.models.distilbert_model import analyze_sentiment_distilbert
from matplotlib.colors import LinearSegmentedColormap


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
                
                # Safely access dictionary keys with defaults
                selected_app = chosen_app.get('title', 'Unknown App')
                selected_app_id = chosen_app.get('appId', None)
                selected_app_icon = chosen_app.get('icon', None)
                st.session_state['selected_app_icon'] = chosen_app.get('icon', None)
                
                
                if not selected_app_id:
                    st.sidebar.error("Selected app does not have a valid App ID.")
                    selected_app = None
                    selected_app_id = None
        else:
            st.sidebar.write(f"No apps found matching '{search_query}'. Please try a different name.")
    else:
        st.sidebar.write("Please enter an application name to search.")

    # Reset session state if the app changes
    if selected_app_id:
        if 'last_selected_app' not in st.session_state:
            st.session_state['last_selected_app'] = selected_app_id

        if st.session_state['last_selected_app'] != selected_app_id:
            # Reset session state for analysis when a new app is selected
            st.session_state['analysis_data'] = None
            st.session_state['selected_model'] = None
            st.session_state['analyzed_date_range'] = None
            st.session_state['last_selected_app'] = selected_app_id
    
        # Initialize session variables for date range
        if 'selected_date_range' not in st.session_state:
            st.session_state['selected_date_range'] = (datetime.now() - timedelta(days=30), datetime.now())

        # Reset selected_date_range if a new app is selected
        if st.session_state['last_selected_app'] != selected_app_id:
            st.session_state['selected_date_range'] = (datetime.now() - timedelta(days=30), datetime.now())

        # Initialize session variables for selected scores
        if 'selected_scores' not in st.session_state:
            st.session_state['selected_scores'] = [1, 2, 3, 4, 5]  

        # Reset selected_scores if a new app is selected
        if st.session_state['last_selected_app'] != selected_app_id:
            st.session_state['selected_scores'] = [1, 2, 3, 4, 5]  

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

        st.session_state['selected_date_range'] = (start_date_input, end_date_input)
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
        if 'app_data' not in st.session_state:
            st.session_state.app_data = None  

        if selected_app and selected_app_id:
            
            if perform_analysis_button:
                st.session_state.stop_download = False

                status_placeholder = st.empty()
                missing_placeholder = st.empty()

                check_and_fetch_reviews(
                    conn,
                    selected_app,
                    selected_app_id,
                    start_date,
                    end_date,
                    status_placeholder,
                    missing_placeholder
                )

                # Update raw data in session state
                app_data = get_app_data(conn, selected_app)
                if not app_data.empty:
                    app_data = preprocess_data(app_data)
                    app_data['at'] = pd.to_datetime(app_data['at']).dt.date
                    st.session_state.app_data = app_data  
                    st.write(f"### Fetched Data for **{selected_app}**:")
                    st.dataframe(app_data)
                else:
                    st.session_state.app_data = None
                    st.warning(f"No data available for {selected_app}. Please try another app.")

            elif stop_download_button:
                st.session_state.stop_download = True
                st.info("Stopping download and performing analysis with existing data...")

                # Update raw data in session state
                app_data = get_app_data(conn, selected_app)
                if not app_data.empty:
                    app_data = preprocess_data(app_data)
                    app_data['at'] = pd.to_datetime(app_data['at']).dt.date
                    st.session_state.app_data = app_data 
                    st.session_state['selected_app_icon'] = chosen_app.get('icon', None)
                    st.write(f"### Fetched Data for **{selected_app}**:")
                    st.dataframe(app_data)
                else:
                    st.session_state.app_data = None
                    st.warning(f"No data available for {selected_app}. Please try another app.")

        elif perform_analysis_button or stop_download_button:
            st.warning("Please select an application before proceeding.")

        # Display analysis results
        if st.session_state.analysis_result is not None and not st.session_state.analysis_result.empty:
            st.write(f"### Reviews for **{selected_app}**:")
            st.dataframe(st.session_state.analysis_result)
        else:
            st.write("No analysis performed yet or no reviews found for the selected date range.")


    with tabs[1]:
        if selected_app:
            app_data = get_app_data(conn, selected_app)
            if app_data.empty:
                st.sidebar.write("No date slider means that there is no app data available. Please download it first via the 'Data Downloading' tab.")
            if not app_data.empty:
                app_data = preprocess_data(app_data)
                app_data['at'] = pd.to_datetime(app_data['at']).dt.date

                # Date slider in sidebar
                st.sidebar.write("Filter by Date:")
                st.sidebar.write("Date range is selectable. It indicates that data is available for that period and can be analyzed. You can download additional data using the 'Data Downloading' tab.")
                min_date = app_data['at'].min()
                max_date = app_data['at'].max()

                if min_date < max_date:
                    st.session_state['selected_date_range'] = st.sidebar.slider(
                        "Select Date Range",
                        min_value=min_date,
                        max_value=max_date,
                        value=(min_date, max_date)
                    )
                else:
                    st.sidebar.warning("Not enough data to display the date range slider. This means there is no app data available. Please download it first via the 'Download reviews' button in the 'Data Downloading' tab.")
                    st.session_state['selected_date_range'] = (min_date, max_date)

                analysis_data = st.session_state.get('analysis_data', None)
                analyzed_date_range = st.session_state.get('analyzed_date_range', None)

                can_filter_existing = False
                if analysis_data is not None and analyzed_date_range is not None:
                    if st.session_state['selected_date_range'][0] >= analyzed_date_range[0] and st.session_state['selected_date_range'][1] <= analyzed_date_range[1]:
                        can_filter_existing = True

                # Sidebar Filters for Scores
                if 'selected_scores' not in st.session_state:
                    st.session_state['selected_scores'] = [1, 2, 3, 4, 5] 

                st.sidebar.write("Filter by Scores:")
                score_filters = {
                    1: st.sidebar.checkbox("1 Star", value=1 in st.session_state['selected_scores']),
                    2: st.sidebar.checkbox("2 Stars", value=2 in st.session_state['selected_scores']),
                    3: st.sidebar.checkbox("3 Stars", value=3 in st.session_state['selected_scores']),
                    4: st.sidebar.checkbox("4 Stars", value=4 in st.session_state['selected_scores']),
                    5: st.sidebar.checkbox("5 Stars", value=5 in st.session_state['selected_scores']),
                }

                # Update session state
                st.session_state['selected_scores'] = [score for score, selected in score_filters.items() if selected]

                st.write("### Select Sentiment Analysis Model")
                model_options = ["TextBlob", "VADER", "DistilBERT", "RoBERTa"]
                st.markdown("""
                - **TextBlob**  
                Speed: very fast  
                Simple model based on basic NLP techniques; can analyze text with high throughput.

                - **VADER**  
                Speed: fast  
                Lightweight and efficient model for short texts (e.g., tweets, comments).

                - **DistilBERT**  
                Speed: moderate  
                A “distilled” version of BERT, more advanced than TextBlob or VADER.

                - **RoBERTa**  
                Speed: slowest  
                An improved variant of BERT with very high accuracy, but also more computationally intensive.
                """)
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
                        (analysis_data['at'] >= st.session_state['selected_date_range'][0]) &
                        (analysis_data['at'] <= st.session_state['selected_date_range'][1]) &
                        (analysis_data['score'].isin(st.session_state['selected_scores']))
                    ]
                else:
                    final_filtered_data = app_data[
                        (app_data['at'] >= st.session_state['selected_date_range'][0]) &
                        (app_data['at'] <= st.session_state['selected_date_range'][1]) &
                        (app_data['score'].isin(st.session_state['selected_scores']))
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

                            sentiments = run_sentiment_analysis(model_function, selected_model)
                            sentiment_df = pd.DataFrame(sentiments)

                            # remove duplicate columns
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
                            st.session_state['analyzed_date_range'] = st.session_state['selected_date_range']
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

                    if st.session_state['selected_date_range'][0] >= analyzed_date_range[0] and st.session_state['selected_date_range'][1] <= analyzed_date_range[1]:
                        displayed_data = analyzed_data[
                            (analyzed_data['at'] >= st.session_state['selected_date_range'][0]) &
                            (analyzed_data['at'] <= st.session_state['selected_date_range'][1]) &
                            (analyzed_data['score'].isin(st.session_state['selected_scores']))
                        ]
                    else:
                        st.warning("You've selected a broader date range than previously analyzed. Please re-run the analysis.")
                        displayed_data = None

                    if displayed_data is not None and not displayed_data.empty:
                        st.write("Analysis Completed!")
                        date_range_str = f"{st.session_state['selected_date_range'][0]} to {st.session_state['selected_date_range'][1]}"
                        cols = st.columns([0.9, 0.1])
                        with cols[0]:
                            st.title(selected_app)
                            
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
                            fig = px.bar(sentiment_counts_df, x='Sentiment', y='Count', color_discrete_sequence=['#2196F3'])
                            st.plotly_chart(fig)

                        st.write("### Average Sentiment Metrics Over Time")
                        selected_metrics = st.multiselect(
                            "Select metrics to plot over time (you can choose additional metrics to compare them):",
                            model_numeric_cols,
                            default=model_numeric_cols[:1]
                        )
                        if selected_metrics:
                            
                            metrics_over_time = (
                                displayed_data
                                .groupby('at', as_index=False)[selected_metrics]
                                .mean(numeric_only=True)
                            )

                            metrics_over_time.rename(columns={'at': 'date'}, inplace=True)
                            melted = metrics_over_time.melt(id_vars='date', value_vars=selected_metrics, var_name='metric', value_name='value')

                            # Compute a 7-day moving average trend for each metric
                            melted['trend'] = melted.groupby('metric')['value'].transform(lambda x: x.rolling(7, min_periods=1).mean())
                            fig_line = px.line(melted, x='date', y='value', color='metric', title='Average Sentiment Metrics Over Time')

                            # Add the trend line as a dashed line for each metric
                            for metric in selected_metrics:
                                metric_data = melted[melted['metric'] == metric]
                                fig_line.add_trace(
                                    go.Scatter(
                                        x=metric_data['date'],
                                        y=metric_data['trend'],
                                        mode='lines',
                                        name=f'{metric} (Trend)',
                                        line=dict(dash='dash', color='#FF66C4')
                                    )
                                )

                            st.plotly_chart(fig_line)
                        else:
                            st.write("No numeric metrics selected to plot.")
                        
                        # Determine best/worst comments
                        if selected_model == "TextBlob":
                            if 'textblob_polarity' in displayed_data.columns:
                                best_10 = displayed_data.sort_values(by='textblob_polarity', ascending=False).head(10)
                                worst_10 = displayed_data.sort_values(by='textblob_polarity', ascending=True).head(10)
                            else:
                                best_10 = None
                                worst_10 = None
                        else:
                            if selected_model == "VADER":
                                col_positive = 'vader_positive'
                                col_negative = 'vader_negative'
                            elif selected_model == "DistilBERT":
                                col_positive = 'distilbert_positive'
                                col_negative = 'distilbert_negative'
                            elif selected_model == "RoBERTa":
                                col_positive = 'roberta_positive'
                                col_negative = 'roberta_negative'
                            else:
                                col_positive = None
                                col_negative = None

                            if col_positive and col_negative and col_positive in displayed_data.columns and col_negative in displayed_data.columns:
                                
                                best_10 = displayed_data.sort_values(by=[col_positive, col_negative], ascending=[False, True]).head(10)
                                
                                worst_10 = displayed_data.sort_values(by=[col_negative, col_positive], ascending=[False, True]).head(10)
                            else:
                                best_10 = None
                                worst_10 = None

                        st.write("### Top 10 Best Comments")
                        if best_10 is not None and not best_10.empty:
                            # Show all metrics
                            metrics_cols = [c for c in best_10.columns if c.startswith(selected_model.lower())]
                            st.dataframe(best_10[['content'] + metrics_cols])
                        else:
                            st.write("No data available for best comments.")

                        st.write("### Top 10 Worst Comments")
                        if worst_10 is not None and not worst_10.empty:
                            metrics_cols = [c for c in worst_10.columns if c.startswith(selected_model.lower())]
                            st.dataframe(worst_10[['content'] + metrics_cols])
                        else:
                            st.write("No data available for worst comments.")
                    elif displayed_data is not None and displayed_data.empty:
                        st.write("No data available after applying these filters.")
            else:
                st.write("No reviews available for the selected app.")
        else:
            st.write("Please select an application to perform sentiment analysis.")

    with tabs[2]:
        # Display the logo and app name
        cols = st.columns([0.9, 0.1])
        date_range_str = f"{st.session_state['selected_date_range'][0]} to {st.session_state['selected_date_range'][1]}"
        with cols[0]:
            st.title(selected_app)
            st.markdown(
                f"<p style='font-size:20px; font-weight:bold;'>Date Range: {date_range_str}</p>",
                unsafe_allow_html=True
            )
        with cols[1]:
            if 'selected_app_icon' in st.session_state and st.session_state['selected_app_icon']:
                st.image(st.session_state['selected_app_icon'], use_container_width=True)

        st.header("Score Analysis")

        # Fetch data from the database
        if selected_app:
            app_data = get_app_data(conn, selected_app)
            if not app_data.empty:
                app_data = preprocess_data(app_data)
                app_data['at'] = pd.to_datetime(app_data['at']).dt.date
                st.session_state['app_data'] = app_data
            else:
                st.write("No data available. Please select an application and download reviews.")
                st.session_state['app_data'] = None

        if 'app_data' in st.session_state and st.session_state['app_data'] is not None:
            app_data = st.session_state['app_data']

            # Apply filters based on date range and scores
            displayed_data = app_data[
                (app_data['at'] >= st.session_state['selected_date_range'][0]) &
                (app_data['at'] <= st.session_state['selected_date_range'][1]) &
                (app_data['score'].isin(st.session_state['selected_scores']))
            ]

            if not displayed_data.empty:
                # Score Distribution Plot
                st.write("### Score Distribution")
                score_fig = plot_score_distribution(displayed_data)
                st.plotly_chart(score_fig)
                st.write("### Daily Average Rating Over Time")

                # Group by date
                metrics_over_time = (
                    displayed_data
                    .groupby('at', as_index=False)['score']
                    .mean(numeric_only=True)
                )

                melted = metrics_over_time.melt(id_vars='at', value_vars=['score'], var_name='metric', value_name='value')

                # Compute a 7-day moving average trend for the score
                melted['trend'] = melted.groupby('metric')['value'].transform(lambda x: x.rolling(7, min_periods=1).mean())

                fig_line = px.line(
                    melted,
                    x='at',
                    y='value',
                    color='metric',
                    title="Daily Average Rating Over Time",
                    labels={'at': 'Date', 'value': 'Average Score'}
                )

                # Add the trend line as a dashed line
                for metric in ['score']:
                    metric_data = melted[melted['metric'] == metric]
                    fig_line.add_trace(
                        go.Scatter(
                            x=metric_data['at'],
                            y=metric_data['trend'],
                            mode='lines',
                            name='Trend score*',
                            line=dict(dash='dash', color='#FF66C4')
                        )
                    )

                st.plotly_chart(fig_line)

                st.write("""
                **Description**:  
                This plot shows the daily average rating of the app over time. Each point represents the average score on a given day, aggregated from user reviews.  

                *The **trend line** represents a 7-day moving average of the daily scores, smoothing out short-term fluctuations to highlight the general trend over time.
                """)

                if not metrics_over_time.empty:
                    # Calculate daily changes
                    metrics_over_time['Change'] = metrics_over_time['score'].diff()

                    # Find the biggest drop and growth
                    max_growth = metrics_over_time.loc[metrics_over_time['Change'].idxmax()] if metrics_over_time['Change'].max() > 0 else None
                    max_drop = metrics_over_time.loc[metrics_over_time['Change'].idxmin()] if metrics_over_time['Change'].min() < 0 else None

                    # Display table with results
                    st.write("### Biggest Daily Changes")
                    if max_growth is not None or max_drop is not None:
                        changes_table = pd.DataFrame(
                            {
                                "Type": ["Growth", "Drop"],
                                "Date": [
                                    max_growth['at'] if max_growth is not None else None,
                                    max_drop['at'] if max_drop is not None else None
                                ],
                                "Change in Average Score": [
                                    f"{max_growth['Change']:.2f}" if max_growth is not None else None,
                                    f"{max_drop['Change']:.2f}" if max_drop is not None else None,
                                ],
                            }
                        )
                        st.dataframe(changes_table, use_container_width=True)
                    else:
                        st.write("No significant changes detected in daily average ratings.")
                else:
                    st.write("No data available for plotting.")
            else:
                st.write("No data available after applying these filters.")
        else:
            st.write("No data available. Please download reviews first.")

    with tabs[3]:
        # Display the logo
        cols = st.columns([0.9, 0.1])
        date_range_str = f"{st.session_state['selected_date_range'][0]} to {st.session_state['selected_date_range'][1]}"
        with cols[0]:
            st.title(selected_app)
            st.markdown(
                f"<p style='font-size:20px; font-weight:bold;'>Date Range: {date_range_str}</p>",
                unsafe_allow_html=True
            )
        with cols[1]:
            if 'selected_app_icon' in st.session_state and st.session_state['selected_app_icon']:
                st.image(st.session_state['selected_app_icon'], use_container_width=True)

        st.header("Problems Identification")

        # Fetch data from the database
        if selected_app:
            app_data = get_app_data(conn, selected_app)
            if not app_data.empty:
                app_data = preprocess_data(app_data)
                app_data['at'] = pd.to_datetime(app_data['at']).dt.date
                st.session_state['app_data'] = app_data
            else:
                st.write("No data available. Please select an application and download reviews.")
                st.session_state['app_data'] = None

        if 'app_data' in st.session_state and st.session_state['app_data'] is not None:
            app_data = st.session_state['app_data']

            # Apply filters based on date range and scores
            final_filtered_data = app_data[
                (app_data['at'] >= st.session_state['selected_date_range'][0]) &
                (app_data['at'] <= st.session_state['selected_date_range'][1]) &
                (app_data['score'].isin(st.session_state['selected_scores']))
            ]

            if not final_filtered_data.empty:
                final_filtered_data = final_filtered_data.drop_duplicates(subset=['content'])
                final_filtered_data['cleaned_content'] = final_filtered_data['content'].apply(preprocess_text_simple)

                # User input for problem identification
                problem_keyword = st.text_input("Enter a keyword to identify problems (e.g., 'bug')")

                if problem_keyword:
                    # Filter comments containing the exact keyword from the cleaned content
                    keyword_comments = final_filtered_data[
                        final_filtered_data['cleaned_content'].str.contains(rf'\b{problem_keyword}\b', case=False, na=False)
                    ]

                    # Calculate the percentage of comments containing the keyword
                    keyword_count = len(keyword_comments)
                    total_comments = len(final_filtered_data)
                    keyword_percentage = (keyword_count / total_comments) * 100 if total_comments > 0 else 0

                    # Display results
                    st.write(f"### Analysis for keyword: **{problem_keyword}**")
                    st.write(f"Total comments: {total_comments}")
                    st.write(f"Comments containing '{problem_keyword}': {keyword_count} ({keyword_percentage:.2f}%)")

                    if keyword_count > 0:
                        st.write(f"### Comments containing the keyword '{problem_keyword}':")
                        st.dataframe(keyword_comments[['content']].reset_index(drop=True), use_container_width=True)

                # Generate n-grams for each row and store them
                st.header("Most Frequent Words and Phrases")
                ngram_length = st.selectbox("Select phrase length:", [1, 2, 3, 4], index=0)

                all_ngrams = []
                ngram_to_row_mapping = [] 

                for index, text in final_filtered_data['cleaned_content'].dropna().items():
                    ngrams = generate_ngrams(text, ngram_length)
                    all_ngrams.extend(ngrams)
                    ngram_to_row_mapping.extend([(index, ngram) for ngram in ngrams])

                # Count n-gram frequencies
                ngram_counts = Counter(all_ngrams)
                ngram_df = pd.DataFrame(ngram_counts.items(), columns=['Phrase', 'Count']).sort_values(by='Count', ascending=False)

                if not ngram_df.empty:
                    # Display the top 10 most common phrases
                    st.write(f"### Top 10 Most Common {ngram_length}-Word Phrases")
                    st.dataframe(ngram_df.head(10).reset_index(drop=True), use_container_width=True)

                    # Plot the bar chart for the top 10 phrases
                    fig = px.bar(
                        ngram_df.head(10),
                        x='Phrase',
                        y='Count',
                        title=f"Top 10 Most Common {ngram_length}-Word Phrases",
                        color_discrete_sequence=['#2196F3']
                    )
                    st.plotly_chart(fig)

                    # Select a phrase to view related comments
                    selected_phrase = st.selectbox(
                        "Select a phrase to view related comments:",
                        ngram_df['Phrase'].head(10).tolist()
                    )

                    if selected_phrase:
                        st.write(f"### Comments containing the phrase: **{selected_phrase}**")

                        # Find the rows containing the selected phrase
                        matching_rows = list(set(
                            row_index for row_index, ngram in ngram_to_row_mapping if ngram == selected_phrase
                        ))
                        related_comments = final_filtered_data.loc[matching_rows, ['content', 'score', 'at', 'user_name']]

                        if not related_comments.empty:
                            st.dataframe(related_comments.reset_index(drop=True), use_container_width=True)
                        else:
                            st.write(f"No comments contain the phrase: **{selected_phrase}**")

                # Word Cloud
                colors = ["#FF66C4", "#FF66C4", "#cbd5e8", "#2196F3", "#2E2E2E"]
                custom_cmap = LinearSegmentedColormap.from_list("custom_palette", colors)

                st.header("Word Cloud")
                all_cleaned_text = ' '.join(final_filtered_data['cleaned_content'])
                wordcloud = WordCloud(width=800, height=400, background_color='white', colormap=custom_cmap).generate(all_cleaned_text)

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)

            else:
                st.write("No data available after applying these filters.")
        else:
            st.write("No data available. Please download reviews first.")


    conn.close()