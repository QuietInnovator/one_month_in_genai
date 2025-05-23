import streamlit as st

def semantic_search_redirect():
    st.title("Semantic Search")
    st.write("This is the semantic search app")

    st.write("For technical reasons that have to do with libraries, We need to ask you to go to this link:")
    st.write("[Semantic Search App](https://semanticsearchapp.streamlit.app/)")

    st.write("Once you have completed the demonstration, please return to this app To continue with the exploration")

if __name__ == "__main__":
    semantic_search_redirect()