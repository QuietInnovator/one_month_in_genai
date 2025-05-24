import streamlit as st
import openai
import os


def get_text_input():
    """
    Function to get text input from the user
    Returns:
        str: The text input from the user
    """
    import streamlit as st
    return st.text_input("Enter your text here:")

def get_number_input():
    """
    Function to get number input from the user
    Returns:
        float: The number input from the user
    """
    import streamlit as st
    return st.number_input("Enter a number:", min_value=0.0, step=0.1)

def get_selectbox_input(options):
    """
    Function to get selection input from the user
    Args:
        options (list): List of options to choose from
    Returns:
        str: The selected option
    """
    import streamlit as st
    return st.selectbox("Select an option:", options)

def get_business_info():
    """
    Function to get business information from the user
    Returns:
        dict: Dictionary containing business information
    """
    business_info = {
        "name": st.text_input("Business Name:"),
        "industry": st.text_input("Industry/Sector:"),
        "description": st.text_area("Business Description:", 
            help="Describe what your business does, its values, and target audience"),
        "unique_selling_points": st.text_area("Unique Selling Points:", 
            help="What makes your business different from competitors?"),
        "tone": st.selectbox("Desired Tagline Tone:", 
            options=["Professional", "Casual", "Humorous", "Inspirational", "Technical"])
    }
    return business_info

def generate_tagline(business_info):
    """
    Function to generate a tagline using OpenAI
    Args:
        business_info (dict): Dictionary containing business information
    Returns:
        str: Generated tagline
    """
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    prompt = f"""Generate a compelling business tagline for the following business:
    
    Business Name: {business_info['name']}
    Industry: {business_info['industry']}
    Description: {business_info['description']}
    Unique Selling Points: {business_info['unique_selling_points']}
    Desired Tone: {business_info['tone']}
    
    Please generate a short, memorable tagline that captures the essence of the business.
    The tagline should be no more than 8 words and should reflect the desired tone.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional copywriter specializing in creating compelling business taglines."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating tagline: {str(e)}")
        return None 

def main():
    st.title("Business Tagline Generator")
    st.write("Generate a compelling tagline for your business using AI.")

    # Get business information
    business_info = get_business_info()

    # Generate tagline button
    if st.button("Generate Tagline"):
        if not all([business_info['name'], business_info['industry'], business_info['description']]):
            st.warning("Please fill in all required fields (Business Name, Industry, and Description)")
        else:
            with st.spinner("Generating your tagline..."):
                tagline = generate_tagline(business_info)
                if tagline:
                    st.success("Here's your generated tagline:")
                    st.markdown(f"## {tagline}")
                    
                    # Add a copy button
                    st.button("Copy Tagline", 
                             on_click=lambda: st.write(f"Tagline copied to clipboard: {tagline}"))

if __name__ == "__main__":
    main() 