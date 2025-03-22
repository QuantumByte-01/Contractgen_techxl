import re
import markdown
from google import genai

# Make sure you install google-genai: pip install google-generativeai

# Initialize the GenAI client with your API key.
client = genai.Client(api_key="AIzaSyC9phEzmwI8zEx6o3ohlbdT9yeUyfKmvaE")

def gemini_generate(prompt: str) -> str:
    """
    Calls the Gemini model using the Google GenAI client with an advanced prompt.
    The prompt instructs the model to output a complete clause or analysis in formal language.
    If further details are needed, a clarifying question is appended in square brackets.
    At the end, detailed suggestions or improvements are listed as bullet points.
    """
    improved_prompt = (
        prompt
        + "\n\nPlease provide the complete text using formal legal language. "
          "If further details are required, include a clarifying question in square brackets. "
          "At the end of your response, list detailed suggestions or improvements as bullet points."
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=improved_prompt
    )
    return response.text

def generate_clause(clause_title: str, base_text: str, customization: dict) -> str:
    """
    Builds an advanced prompt for a single clause based on the clause title, base text, and customization options.
    If base_text is empty, "None provided" triggers an example clause.
    Converts the model's Markdown output to HTML.
    """
    tone = customization.get("TONE", "formal")
    jurisdiction = customization.get("JURISDICTION", "Default Jurisdiction")
    prompt = (
        f"Generate a '{clause_title}' clause for a legal contract. "
        f"Ensure compliance with {jurisdiction} law and write it in a {tone} tone. "
        f"Base clause text: '{base_text if base_text.strip() else 'None provided'}'."
    )
    model_output = gemini_generate(prompt)
    return markdown.markdown(model_output)

def generate_suggestions(customization: dict) -> str:
    """
    Requests additional suggestions or improvements for the contract from the Gemini model.
    Converts any Markdown to HTML.
    """
    prompt = (
        "Based on the current contract, please provide additional suggestions or improvements. "
        "Include a detailed analysis for each suggestion. Format them as bullet points."
    )
    model_output = gemini_generate(prompt)
    return markdown.markdown(model_output)

def parse_clauses(clauses_input: str) -> dict:
    """
    Parses multi-clause input (e.g., "Clause Title:\n[Clause content]\n\nClause Title:\n[Clause content]")
    and returns a dict {clause_title: content}.
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
    Removes the 'Additional Suggestions' block from the contract HTML so we can export
    a version that has no suggestions or analysis. This is a simplistic approach.
    """
    # For example, if your suggestions block starts with <hr><h4>Additional Suggestions
    # and extends to the end, you could do:
    import re
    pattern = re.compile(r'(<hr><h4>Additional Suggestions.*)', re.DOTALL)
    cleaned = re.sub(pattern, '', contract_html)
    return cleaned

def generate_contract(contract_type: str, details: dict, clauses: dict, other_clauses: dict, customization: dict) -> str:
    """
    Generates the complete contract (HTML) by:
    1) Building a header (depends on contract_type)
    2) Generating each clause
    3) Generating other (additional) clauses
    4) Adding a signature block
    5) Appending a suggestions block
    """
    # Build header
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

    # Generate main clauses
    clauses_block = ""
    for title, base_text in clauses.items():
        generated_html = generate_clause(title, base_text, customization)
        clauses_block += f"<h3>{title}</h3><div>{generated_html}</div><hr>"

    # Generate additional (other) clauses
    other_block = ""
    if other_clauses:
        for title, base_text in other_clauses.items():
            generated_html = generate_clause(title, base_text, customization)
            other_block += f"<h3>{title}</h3><div>{generated_html}</div><hr>"

    # Gather suggestions at the end
    suggestions = generate_suggestions(customization)

    contract_html = (
        header
        + clauses_block
        + other_block
        + signature_block
        + "<hr><h4>Additional Suggestions (Detailed Analysis)</h4>"
        + f"<div>{suggestions}</div>"
    )
    return contract_html
