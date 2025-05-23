import streamlit as st

#----------- description ----------
def description():
    """
    Description of the app
    input: none
    output: none
    """
    st.subheader("Description")
    st.write("""
             My third project Was inspired by the advancements that we can see In the artificial intelligence space.
             We are now search by meaning, not just by keywordss.
             So the motivation for this project is to explore semantic search with the Facebook AI semantic search model.
             """)


def semantic_search_redirect():
    st.title("Semantic Search")
    st.write("This is the semantic search app")

    st.write("For technical reasons that have to do with libraries, We need to ask you to go to this link:")
    st.write("[Semantic Search App](https://semanticsearchapp.streamlit.app/)")

    st.write("Once you have completed the demonstration, please return to this app To continue with the exploration")

if __name__ == "__main__":
    semantic_search_redirect()