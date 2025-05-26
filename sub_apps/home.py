import streamlit as st



def main():
    # home page
    st.title("Month of genAI")
    st.write("""
        This is a project that I've been working on for the past month. It's a collection of Streamlit apps that I've been working on to experiment with Generative AI.
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