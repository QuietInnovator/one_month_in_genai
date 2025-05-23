# imports
import streamlit as st
import sub_apps.summarize_meetings as sm

st.set_page_config(page_title="Chadi's 1 month of genAI", page_icon=":tada:", layout="wide")

# navigation
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["Home", "Summarize Meetings", "About", "Contact"])

if choice == "Home":
    # home page
    st.title("Month of genAI")
    st.write("This is a portfolio of the projects I've done in the last month of playing around with genAI")
    st.write("I've used the following tools:")
    st.write("1. Cursor")
    st.write("2. Jira")
    st.write("3. Notion")
    st.write("4. Cursor")
    st.write("5. Cursor")
elif choice == "Summarize Meetings":
    # jira page
    st.title("Summarize Meetings")
    sm.summaryapp()
elif choice == "About":
    # about page
    st.title("About")
elif choice == "Contact":
    # contact page
    st.title("Contact")