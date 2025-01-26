import streamlit as st
import os

def create_st_button(text, url, st_col=None):
    """
    Creates a clickable button in Streamlit that links to a specified URL.

    Parameters:
        text (str): The text displayed on the button.
        url (str): The URL to navigate to when the button is clicked.
        st_col (Streamlit Column, optional): The Streamlit column to render the button in. If None, defaults to main container.

    Returns:
        None
    """
    if st_col:
        st_col.markdown(f"[{text}]({url})", unsafe_allow_html=True)
    else:
        st.markdown(f"[{text}]({url})", unsafe_allow_html=True)

def create_st_button_with_color(text, url, st_col=None):
    """
    Creates a clickable button in Streamlit that links to a specified URL with a custom color.

    Parameters:
        text (str): The text displayed on the button.
        url (str): The URL to navigate to when the button is clicked.
        st_col (Streamlit Column, optional): The Streamlit column to render the button in. If None, defaults to main container.

    Returns:
        None
    """
    button_html = f"""
    <a href="{url}" target="_blank" style="text-decoration: none; color: #2196F3; font-weight: bold; display: block; margin-bottom: 15px;">
        {text}
    </a>
    """
    if st_col:
        st_col.markdown(button_html, unsafe_allow_html=True)
    else:
        st.markdown(button_html, unsafe_allow_html=True)