import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Wczytaj dane
data = pd.read_csv('combined_app_reviews.csv')

pd.set_option('display.max_columns', None)

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

# Rozkład ocen w kolumnie 'score'
print("\nRozkład ocen w kolumnie 'score':")
print(data['score'].value_counts(normalize=True) * 100)
sns.histplot(data['score'], bins=5, kde=False)
plt.title("Rozkład ocen")
plt.xlabel("Ocena")
plt.ylabel("Liczba")
plt.show()


# Sprawdzenie nulli w kolumnach 'reviewCreatedVersion' i 'appVersion'
print("\nLiczba braków w kolumnach 'reviewCreatedVersion' oraz 'appVersion':")
print(data[['reviewCreatedVersion', 'appVersion']].isnull().sum())

# Rozkład wersji aplikacji
print("\nRozkład wersji aplikacji w kolumnie 'reviewCreatedVersion':")
print(data['reviewCreatedVersion'].value_counts(normalize=True).head(10) * 100)
