import streamlit as st
import sys
from src.pages import home_page

# Słownik mapujący nazwy stron na funkcje
PAGES = {
    "Home": home_page.home_page,
}

def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))  # Wybór strony
    page = PAGES[selection]  # Pobierz funkcję odpowiedzialną za daną stronę
    page()  # Wywołaj funkcję wybranej strony

if __name__ == "__main__":
    sys.path.append("src")  # Dodaj src do ścieżki, aby łatwo importować moduły
    main()