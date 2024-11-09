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

def get_file_path(file_name, dir_path="./data"):
    """
    Constructs the absolute path to a file given its name and a directory path.

    Parameters:
        file_name (str): The name of the file.
        dir_path (str): The relative or absolute directory path where the file is located.

    Returns:
        str: The absolute file path.

    Raises:
        FileNotFoundError: If the file does not exist in the specified directory.
    """
    file_path = os.path.join(dir_path, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_name}' not found in directory '{dir_path}'.")
    return file_path