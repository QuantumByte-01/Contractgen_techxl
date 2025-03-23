import os
import markdown
from google import genai

client = genai.Client(api_key="AIzaSyC9phEzmwI8zEx6o3ohlbdT9yeUyfKmvaE")

def extract_text_from_pdf(filepath: str) -> str:
    """
    Stub for extracting text from PDF using PyPDF2.
    """
    try:
        import PyPDF2
        text_content = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
        return text_content
    except ImportError:
        return "PyPDF2 not installed."

def extract_text_from_docx(filepath: str) -> str:
    """
    Stub for extracting text from DOCX using python-docx.
    """
    try:
        import docx
        doc = docx.Document(filepath)
        text_content = "\n".join(para.text for para in doc.paragraphs)
        return text_content
    except ImportError:
        return "python-docx not installed."

def summarize_and_analyze(text_content: str) -> str:
    """
    Sends the contract text to the model for a summary + deep analysis.
    """
    prompt = (
        "You are a legal assistant. Below is a contract text:\n\n"
        f"{text_content}\n\n"
        "Please provide a concise summary of key points, then a deep analysis of potential risks, "
        "legal considerations, and improvements. Format your response with headings and bullet points."
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return markdown.markdown(response.text)
