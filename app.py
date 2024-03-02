import streamlit as st
import glob

def main():
    st.title("Jugar Codeshare")

    # List all files in the current directory
    files = glob.glob("data/*")

    # Create a dropdown to select a file
    selected_file = st.selectbox("Select a file", files)

    if selected_file:
        # Read the contents of the selected file
        with open(selected_file, 'r') as file:
            file_contents = file.read()

        # Display the contents of the selected file in a text area
        st.text_area("File Content", file_contents, height=1000)

if __name__ == "__main__":
    main()
