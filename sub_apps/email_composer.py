import streamlit as st

# ---- 1. Mock and Real LLM Functions ----

def llm_api_mock(text: str, action: str) -> str:
    if action == "Expand":
        return text + " This is an expanded version."
    elif action == "Make Polite":
        return "Please note: " + text
    elif action == "Summarize":
        return "Summary: " + " ".join(text.split()[:5])
    else:
        return text

def llm_api_openai(text: str, action: str, openai_api_key: str) -> str:
    import openai
    client = openai.OpenAI(api_key=openai_api_key)

    if action == "Expand":
        prompt = f"Expand this message:\n{text}"
    elif action == "Make Polite":
        prompt = f"Rewrite this message to sound more polite:\n{text}"
    elif action == "Summarize":
        prompt = f"Summarize this email in 5 words:\n{text}"
    else:
        prompt = text

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI API error: {e}"

# ---- 2. LLM Dependency Switch ----

def get_llm_handler(mode: str, openai_api_key: str = None):
    if mode == "Mock":
        return lambda text, action: llm_api_mock(text, action)
    elif mode == "OpenAI":
        if not openai_api_key:
            return lambda text, action: "Please enter your OpenAI API key."
        return lambda text, action: llm_api_openai(text, action, openai_api_key)
    else:
        raise ValueError("Unknown LLM mode.")

# ---- 3. Streamlit UI ----
def email_composer_ui():
    st.title("LLM-Powered Email Composer")

    if "to" not in st.session_state: st.session_state.to = ""
    if "subject" not in st.session_state: st.session_state.subject = ""
    if "body" not in st.session_state: st.session_state.body = ""

    # LLM mode selector
    llm_mode = st.radio("Choose LLM backend:", ["Mock", "OpenAI"])
    openai_api_key = ""
    if llm_mode == "OpenAI":
        openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")
        if not openai_api_key:
            st.warning("OpenAI mode requires an API key.")

    llm_handler = get_llm_handler(llm_mode, openai_api_key)

    with st.form("email_form"):
        to = st.text_input("To", st.session_state.to)
        subject = st.text_input("Subject", st.session_state.subject)
        body = st.text_area("Body", st.session_state.body, height=150)
        
        # INSERT WORD/CHARACTER COUNTER HERE - RIGHT AFTER BODY INPUT
        # Calculate counts
        text = body
        word_count = len([word for word in text.split() if word.strip()])
        char_count = len(text)
        char_no_spaces = len(text.replace(" ", "").replace("\n", ""))
        
        # Create visual indicators
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Words", word_count)
            if word_count > 300:
                st.caption("📝 Approaching long email territory")
                
        with col2:
            st.metric("Characters", char_count)
        
        with col3:
            st.metric("Chars (no spaces)", char_no_spaces)
        
        # Add reading time estimate
        reading_time = max(1, round(word_count / 230, 1))
        st.caption(f"📚 Estimated reading time: {reading_time} minute{'s' if reading_time != 1 else ''}")
        
        # Optional readability indicator
        sentences = len([s for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()])
        if sentences > 0:
            avg_words_per_sentence = word_count / sentences
            if avg_words_per_sentence > 25:
                st.caption("⚠️ Consider shorter sentences for better readability")
        
        # CONTINUE WITH EXISTING CODE
        col1, col2, col3 = st.columns(3)
        with col1:
            expand_btn = st.form_submit_button("Expand")
        with col2:
            polite_btn = st.form_submit_button("Make Polite")
        with col3:
            summarize_btn = st.form_submit_button("Summarize")

        new_body = body
        if expand_btn:
            new_body = llm_handler(body, "Expand")
        elif polite_btn:
            new_body = llm_handler(body, "Make Polite")
        elif summarize_btn:
            new_body = llm_handler(body, "Summarize")

        # Save new values to session state
        st.session_state.to = to
        st.session_state.subject = subject
        st.session_state.body = new_body
    # --- Live Preview ---
    st.write("### Preview of Updated Email")
    st.write(f"**To:** {st.session_state.to}")
    st.write(f"**Subject:** {st.session_state.subject}")
    st.write(f"**Body:**\n{st.session_state.body}")

    # --- Instructions for Manual Testing ---
    st.markdown("""
    **Manual Test Cases:**  
    - Use Mock or OpenAI as backend.
    - Validate the body updates for each button:
        - "Expand": appends "This is an expanded version." (mock) or uses GPT (OpenAI)
        - "Make Polite": prepends "Please note: " (mock) or uses GPT (OpenAI)
        - "Summarize": returns 5-word summary (mock) or uses GPT (OpenAI)
    - OpenAI mode requires your API key.
    """)
