import streamlit as st

# Main function for the analysis pages
def show():
    # Set up the page
    st.title("Answer ALS Data Scripts")
    st.write("*Run a variety of internal Answer ALS data-related .py scripts from the browser.*")
    st.write("------")

    st.write("## Welcome to the Answer ALS Data Scripts App")
    st.write("This app is a compilation of various useful scripts which make our lives easier here at Answer ALS.")
    st.write("**Features**:")
    st.write("- Email Generator: Automatically generate initial emails for our data users. Provide an Excel file with the users' emails and the reason for the initial email correspondence.")
    st.write("-----")
    st.write("### **Get Started**: Use the sidebar to navigate through different sections and visualizations.")
    st.write("Source code: **ADD LINK HERE**")

    import os
    st.write("Current working directory:", os.getcwd())
    
