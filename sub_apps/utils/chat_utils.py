import openai

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