import streamlit as st

def main():
    st.title("My Advanced Streamlit App")

    # Add a sidebar with options
    st.sidebar.title("Options")
    option = st.sidebar.selectbox("Select an option", ["Option 1", "Option 2", "Option 3"])

    # Display different content based on the selected option
    if option == "dupa":
        st.write("You selected Option 1")
    elif option == "Option 2":
        st.write("You selected Option 2")
    else:
        st.write("You selected Option 3")

    # Add a slider for selecting a value
    value = st.slider("Select a value", 0, 100, 50)
    st.write("Selected value:", value)

    # Add a button
    if st.button("Click me"):
        st.write("Button clicked!")

if __name__ == "__main__":
    main()