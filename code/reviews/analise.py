import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Wczytaj dane
data = pd.read_csv('combined_app_reviews.csv')

# Ustawienia wyświetlania dla lepszej czytelności
pd.set_option('display.max_columns', None)

# Wyświetlenie rodzaju danych oraz liczby unikalnych wartości w każdej kolumnie
print("Rodzaj danych i liczba unikalnych wartości w każdej kolumnie:")
data = data.infer_objects()
print(data.dtypes)

print("\nLiczba unikalnych wartości w każdej kolumnie:")
print(data.nunique())


# Analiza brakujących wartości (procent nulli w każdej kolumnie)
print("\nProcent brakujących wartości w każdej kolumnie:")
print(data.isnull().mean() * 100)

# Liczba unikalnych wartości dla 'reviewId' i 'userName'
print("\nLiczba unikalnych wartości dla 'reviewId':", data['reviewId'].nunique())
print("Liczba unikalnych wartości dla 'userName':", data['userName'].nunique())

# Analiza częstości występowania tekstów w 'content' (recenzja), wyświetlenie tylko najpopularniejszych fraz
print("\nNajczęściej występujące treści w 'content':")
print(data['content'].value_counts().head(10) / len(data) * 100)

# Analiza długości tekstów w 'content'
data['content_length'] = data['content'].astype(str).apply(len)
print("\nStatystyki długości treści recenzji w 'content':")
print(data['content_length'].describe())
sns.histplot(data['content_length'], bins=30, kde=True)
plt.title("Rozkład długości treści recenzji")
plt.xlabel("Długość treści")
plt.ylabel("Liczba")
plt.show()

# Rozkład ocen w kolumnie 'score'
print("\nRozkład ocen w kolumnie 'score':")
print(data['score'].value_counts(normalize=True) * 100)
sns.histplot(data['score'], bins=5, kde=False)
plt.title("Rozkład ocen")
plt.xlabel("Ocena")
plt.ylabel("Liczba")
plt.show()

# Analiza kolumny 'thumbsUpCount' (polubienia)
print("\nStatystyki dla 'thumbsUpCount' (polubienia):")
print(data['thumbsUpCount'].describe())
sns.histplot(data['thumbsUpCount'], bins=20, kde=False)
plt.title("Rozkład liczby polubień")
plt.xlabel("Liczba polubień")
plt.ylabel("Liczba")
plt.show()

# Sprawdzenie nulli w kolumnach 'reviewCreatedVersion' i 'appVersion'
print("\nLiczba braków w kolumnach 'reviewCreatedVersion' oraz 'appVersion':")
print(data[['reviewCreatedVersion', 'appVersion']].isnull().sum())

# Rozkład wersji aplikacji
print("\nRozkład wersji aplikacji w kolumnie 'reviewCreatedVersion':")
print(data['reviewCreatedVersion'].value_counts(normalize=True).head(10) * 100)

# Wykres liczby recenzji w czasie na podstawie kolumny 'at' (data recenzji)
data['at'] = pd.to_datetime(data['at'])
data.set_index('at', inplace=True)
data['at'].resample('W').size().plot()
plt.title("Liczba recenzji w czasie")
plt.xlabel("Data")
plt.ylabel("Liczba recenzji")
plt.show()
