# imports
import streamlit as st
import sub_apps.home as h
import sub_apps.summarize_meetings as sm
import sub_apps.research_writer as rw
import sub_apps.semantic_search as ss
import sub_apps.linkedin_chat as lc
import sub_apps.flight_search as fs
import sub_apps.email_composer as ec
import sub_apps.tagline_generator as tg 
import sub_apps.doc_editor as de
import sub_apps.email_title as et
import sub_apps.regex_generator as rg
import sub_apps.entity_extraction as ee
import sub_apps.schedule_generator as sg

st.set_page_config(page_title="Chadi's 1 month of genAI", page_icon=":tada:", layout="wide")

# navigation
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["Home", "Summarize Meetings", "Research Writer", "Semantic Search", "LinkedIn Chat", "Flight Search", "Email Composer", "Tagline Generator", "Doc Editor", "Email Title", "Regex Generator", "Entity Extractor", "Schedule Generator"])

if choice == "Home":
    h.main()

elif choice == "Summarize Meetings":
    # jira page
    st.title("Summarize Meetings")
    sm.summaryapp()
elif choice == "Research Writer":
    # research writer page
    st.title("Research Writer")
    rw.research_writer_redirect()

elif choice == "Semantic Search":
    # semantic search page
    ss.semantic_search_redirect()

elif choice == "LinkedIn Chat":
    # linkedin chat page
    lc.main()

elif choice == "Flight Search":
    # flight search page
    fs.main()

elif choice == "Email Composer":
    # email composer page
    ec.email_composer_ui()

elif choice == "Tagline Generator":
    # tagline generator page
    tg.main()

elif choice == "Doc Editor":
    # doc editor page
    de.main()

elif choice == "Email Title":
    # email title page
    et.main()

elif choice == "Regex Generator":
    # regex generator page
    rg.main()

elif choice == "Entity Extractor":
    # entity extractor page
    ee.main()

elif choice == "Schedule Generator":
    # schedule generator page
    sg.main()