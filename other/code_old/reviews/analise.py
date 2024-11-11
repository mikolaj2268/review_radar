import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from matplotlib.colors import LinearSegmentedColormap


# Wczytaj dane
data = pd.read_csv('assets/data/combined_app_reviews.csv')

pd.set_option('display.max_columns', None)

all_reviews = ' '.join(data['content'].dropna())

# Define a custom colormap with vibrant colors
colors = ["#FF66C4", "#FF66C4", "#4CAF50", "#2196F3", "#2E2E2E"]
custom_cmap = LinearSegmentedColormap.from_list("custom_palette", colors)

# Generate the word cloud with the custom colormap
wordcloud = WordCloud(
    width=800,
    height=400,
    background_color="white",
    colormap=custom_cmap,  
    contour_color="black"
).generate(all_reviews)

# Display the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Colorful Word Cloud", fontsize=16)
plt.show()

print("Rodzaj danych i liczba unikalnych wartości w każdej kolumnie:")
data = data.infer_objects()
print(data.dtypes)

print("\nLiczba unikalnych wartości w każdej kolumnie:")
print(data.nunique())


# Analiza brakujących wartości
print("\nProcent brakujących wartości w każdej kolumnie:")
print(data.isnull().mean() * 100)

# Liczba unikalnych wartości dla 'reviewId' i 'userName'
print("\nLiczba unikalnych wartości dla 'reviewId':", data['reviewId'].nunique())
print("Liczba unikalnych wartości dla 'userName':", data['userName'].nunique())

# Analiza częstości występowania tekstów w 'content'
print("\nNajczęściej występujące treści w 'content':")
print(data['content'].value_counts().head(10) / len(data) * 100)
data['content_length'] = data['content'].astype(str).apply(len)
print("\nStatystyki długości treści recenzji w 'content':")
print(data['content_length'].describe())
sns.histplot(data['content_length'], bins=30, kde=True)
plt.title("Rozkład długości treści recenzji")
plt.xlabel("Długość treści")
plt.ylabel("Liczba")
plt.show()

score_distribution = data['score'].value_counts(normalize=True) * 100
print("\nRozkład ocen w kolumnie 'score':")
print(score_distribution)

score_distribution = pd.Series({
    5: 60.059915,
    1: 21.441825,
    4: 7.758021,
    3: 5.655199,
    2: 5.085041
})

# Utworzenie wykresu słupkowego z procentami nad słupkami
plt.figure(figsize=(8, 6))
bars = plt.bar(score_distribution.index, score_distribution.values, width=0.6)

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

