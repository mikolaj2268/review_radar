import streamlit as st
import sys
from src.pages import home_page

# Słownik mapujący nazwy stron na funkcje
PAGES = {
    "Home": home_page.home_page,
    # Add other page functions here when they are implemented
    # "Add Application": add_application_page,
    # "Refresh Database": refresh_database_page,
}

def main():
    st.sidebar.title("Options")
    selection = st.sidebar.selectbox(
        "Select a page", ["Home", "App Analysis"]
    )  # Wybór strony
    if selection in PAGES:
        page = PAGES[selection]  # Pobierz funkcję odpowiedzialną za daną stronę
        page()  # Wywołaj funkcję wybranej strony
    else:
        st.write(f"{selection} page is not implemented yet.")

if __name__ == "__main__":
    sys.path.append("src")  # Dodaj src do ścieżki, aby łatwo importować moduły
    main()