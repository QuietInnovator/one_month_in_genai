import streamlit as st
from google import genai
from google.genai import types

# ------------------ CONFIG ------------------
def get_gemini_config():
    return {
        "project": "superb-heaven-421314",
        "location": "us-central1",
        "model": "gemini-2.5-flash-preview-05-20",
        "prompt": """
You are a document entity extraction specialist. Given a document, your task is to extract the text value of the following entities and structure them as a table with the following columns:

date, amount

- you must return a table
- The values must only include text found in the document
- Do not normalize any entity value.
- If an entity is not found in the document, set the entity value to null.
""",
        "safety_settings": [
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "OFF"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "OFF"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "OFF"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "OFF"},
        ]
    }

# ------------------ GEMINI EXTRACTION LOGIC ------------------
def get_gemini_client(config):
    return genai.Client(
        vertexai=True,
        project=config["project"],
        location=config["location"],
    )

def build_contents(pdf_bytes, prompt):
    pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
    prompt_part = types.Part.from_text(text=prompt)
    return [
        types.Content(role="user", parts=[pdf_part, prompt_part])
    ]

def build_generate_content_config(safety_settings):
    return types.GenerateContentConfig(
        temperature=1,
        top_p=1,
        seed=0,
        max_output_tokens=65535,
        safety_settings=[
            types.SafetySetting(**setting) for setting in safety_settings
        ],
    )

def extract_entities_from_pdf(pdf_bytes):
    config = get_gemini_config()
    client = get_gemini_client(config)
    contents = build_contents(pdf_bytes, config["prompt"])
    generate_content_config = build_generate_content_config(config["safety_settings"])

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=config["model"],
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text
    return response_text

# ------------------ STREAMLIT UI ------------------
def main():
    st.title("PDF Entity Extraction (Gemini)")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded. Processing...")
        with st.spinner("Extracting entities using Gemini..."):
            try:
                pdf_bytes = uploaded_file.read()
                output = extract_entities_from_pdf(pdf_bytes)
                st.subheader("Extraction Result")
                st.markdown(output)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Please upload a PDF file to begin.")

if __name__ == "__main__":
    main()
