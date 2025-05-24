import streamlit as st
from openai import OpenAI
import os

def description():
    st.markdown("""
    My eighth app is a smart document editor that uses a LLM to edit documents.
    It has a simple interface with the right fields and is a great help for editing documents.
    """)

# =========================
# CONFIGURATION & SETUP
# =========================

def get_api_key():
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        st.stop()
    return api_key

def init_openai_client():
    return OpenAI(api_key=get_api_key())

client = init_openai_client()

# =========================
# LLM HELPER
# =========================

def call_llm(prompt, input_text, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text},
        ],
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

# =========================
# UI COMPONENTS
# =========================

def main_title():
    st.title("Smart Document Editor ✍️")
    st.write("Paste your text below and use the buttons to enhance your writing with AI:")

def text_input_area():
    return st.text_area(
        "Your document text here...",
        height=300,
        placeholder="Type or paste your document here..."
    )

def action_buttons():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Summarize"):
            return "summarize"
    with col2:
        if st.button("Rewrite (Formal)"):
            return "rewrite_formal"
    with col3:
        if st.button("Improve Clarity"):
            return "clarify"
    with col4:
        if st.button("Make Concise"):
            return "concise"
    return None

def get_prompt(action):
    prompts = {
        "summarize": "Summarize the following text in 3-4 sentences.",
        "rewrite_formal": "Rewrite the following text in a more formal and professional tone.",
        "clarify": "Improve the clarity of the following text. Make it easy to understand.",
        "concise": "Rewrite the following text to be more concise without losing important information."
    }
    return prompts.get(action, "")

def display_output(output):
    if output:
        st.subheader("Editable AI Output")
        edited_output = st.text_area("Edit the AI's output as you wish:", value=output, height=250, key="output_editor")
        st.download_button("Download Output", edited_output, file_name="output.txt")

def footer():
    st.markdown("---")
    st.markdown("Powered by [OpenAI](https://openai.com) • Chadi Abi Fadel")

# =========================
# MAIN APP LOGIC
# =========================

def main():
    main_title()
    description()
    text_input = text_input_area()
    action = action_buttons()

    if action and not text_input.strip():
        st.warning("Please enter some text to process.")
        return

    if action and text_input.strip():
        prompt = get_prompt(action)
        with st.spinner("AI is working..."):
            try:
                output = call_llm(prompt, text_input)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                return
        display_output(output)

    footer()

if __name__ == "__main__":
    main()
