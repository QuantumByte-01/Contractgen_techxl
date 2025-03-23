import re
import markdown
from google import genai
import requests

client = genai.Client(api_key="AIzaSyC9phEzmwI8zEx6o3ohlbdT9yeUyfKmvaE")

def gemini_generate(prompt: str) -> str:
    improved_prompt = (
        prompt
        + "\n\nPlease provide the complete text using formal legal language. "
          "If further details are required, include a clarifying question in square brackets. "
          "At the end of your response, list detailed suggestions or improvements as bullet points."
    )
    response = client.models.generate_content(model="gemini-2.0-flash", contents=improved_prompt)
    return response.text

def generate_clause(clause_title: str, base_text: str, customization: dict) -> str:
    tone = customization.get("TONE", "formal")
    jurisdiction = customization.get("JURISDICTION", "Default Jurisdiction")
    base_text_str = base_text.strip() if base_text.strip() else "None provided"
    prompt = (
        f"Generate a '{clause_title}' clause for a legal contract. "
        f"Ensure compliance with {jurisdiction} law and write it in a {tone} tone. "
        f"Base clause text: '{base_text_str}'.\n\n"
        "Please provide a complete clause. If more info is needed, include a clarifying question in square brackets. "
        "End with bullet-point suggestions if relevant."
    )
    model_output = gemini_generate(prompt)
    return markdown.markdown(model_output)
def search_context(query: str) -> str:
    """
    Uses the Google Custom Search API to fetch additional context.
    Returns a structured string with context information.
    """
    import requests
    api_key = "AIzaSyCN4Ze3QgbbSmOMcLlJZAj4828ijbaG1Nk"
    cx = "a28fa63ae51994dac"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json().get("items", [])
            context = "\n".join([item.get("snippet", "") for item in results[:3]])
            return "ADDITIONAL CONTEXT:\n" + context
        else:
            return ""
    except Exception as e:
        return ""


def parse_clauses(clauses_input: str) -> dict:
    """
    Parses multi-clause input in the format:
      Clause Title:
      [Clause content]
    """
    clause_dict = {}
    blocks = re.split(r'\n\s*\n', clauses_input.strip())
    pattern = re.compile(r'^(.*?):\s*\[(.*?)\]\s*$', re.DOTALL)
    for block in blocks:
        match = pattern.match(block.strip())
        if match:
            title = match.group(1).strip()
            content = match.group(2).strip()
            clause_dict[title] = content
    return clause_dict

def remove_suggestions_from_html(contract_html: str) -> str:
    """
    Removes the suggestions/analysis block from the contract HTML for export.
    For instance, if suggestions appear after <hr><h4>Additional Suggestions...
    """
    pattern = re.compile(r'(<hr><h4>Additional Suggestions.*)', re.DOTALL)
    cleaned = re.sub(pattern, '', contract_html)
    return cleaned

def extract_suggestions_from_html(contract_html: str) -> (str, str):
    """
    Separates the main contract (everything before the suggestions block) and the suggestions.
    Assumes suggestions start with a specific marker.
    """
    pattern = re.compile(r'(<hr><h4>Additional Suggestions.*)', re.DOTALL)
    match = pattern.search(contract_html)
    if match:
        main_body = contract_html[:match.start()].strip()
        suggestions_block = contract_html[match.start():].strip()
        return main_body, suggestions_block
    else:
        return contract_html, ""

def incorporate_suggestions_with_model(contract_body: str, suggestions: str) -> str:
    """
    Feeds the main contract and suggestions to the model to produce a final version with no suggestions.
    """
    plain_contract = re.sub(r'<[^>]+>', '', contract_body)
    plain_suggestions = re.sub(r'<[^>]+>', '', suggestions)
    
    prompt = (
        "Below is a contract and a set of suggestions. "
        "Please merge these suggestions into the contract and produce a final version with no additional suggestions. "
        "Return the final contract text with proper formatting (using HTML tags for headings, lists, etc.) only.\n\n"
        "CONTRACT:\n" + plain_contract + "\n\n"
        "SUGGESTIONS:\n" + plain_suggestions + "\n\n"
        "Final Contract:"
    )
    result = gemini_generate(prompt)
    return markdown.markdown(result)


def generate_suggestions(customization: dict) -> str:
    """
    Requests additional suggestions or improvements from the model.
    """
    prompt = (
        "Based on the current contract, please provide additional suggestions or improvements. "
        "Include a detailed analysis for each suggestion. Format them as bullet points."
    )
    model_output = gemini_generate(prompt)
    return markdown.markdown(model_output)

def generate_contract(contract_type: str, details: dict, clauses: dict, other_clauses: dict, customization: dict) -> str:
    """
    Generates a contract (HTML) with:
      - a header (based on contract_type)
      - each clause
      - additional clauses
      - signature block
      - appended suggestions at the end
    """
    if contract_type == "nda":
        header = f"""
        <h2>NON-DISCLOSURE AGREEMENT</h2>
        <p><strong>Effective Date:</strong> {details.get('EFFECTIVE_DATE')}</p>
        <p><strong>Party A:</strong> {details.get('PARTY_A')}</p>
        <p><strong>Party B:</strong> {details.get('PARTY_B')}</p>
        <p><strong>Jurisdiction:</strong> {customization.get('JURISDICTION')}</p>
        <p><strong>Tone:</strong> {customization.get('TONE')}</p>
        <hr>
        """
        signature_block = """
        <h4>Signatures</h4>
        <p>Party A Signature: ______________________</p>
        <p>Party B Signature: ______________________</p>
        <p>Date: ______________________</p>
        <p>Witness: ______________________</p>
        """
    elif contract_type == "service_agreement":
        header = f"""
        <h2>SERVICE AGREEMENT</h2>
        <p><strong>Effective Date:</strong> {details.get('EFFECTIVE_DATE')}</p>
        <p><strong>Service Provider:</strong> {details.get('SERVICE_PROVIDER')}</p>
        <p><strong>Client:</strong> {details.get('CLIENT')}</p>
        <p><strong>Jurisdiction:</strong> {customization.get('JURISDICTION')}</p>
        <p><strong>Tone:</strong> {customization.get('TONE')}</p>
        <hr>
        """
        signature_block = """
        <h4>Signatures</h4>
        <p>Service Provider Signature: ______________________</p>
        <p>Client Signature: ______________________</p>
        <p>Date: ______________________</p>
        <p>Witness: ______________________</p>
        """
    elif contract_type == "employment_contract":
        header = f"""
        <h2>EMPLOYMENT CONTRACT</h2>
        <p><strong>Effective Date:</strong> {details.get('EFFECTIVE_DATE')}</p>
        <p><strong>Employer:</strong> {details.get('EMPLOYER')}</p>
        <p><strong>Employee:</strong> {details.get('EMPLOYEE')}</p>
        <p><strong>Jurisdiction:</strong> {customization.get('JURISDICTION')}</p>
        <p><strong>Tone:</strong> {customization.get('TONE')}</p>
        <hr>
        """
        signature_block = """
        <h4>Signatures</h4>
        <p>Employer Signature: ______________________</p>
        <p>Employee Signature: ______________________</p>
        <p>Date: ______________________</p>
        <p>Witness: ______________________</p>
        """
    elif contract_type == "rental_agreement":
        header = f"""
        <h2>RENTAL AGREEMENT</h2>
        <p><strong>Effective Date:</strong> {details.get('EFFECTIVE_DATE')}</p>
        <p><strong>Landlord:</strong> {details.get('LANDLORD')}</p>
        <p><strong>Tenant:</strong> {details.get('TENANT')}</p>
        <p><strong>Jurisdiction:</strong> {customization.get('JURISDICTION')}</p>
        <p><strong>Tone:</strong> {customization.get('TONE')}</p>
        <hr>
        """
        signature_block = """
        <h4>Signatures</h4>
        <p>Landlord Signature: ______________________</p>
        <p>Tenant Signature: ______________________</p>
        <p>Date: ______________________</p>
        <p>Witness: ______________________</p>
        """
    else:
        header = "<h2>Contract</h2>"
        signature_block = "<h4>Signatures</h4>"

    clauses_block = ""
    for title, base_text in clauses.items():
        clause_html = generate_clause(title, base_text, customization)
        clauses_block += f"<h3>{title}</h3><div>{clause_html}</div><hr>"

    other_block = ""
    if other_clauses:
        for title, base_text in other_clauses.items():
            clause_html = generate_clause(title, base_text, customization)
            other_block += f"<h3>{title}</h3><div>{clause_html}</div><hr>"

    suggestions_html = generate_suggestions(customization)

    return (
        header
        + clauses_block
        + other_block
        + signature_block
        + "<hr><h4>Additional Suggestions (Detailed Analysis)</h4>"
        + f"<div>{suggestions_html}</div>"
    )
