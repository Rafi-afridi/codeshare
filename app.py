import streamlit as st
import glob
import os
import time

def save_to_temp_file(content):
    with open("temp.txt", "w") as file:
        file.write(content)
        
def read_temp_file():
    if os.path.exists("temp.txt"):
        with open("temp.txt", "r") as file:
            return file.read()
    return ""
    
def main():
    st.title("Jugar Codeshare")

    # List all files in the current directory
    files = glob.glob("data/*")
    
    # Create a dropdown to select a file
    selected_file = st.selectbox("Select a file", files)
        
    # Password input field
    password = st.text_input("Enter Password", type="password")
    
    # Upload file functionality
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "ipynb", "md", "py", "sql"])

    if uploaded_file:
        # Save the uploaded file to the data folder with the same extension
        with open(os.path.join("data", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getvalue())
        st.success("File uploaded successfully!")
        
    if password == "sleep":
        if selected_file:
            # Read the contents of the selected file
            with open(selected_file, 'r') as file:
                file_contents = file.read()
    
            # Display the contents of the selected file in a text area
            st.text_area("File Content", file_contents, height=1000)
            
            # Download button to download the selected file
            st.download_button(label="Download File", data=open(selected_file, 'rb'), file_name=os.path.basename(selected_file))
            
    else:
        st.write("Enter password to see code")
    
    # Delete file functionality
    if st.button("Delete File"):
        try:
            os.remove(selected_file)
            st.success(f"File '{selected_file}' deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting file: {e}")
            
if __name__ == "__main__":
    main()
