# Review Radar

![GitHub repo size](https://img.shields.io/github/repo-size/mikolaj2268/review_radar)
![GitHub stars](https://img.shields.io/github/stars/mikolaj2268/review_radar?style=social)
![GitHub forks](https://img.shields.io/github/forks/mikolaj2268/review_radar?style=social)
![GitHub issues](https://img.shields.io/github/issues/mikolaj2268/review_radar)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Sentiment Analysis Models](#sentiment-analysis-models)
- [Comparing Models](#comparing-models)
- [Contributing](#contributing)

## Introduction

**Review Radar** is a comprehensive system designed to collect, analyze, and visualize user reviews from the Google Play Store. By leveraging advanced sentiment analysis models and efficient data management techniques, Review Radar provides insightful visualizations and reports that help developers understand user feedback, identify trends, and improve their applications.
You can try the live application here: ![Review Radar](https://reviewradar.streamlit.app)


## Features

- **Data Collection:** Scrapes reviews from the Google Play Store using Google Play API.
- **Sentiment Analysis:** Utilizes multiple models for robust sentiment classification:
  - **TextBlob:** For basic sentiment polarity and subjectivity.
  - **VADER:** Optimized for social media text with nuanced sentiment scoring.
  - **DistilBERT:** A lightweight transformer model for precise sentiment probabilities.
  - **RoBERTa:** An advanced transformer model for comprehensive sentiment classification.
- **Data Storage:** Efficiently stores and manages review data in a local SQLite database.
- **Data Optimization:**
  - Avoids redundant data downloads by tracking downloaded dates.
  - Prevents multiple sentiment analyses on the same reviews by storing sentiment results.
- **Visualization:** Interactive dashboards and plots using Streamlit and Plotly to display sentiment distributions, trends over time, and other key metrics.
- **Scalability:** Designed to handle large volumes of reviews with optimized database schemas and processing pipelines.

## Technologies

- **Programming Language:** Python
- **Web Framework:** Streamlit
- **Database:** SQLite
- **Sentiment Analysis Libraries:**
  - [TextBlob](https://textblob.readthedocs.io/en/dev/)
  - [VADER](https://github.com/cjhutto/vaderSentiment)
  - [Transformers (DistilBERT & RoBERTa)](https://huggingface.co/transformers/)
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly, Matplotlib
- **Others:** Torch, tqdm

## Installation

### Prerequisites

- Python 3.12 or higher
- Git

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/mikolaj2268/review_radar.git
   cd review_radar
   ```

2. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set Up the Database:**

   Ensure that the SQLite database file `google_play_reviews.db` is present in the repository. If not, it will be created automatically when running the application.

## Usage

### Running the Streamlit Application

1. **Activate the Virtual Environment:**

   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Run the Streamlit App:**

   ```bash
   streamlit run app.py
   ```

   This command will launch the Streamlit application in your default web browser.

### Scraping and Analyzing Reviews

1. **Search and Select an App:**
   - Use the search functionality to find the desired application on the Google Play Store.

2. **Fetch Reviews:**
   - Select the date range for which you want to fetch reviews.
   - The system will check for already downloaded dates to avoid redundant scraping.
   - Missing reviews will be fetched and stored in the database.

3. **View Sentiment Analysis:**
   - Navigate to the visualization section to see sentiment distributions, trends over time, and other insightful metrics based on the analyzed reviews.

## Sentiment Analysis Models

Review Radar employs multiple sentiment analysis models to ensure comprehensive and accurate sentiment classification of user reviews.

### TextBlob

TextBlob is a Python library for processing textual data. It provides a simple API for diving into common natural language processing (NLP) tasks such as part-of-speech tagging, noun phrase extraction, sentiment analysis, classification, translation, and more.

- **Polarity:** Measures sentiment polarity in the range [-1.0, 1.0], where -1.0 is very negative and 1.0 is very positive.
- **Subjectivity:** Measures sentiment subjectivity in the range [0.0, 1.0], where 0.0 is very objective and 1.0 is very subjective.

### VADER (Valence Aware Dictionary and sEntiment Reasoner)

VADER is a rule-based sentiment analysis tool specifically attuned to sentiments expressed in social media. It is capable of detecting sentiment intensity and is optimized for short texts.

- **neg:** Probability of negative sentiment.
- **neu:** Probability of neutral sentiment.
- **pos:** Probability of positive sentiment.
- **compound:** Aggregated sentiment score ranging from -1 (most negative) to +1 (most positive).

### DistilBERT

DistilBERT is a distilled version of BERT, designed to be lighter and faster while retaining most of BERT's language understanding capabilities. It is used for more nuanced sentiment analysis by providing probabilities for negative and positive sentiments.

- **Negative Probability:** Likelihood of the text being negative.
- **Positive Probability:** Likelihood of the text being positive.

### RoBERTa (Robustly Optimized BERT Approach)

RoBERTa is an optimized method for pretraining self-supervised NLP systems based on BERT. It achieves state-of-the-art performance on various NLP tasks, including sentiment analysis, by providing probabilities for negative, neutral, and positive sentiments.

- **Negative Probability:** Likelihood of the text being negative.
- **Neutral Probability:** Likelihood of the text being neutral.
- **Positive Probability:** Likelihood of the text being positive.

### Comparing Models

To determine which sentiment analysis model best aligns with the actual user ratings (`score`), we calculate the correlation between the sentiment scores generated by each model and the `score` variable. Higher correlation values indicate a stronger relationship between the sentiment analysis results and the user ratings, suggesting that the model more accurately reflects user sentiment.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. **Fork the Project**
2. **Create your Feature Branch:**

   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. **Commit your Changes:**

   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

4. **Push to the Branch:**

   ```bash
   git push origin feature/AmazingFeature
   ```

5. **Open a Pull Request**


Project Link: [https://github.com/mikolaj2268/review_radar](https://github.com/mikolaj2268/review_radar)
