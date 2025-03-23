from google import genai
import markdown

client = genai.Client(api_key="AIzaSyC9phEzmwI8zEx6o3ohlbdT9yeUyfKmvaE")

def chat_with_model(current_contract: str, user_message: str) -> str:
    """
    Sends the current contract + user's request to the model, returning an updated contract.
    """
    prompt = (
        "You are a legal contract assistant. The current contract is as follows:\n\n"
        f"{current_contract}\n\n"
        "User wants the following changes or clarifications:\n"
        f"{user_message}\n\n"
        "Please provide an updated contract reflecting these changes. If more info is needed, "
        "append a clarifying question in square brackets. End with bullet-point suggestions for improvements."
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return markdown.markdown(response.text)
