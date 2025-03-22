import os
import markdown
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

def extract_text_from_pdf(filepath: str) -> str:
    """
    Stub for extracting text from a PDF. In a real scenario, use PyPDF2 or similar.
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
        return "PyPDF2 not installed. Unable to parse PDF."

def extract_text_from_docx(filepath: str) -> str:
    """
    Stub for extracting text from a DOCX. Use python-docx or similar.
    """
    try:
        import docx
        doc = docx.Document(filepath)
        text_content = "\n".join([para.text for para in doc.paragraphs])
        return text_content
    except ImportError:
        return "python-docx not installed. Unable to parse DOCX."

def summarize_and_analyze(text_content: str) -> str:
    """
    Summarizes and deeply analyzes the given contract text using the model.
    """
    prompt = (
        "You are a legal assistant. Below is a contract text:\n\n"
        f"{text_content}\n\n"
        "Please provide a summary of the key points, then perform a deep analysis of potential risks, "
        "legal considerations, and any improvements needed. Format your response with headings and bullet points."
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return markdown.markdown(response.text)
