import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from matplotlib.colors import LinearSegmentedColormap


# Wczytaj dane
#data = pd.read_csv('assets/data/netflix_reviews.csv')

data = pd.read_parquet('models_comparison/reviews.parquet')

pd.set_option('display.max_columns', None)

all_reviews = ' '.join(data['content'].dropna())


# # Define a custom colormap with vibrant colors
# colors = ["#FF66C4", "#FF66C4", "#4CAF50", "#2196F3", "#2E2E2E"]
# custom_cmap = LinearSegmentedColormap.from_list("custom_palette", colors)

# # Generate the word cloud with the custom colormap
# wordcloud = WordCloud(
#     width=800,
#     height=400,
#     background_color="white",
#     colormap=custom_cmap,  
#     contour_color="black"
# ).generate(all_reviews)

# # Display the word cloud
# plt.figure(figsize=(10, 5))
# plt.imshow(wordcloud, interpolation="bilinear")
# plt.axis("off")
# plt.title("Colorful Word Cloud", fontsize=16)
# plt.show()

print("Rodzaj danych i liczba unikalnych wartości w każdej kolumnie:")
data = data.infer_objects()
print(data.dtypes)

print("\nLiczba unikalnych wartości w każdej kolumnie:")
print(data.nunique())
# what kind of unique values does app_name have?
print("\nUnikalne wartości w kolumnie 'app_name':")
print(data['app_name'].unique())

# how many records are there?
print("\nLiczba rekordów w zbiorze danych:", len(data))

#what is the date range for this data?
print("\nZakres dat w zbiorze danych:")
print(data['at'].min(), data['at'].max())

# Analiza brakujących wartości
print("\nProcent brakujących wartości w każdej kolumnie:")
print(data.isnull().mean() * 100)

# Liczba unikalnych wartości dla 'reviewId' i 'userName'
print("\nLiczba unikalnych wartości dla 'reviewId':", data['review_id'].nunique())
# print("Liczba unikalnych wartości dla 'userName':", data['user_name'].nunique())

# Analiza częstości występowania tekstów w 'content'
print("\nNajczęściej występujące treści w 'content':")
print(data['content'].value_counts().head(10) / len(data) * 100)
data['content_length'] = data['content'].astype(str).apply(len)
print("\nStatystyki długości treści recenzji w 'content':")
print(data['content_length'].describe())

# Histogram z rozkładem długości treści recenzji
sns.histplot(data['content_length'], bins=30, kde=True, color="#2196F3")
plt.title("Rozkład długości treści recenzji")
plt.xlabel("Długość treści")
plt.ylabel("Liczba")

# Wyświetlenie wykresu
plt.show()

# Rozkład ocen w kolumnie 'score'
score_distribution = data['score'].value_counts(normalize=True) * 100
print("\nRozkład ocen w kolumnie 'score':")
print(score_distribution)


# Custom colors
bar_color = "#2196F3"
trendline_color = "#FF66C4"

score_distribution = pd.Series({
    5: 52.360853,
    1: 30.361907,
    4: 7.042628,
    3: 5.199889,
    2: 5.034722
})

# Utworzenie wykresu słupkowego z procentami nad słupkami
plt.figure(figsize=(8, 6))
bars = plt.bar(score_distribution.index, score_distribution.values, width=0.6, color="#2196F3")

# Dodanie wartości procentowych nad słupkami
for bar in bars:
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{bar.get_height():.1f}%",
             ha='center', va='bottom', fontsize=10)

# Dodanie tytułów i etykiet
plt.title("Rozkład ocen")
plt.xlabel("Ocena")
plt.ylabel("Procent")
plt.xticks(list(score_distribution.index))  # Ustawienie etykiet na osiach x
plt.show()

# Sprawdzenie nulli w kolumnach 'reviewCreatedVersion' i 'appVersion'
print("\nLiczba braków w kolumnach 'reviewCreatedVersion' oraz 'appVersion':")
print(data[['reviewCreatedVersion', 'appVersion']].isnull().sum())

# Rozkład wersji aplikacji
print("\nRozkład wersji aplikacji w kolumnie 'reviewCreatedVersion':")
print(data['reviewCreatedVersion'].value_counts(normalize=True).head(10) * 100)

# Sprawdź czy reviewCreatedVersion is appVersion sa takie same
print("\nCzy 'reviewCreatedVersion' jest taka sama jak 'appVersion'?")
print((data['reviewCreatedVersion'] == data['appVersion']).mean())

# oblicz mi mediane po score
print("\nMediana długości treści recenzji dla każdej oceny:")

# preprocessing
def preprocess_data(df, model = None):
    """
    Preprocess the given DataFrame.
    Parameters:
    df (pd.DataFrame): The input DataFrame to preprocess.
    Returns:
    pd.DataFrame: The preprocessed DataFrame.
    """
    # Drop duplicates
    df = df.drop_duplicates()

    # Remove rows with invalid scores
    df = df[(df['score'] >= 1) & (df['score'] <= 5)]
    
    # set the content length maximum to 500
    df = df[df['content'].apply(len) <= 500]

    if (model == 'VADER'):
        # Remove special characters from the content
        reviews['clean_content'] = reviews['content'].str.replace('[^\w\s]', '')

    # Handle missing values
    df['content'] = df['content'].fillna('')
    df['review_created_version'] = df['review_created_version'].fillna('Unknown')
    df['app_version'] = df['app_version'].fillna('Unknown')
    df['reply_content'] = df['reply_content'].fillna('')
    df['replied_at'] = df['replied_at'].fillna(pd.NaT)

    # Convert 'at' to datetime and create 'date' column
    df['at'] = pd.to_datetime(df['at'], errors='coerce')
    df = df.dropna(subset=['at'])  # Remove rows with invalid dates
    df['date'] = df['at'].dt.date

    # Convert other date columns to datetime
    date_columns = ['replied_at']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Normalize text in 'content' column
    df['content'] = df['content'].str.lower().str.replace(r'[^\w\s]', '', regex=True)

    # Add new feature: length of the review content
    df['content_length'] = df['content'].apply(len)

    # Handle missing app_version intelligently
    df = df.sort_values(by='at')
    df['app_version'] = df['app_version'].replace('Unknown', pd.NA)
    df['app_version'] = df['app_version'].ffill()

    # Drop unnecessary columns
    columns_to_drop = ['user_image', 'reply_content', 'replied_at']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    # Handle outliers in thumbs_up_count
    if 'thumbs_up_count' in df.columns:
        df['thumbs_up_count'] = df['thumbs_up_count'].clip(lower=0)

    return df