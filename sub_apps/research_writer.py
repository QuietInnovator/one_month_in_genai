import streamlit as st

def research_writer_redirect():
    st.title("Research Writer")
    st.write("This is the research writer app")

    st.write("For technical reasons that have to do with libraries, We need to ask you to go to this link:")
    st.write("[Research Writer App](https://researchwriter.streamlit.app/)")

    st.write("Once you have completed the demonstration, please return to this app To continue with the exploration")

if __name__ == "__main__":
    research_writer_redirect()