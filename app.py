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
import sub_apps.regex_generator as rg
import sub_apps.entity_extraction as ee

st.set_page_config(page_title="Chadi's 1 month of genAI", page_icon=":tada:", layout="wide")

# navigation
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["Home", "Summarize Meetings", "Research Writer", "Semantic Search", "LinkedIn Chat", "Flight Search", "Email Composer", "Tagline Generator", "Doc Editor", "Email Title", "Regex Generator", "Entity Extractor"])

if choice == "Home":
    # home page
    st.title("Month of genAI")
    st.write("""
    ### Technologies Used in QuietInnovator/one_month_in_genai

    ## 🛠️ Languages
    - Python

    ## 🌐 Frameworks & Libraries
    - Streamlit (for interactive web apps)
    - Google Generative AI SDK (`google-generativeai`)
    - OpenAI (optional, mentioned in code samples)
    - Requests (HTTP requests)
    - OS, sys, dotenv (Python standard and utility libraries)

    ## 📦 Project Structure
    - Modular app design (separate folders for sub-apps)
    - Main entry point: app.py (Streamlit)
    - requirements.txt for Python dependencies

    ## 🚀 Deployment
    - Designed for deployment on Heroku (per README)
    - Custom domain plans (e.g., abifadel.net)

    ## 📝 Features/Other Tools
    - Use of `.env` files and dotenv for environment variables
    - Git for version control
    - README documentation for learning journey and project roadmap

    ## 📂 Example Directory Layout
    ```
    one_month_in_genai/
    ├── sub_apps/              # Modular sub-apps
    ├── app.py                 # Main Streamlit app
    ├── requirements.txt       # Dependencies
    ├── .gitignore
    └── README.md
    ```
    ---

    This repository documents a month-long exploration of Generative AI, focusing on modular Python apps with Streamlit UIs and Google’s Generative AI SDK, intended for both learning and deployment.
    """)

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