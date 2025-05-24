# imports
import streamlit as st
import sub_apps.summarize_meetings as sm
import sub_apps.research_writer as rw
import sub_apps.semantic_search as ss
import sub_apps.linkedin_chat as lc
import sub_apps.flight_search as fs
import sub_apps.email_composer as ec
import sub_apps.tagline_generator as tg 
import sub_apps.doc_editor as de
import sub_apps.email_title as et

st.set_page_config(page_title="Chadi's 1 month of genAI", page_icon=":tada:", layout="wide")

# navigation
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["Home", "Summarize Meetings", "Research Writer", "Semantic Search", "LinkedIn Chat", "Flight Search", "Email Composer", "Tagline Generator", "Doc Editor", "Email Title"])

if choice == "Home":
    # home page
    st.title("Month of genAI")
    st.write("This is a portfolio of the projects I've done in the last month of playing around with genAI")
    st.write("I've used the following tools:")
    st.write("1. Cursor")
    st.write("2. Streamlit")
    st.write("3. Facebook AI Semantic Search (FAISS)")
    st.write("4. CrewAI")
    st.write("5. Cursor")
    st.write("6. OpenAI")
    st.write("7. PyPDF2")
    st.write("8. Streamlit Chat")
    st.write("9. Streamlit Secrets")
    st.write("10. Serper")
    st.write("11. Exa")
    st.write("12. Pandas")
    st.write("13. Datetime")
    st.write("14. Requests")

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