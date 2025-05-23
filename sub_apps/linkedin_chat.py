import streamlit as st
from streamlit_chat import message as chat_message
import openai
import PyPDF2
import openai

NAME = "Chadi"
PAGE_TITLE = "LinkedIn Chat"
PAGE_DESCRIPTION = "Chat with Chadi's LinkedIn profile."

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

#----------- description ----------
def description():
    """
    Description of the app
    input: none
    output: none
    """
    st.subheader("Description")
    st.write("""
            My fourth project solves yet another pain which is not having enough time to interview Interview all the job applicants.
             So this project provides away to chat with the persona of the applicant portrait by their LinkedIn profile
             """)

def chat_with_openai_stream(system_prompt, message, history):
    """
    Chat with OpenAI using streaming response.
    
    Args:
        system_prompt (str): The system prompt for the chat
        message (str): The user's message
        history (list): List of previous chat messages
        
    Returns:
        Generator: Stream of response chunks from OpenAI
    """
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        stream=True
    )
    return response

def create_system_prompt(name, summary_text, pdf_text):
    """
    Create the system prompt for the chat.
    
    Args:
        name (str): The name of the person being represented
        summary_text (str): The summary text
        pdf_text (str): The PDF profile text
        
    Returns:
        str: The formatted system prompt
    """
    return (
        f"You are acting as {name}. You are answering questions on {name}'s website, "
        f"particularly questions related to {name}'s career, background, skills and experience. "
        f"Your responsibility is to represent {name} for interactions on the website as faithfully as possible. "
        f"You are given a summary of {name}'s background and profile which you can use to answer questions. "
        f"Be professional and engaging. If you don't know the answer, say so.\n\n"
        f"## Summary:\n{summary_text}\n\n## Profile:\n{pdf_text}\n\n"
        f"With this context, please chat with the user, always staying in character as {name}."
    ) 
def extract_text_from_pdf(pdf_file):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_file: A file-like object containing the PDF data
        
    Returns:
        str: The extracted text from the PDF
    """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text 

def initialize_session_state():
    """Initialize session state variables."""
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = ""

def display_profile_info(pdf_text, summary_text):
    """Display the profile and summary information."""
    st.subheader("PDF Profile Information")
    st.text_area("Profile Text", pdf_text, height=300)

    st.subheader("Summary")
    st.text_area("Summary Text", summary_text, height=150)

def handle_chat_interaction():
    """Handle the chat interaction with the user."""
    st.subheader(f"Chat with {NAME}")

    user_message = st.chat_input("Ask a question about Chadi's background...")
    if user_message:
        st.session_state.history.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)

        response_text = ""
        with st.chat_message("assistant"):
            response_container = st.empty()
            for chunk in chat_with_openai_stream(
                st.session_state.system_prompt,
                user_message,
                st.session_state.history
            ):
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta.content or ""
                    response_text += delta
                    response_container.markdown(response_text + "▌")
            response_container.markdown(response_text)

        st.session_state.history.append({"role": "assistant", "content": response_text})

    # Display chat history
    for message in st.session_state.history:
        if message['role'] == 'user':
            chat_message(message['content'], is_user=True)
        else:
            chat_message(message['content'])

def main():
    """Main application function."""
    description()
    st.title(PAGE_TITLE)
    st.markdown(PAGE_DESCRIPTION)

    initialize_session_state()

    pdf_file = st.file_uploader("Upload PDF Profile", type="pdf")
    txt_file = st.file_uploader("Upload Summary Text", type="txt")

    if st.button("Display Profile"):
        if pdf_file is None or txt_file is None:
            st.error("Please upload both PDF and summary text files.")
        else:
            with st.spinner("Extracting information..."):
                pdf_text = extract_text_from_pdf(pdf_file)
                summary_text = txt_file.read().decode("utf-8")

            st.success("Profile extracted successfully!")
            display_profile_info(pdf_text, summary_text)
            
            # Set up the system prompt
            st.session_state.system_prompt = create_system_prompt(
                NAME,
                summary_text,
                pdf_text
            )

    # Handle chat interaction if system prompt is set
    if st.session_state.system_prompt:
        handle_chat_interaction()

if __name__ == "__main__":
    main()
    