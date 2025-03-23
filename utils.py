import re
import markdown
from google import genai

client = genai.Client(api_key="AIzaSyC9phEzmwI8zEx6o3ohlbdT9yeUyfKmvaE")

def gemini_generate(prompt: str) -> str:
    """
    Calls the Gemini model using the Google GenAI client with an advanced prompt.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text

def generate_clause(clause_title: str, base_text: str, customization: dict) -> str:
    """
    Builds an advanced prompt for a single clause. Converts Markdown to HTML.
    """
    tone = customization.get("TONE", "formal")
    jurisdiction = customization.get("JURISDICTION", "Default Jurisdiction")
    base_text_str = base_text.strip() if base_text.strip() else "None provided"
    prompt = (
        f"Generate a '{clause_title}' clause for a legal contract. "
        f"Ensure compliance with {jurisdiction} law and write it in a {tone} tone. "
        f"Base clause text: '{base_text_str}'.\n\n"
        "Please provide a complete clause. If more info is needed, include a clarifying question in square brackets. "
        "End with bullet-point suggestions or improvements if relevant."
    )
    model_output = gemini_generate(prompt)
    return markdown.markdown(model_output)

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
    Extracts the suggestions portion and the main contract portion.
    Returns (contract_body, suggestions_text).

    Example logic: If suggestions start at <hr><h4>Additional Suggestions
    and continue to the end, we can separate them.
    """
    pattern = re.compile(r'(<hr><h4>Additional Suggestions.*)', re.DOTALL)
    match = pattern.search(contract_html)
    if match:
        main_part = contract_html[: match.start()].strip()
        suggestions_part = contract_html[match.start():].strip()
        return main_part, suggestions_part
    else:
        # No suggestions found
        return contract_html, ""

def incorporate_suggestions_with_model(contract_body: str, suggestions: str) -> str:
    """
    Feeds the contract body + suggestions to the model, asking it to merge them
    into a final version with no additional suggestions.
    """
    # Convert <...> HTML tags to plain text for the prompt (optional).
    # Or just feed raw HTML. We'll do a quick strip of tags for clarity:
    plain_contract = re.sub(r'<[^>]+>', '', contract_body)
    plain_suggestions = re.sub(r'<[^>]+>', '', suggestions)

    prompt = (
        "Below is a contract and a set of suggestions. "
        "Please merge these suggestions into the contract, producing a final version. "
        "Do not add any new suggestions or analysis. Provide the final contract text only.\n\n"
        "CONTRACT:\n"
        f"{plain_contract}\n\n"
        "SUGGESTIONS:\n"
        f"{plain_suggestions}\n\n"
        "Return the final contract text only, with no extra bullet points or disclaimers."
    )
    result = gemini_generate(prompt)
    # We'll interpret the result as plain text. If there's any Markdown, convert it:
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

    # Main clauses
    clauses_block = ""
    for title, base_text in clauses.items():
        clause_html = generate_clause(title, base_text, customization)
        clauses_block += f"<h3>{title}</h3><div>{clause_html}</div><hr>"

    # Additional clauses
    other_block = ""
    if other_clauses:
        for title, base_text in other_clauses.items():
            clause_html = generate_clause(title, base_text, customization)
            other_block += f"<h3>{title}</h3><div>{clause_html}</div><hr>"

    # Suggestions
    suggestions_html = generate_suggestions(customization)

    return (
        header
        + clauses_block
        + other_block
        + signature_block
        + "<hr><h4>Additional Suggestions (Detailed Analysis)</h4>"
        + f"<div>{suggestions_html}</div>"
    )
