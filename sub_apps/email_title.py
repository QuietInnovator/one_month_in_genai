import streamlit as st
from openai import OpenAI

def description():
    st.subheader("Description")
    st.write("This app generates subject lines for emails based on the email text and the tone selected.")
    st.write("The app uses the OpenAI API to generate the subject lines.")
    st.write("The app is a simple web application that allows you to write an email and select the tone of the email.")
    st.write("The app then generates 5 subject lines for the email based on the tone selected.")
    st.write("The app then allows you to edit the subject lines and the tone of the email.")
# ========================
# ---- OpenAI Utils ------
# ========================

def get_openai_key():
    return st.secrets["OPENAI_API_KEY"]

def get_openai_client():
    return OpenAI(api_key=get_openai_key())

def generate_titles_with_tones(email_text, tones):
    client = get_openai_client()
    results = []
    for tone in tones:
        prompt = (
            f"Write a catchy subject line for the following email. "
            f"The subject line should follow this tone: {tone}.\n\n"
            f"Email:\n{email_text}\n\n"
            f"Subject line ({tone} tone):"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=24,
            n=1,
            temperature=0.7,
        )
        subject_line = response.choices[0].message.content.strip().replace('"', '')
        results.append({"title": subject_line, "tone": tone})
    return results

# ==========================
# ---- UI Components -------
# ==========================

DEFAULT_TONES = ["Professional", "Friendly", "Urgent", "Excited", "Casual"]

def email_input():
    st.write("Write your email below:")
    return st.text_area(
        "Email",
        value=st.session_state.get('email_text', ''),
        height=200,
        key='email_text'
    )

def tone_selector():
    st.write("Select tones to generate subject lines in:")
    return st.multiselect(
        "Tones",
        options=DEFAULT_TONES,
        default=DEFAULT_TONES[:5],
        key='tones_selected'
    )

def editable_titles_section(num=5):
    st.write("Suggested Titles (edit both the title and the tone):")
    for i in range(num):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.session_state['titles'][i]['title'] = st.text_input(
                f"Title {i+1}",
                value=st.session_state['titles'][i]['title'],
                key=f"title_{i}"
            )
        with col2:
            st.session_state['titles'][i]['tone'] = st.text_input(
                f"Tone {i+1}",
                value=st.session_state['titles'][i]['tone'],
                key=f"tone_{i}"
            )

# ========================
# ---- Main App ----------
# ========================

def main():
    st.title("Email Title Generator with Tone")
    description()
    if 'titles' not in st.session_state:
        st.session_state['titles'] = [{"title": "", "tone": ""} for _ in range(5)]
    if 'email_text' not in st.session_state:
        st.session_state['email_text'] = ''
    if 'tones_selected' not in st.session_state:
        st.session_state['tones_selected'] = DEFAULT_TONES[:5]

    email_text = email_input()
    tones_selected = tone_selector()

    if st.button("Generate Titles"):
        if email_text.strip():
            titles_and_tones = generate_titles_with_tones(email_text, tones_selected)
            # Pad to 5 suggestions for consistent UI
            st.session_state['titles'] = (
                titles_and_tones + [{"title": "", "tone": ""}] * (5 - len(titles_and_tones))
            )
        else:
            st.warning("Please write an email first!")

    editable_titles_section()

if __name__ == "__main__":
    main()
