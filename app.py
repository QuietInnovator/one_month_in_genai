# imports
import streamlit as st
import sub_apps.summarize_meetings as sm
import sub_apps.research_writer as rw

import openai

st.set_page_config(page_title="Chadi's 1 month of genAI", page_icon=":tada:", layout="wide")

# navigation
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["Home", "Summarize Meetings", "Research Writer"])

if choice == "Home":
    # home page
    st.title("Month of genAI")
    st.write("This is a portfolio of the projects I've done in the last month of playing around with genAI")
    st.write("I've used the following tools:")
    st.write("1. Cursor")
    st.write("2. Streamlit")
    st.write("3. ")
    st.write("4. CrewAI")
    st.write("5. Cursor")
elif choice == "Summarize Meetings":
    # jira page
    st.title("Summarize Meetings")
    sm.summaryapp()
elif choice == "Research Writer":
    # research writer page
    st.title("Research Writer")
    rw.research_writer_redirect()
