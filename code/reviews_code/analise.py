import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the scraped data
reviews_df = pd.read_csv('code/reviews/combined_app_reviews.csv')

# Display the first few rows to ensure the data is loaded properly
print("Data loaded successfully. Here's a sample of the reviews:")
print(reviews_df.head())

# Step 1: Summary Statistics
print("\nSummary of review ratings:")
print(reviews_df['score'].describe())  # Assuming 'score' is the column for ratings

# Step 2: Reviews by App
print("\nNumber of reviews per app:")
print(reviews_df['app_name'].value_counts())

# Step 3: Plot Distribution of Ratings
plt.figure(figsize=(10, 6))
sns.countplot(x='score', data=reviews_df, hue='app_name')
plt.title('Distribution of Review Ratings by App')
plt.xlabel('Review Rating')
plt.ylabel('Count')
plt.show()

# Step 4: Analyzing Review Length (if 'content' column exists)
reviews_df['review_length'] = reviews_df['content'].apply(lambda x: len(x.split()))
print("\nAverage review length by app:")
print(reviews_df.groupby('app_name')['review_length'].mean())

# Step 5: Sentiment Analysis (Optional)
# You can use libraries like TextBlob or Vader to analyze sentiment if needed.
