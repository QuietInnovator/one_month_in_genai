# app.py
import json
import os
import requests
import streamlit as st
import openai

# ---------- OPENAI KEY ----------
def import_openai_key():
    openai.api_key = (
        st.secrets.get("OPENAI_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )

    if not openai.api_key:
        st.error(
            "⚠️  Please set your OpenAI key in Streamlit → Settings → Secrets "
            "or export OPENAI_API_KEY before running."
        )
        st.stop()

# ---------- TITLE ----------
def summary_welcome():
    """
    Welcome message and file uploader
    input: none
    output: uploaded file
    """
    
    st.title("🧾 auto summarizationr")
    st.write("""
    Upload a plain‑text file, let GPT build a Jira issue payload,  
    then optionally POST it to **Webhook.site** (or any webhook endpoint).
    """)

    # ---------- INPUTS ----------
    uploaded = st.file_uploader("📄  Upload a .txt file", type=["txt"])
    return uploaded

# ---------- GENERATE ----------
def generate_summary(uploaded):
    """
    Generate a summary of the uploaded file
    input: uploaded file
    output: summary
    """
    if st.button("Generate Summary") and uploaded:
        text = uploaded.read().decode("utf‑8", errors="ignore")

        st.subheader("Input text")
        st.text_area("Contents", text, height=200, disabled=True)

        # --- Summarize ---
        summarize_prompt = f"""
        Summarize the following meeting notes or text into clear, concise bullet points.

        Input:
        \"\"\"{text}\"\"\"

        Bullet points:
        """
        with st.spinner("Summarizing meeting notes..."):
            try:
                summary_resp = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": summarize_prompt}],
                    temperature=0.3,
                )
                summary = summary_resp.choices[0].message.content
                st.subheader("Meeting Summary")
                st.markdown(summary)
            except Exception as e:
                st.error(f"❌ Summarization error: {e}")
                st.stop()

def summaryapp():
    """
    Main function to run the summary app
    input: none
    output: none
    """
    import_openai_key()
    uploaded = summary_welcome()
    generate_summary(uploaded)