from google import genai
import markdown

# We'll assume you already have a GenAI client or you can re-import from utils
client = genai.Client(api_key="YOUR_API_KEY")

def chat_with_model(contract_html: str, user_message: str) -> str:
    """
    Chat with the model about the existing contract. The user can request changes,
    clarifications, or updates. The model should output an updated contract or instructions.
    We'll keep it simple: pass the entire contract + user request to the model.
    """
    # Example prompt combining the existing contract with the user message.
    prompt = (
        "You are a legal contract assistant. The current contract is as follows:\n\n"
        f"{contract_html}\n\n"
        "User wants the following changes or clarifications:\n"
        f"{user_message}\n\n"
        "Please provide an updated contract reflecting these changes. If you need more information, "
        "append a clarifying question in square brackets. End with bullet-point suggestions for any additional improvements."
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    # Convert any Markdown to HTML for display
    return markdown.markdown(response.text)
