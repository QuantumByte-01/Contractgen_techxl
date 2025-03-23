import os, io, docx, re
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from utils import (
    parse_clauses,
    generate_contract,
    remove_suggestions_from_html,
    extract_suggestions_from_html,
    incorporate_suggestions_with_model
)
from chat import chat_with_model
from analysis import extract_text_from_pdf, extract_text_from_docx, summarize_and_analyze
from html2docx import html2docx

html_content = "<p>This is a sample contract.</p>"
title = "Contract Document"

docx_content = html2docx(html_content, title)  

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/form")
def form():
    contract_type = request.args.get("contract_type", "nda")
    if contract_type == "service_agreement":
        return render_template("form_service.html")
    elif contract_type == "employment_contract":
        return render_template("form_employment.html")
    elif contract_type == "rental_agreement":
        return render_template("form_rental.html")
    else:
        return render_template("form_nda.html")

@app.route("/generate", methods=["POST"])
def generate():
    contract_type = request.form.get("contract_type", "nda")
    other_clauses = {}

    if contract_type == "nda":
        details = {
            "EFFECTIVE_DATE": request.form.get("EFFECTIVE_DATE", "2025-01-01"),
            "PARTY_A": request.form.get("PARTY_A", "Party A"),
            "PARTY_B": request.form.get("PARTY_B", "Party B")
        }
        customization = {
            "JURISDICTION": request.form.get("JURISDICTION", "Default Jurisdiction"),
            "TONE": request.form.get("TONE", "formal")
        }
        clauses = {
            "Confidentiality Clause": request.form.get("CLAUSE_CONFIDENTIALITY", ""),
            "Non-Use Clause": request.form.get("CLAUSE_NON_USE", ""),
            "Term Clause": request.form.get("CLAUSE_TERM", "")
        }
        other_input = request.form.get("OTHER_CLAUSES", "")
        if other_input.strip():
            other_clauses = parse_clauses(other_input)

    elif contract_type == "service_agreement":
        details = {
            "EFFECTIVE_DATE": request.form.get("EFFECTIVE_DATE", "2025-01-01"),
            "SERVICE_PROVIDER": request.form.get("SERVICE_PROVIDER", "Service Provider"),
            "CLIENT": request.form.get("CLIENT", "Client")
        }
        customization = {
            "JURISDICTION": request.form.get("JURISDICTION", "Default Jurisdiction"),
            "TONE": request.form.get("TONE", "formal")
        }
        clauses = {
            "Scope of Services": request.form.get("CLAUSE_SCOPE_OF_SERVICES", ""),
            "Payment Terms": request.form.get("CLAUSE_PAYMENT_TERMS", ""),
            "Confidentiality Clause": request.form.get("CLAUSE_CONFIDENTIALITY", ""),
            "Non-Compete Clause": request.form.get("CLAUSE_NON_COMPETE", ""),
            "Intellectual Property Clause": request.form.get("CLAUSE_INTELLECTUAL_PROPERTY", ""),
            "Indemnification Clause": request.form.get("CLAUSE_INDEMNIFICATION", ""),
            "Termination Clause": request.form.get("CLAUSE_TERMINATION", ""),
            "Dispute Resolution Clause": request.form.get("CLAUSE_DISPUTE_RESOLUTION", "")
        }
        other_input = request.form.get("OTHER_CLAUSES", "")
        if other_input.strip():
            other_clauses = parse_clauses(other_input)

    elif contract_type == "employment_contract":
        details = {
            "EFFECTIVE_DATE": request.form.get("EFFECTIVE_DATE", "2025-01-01"),
            "EMPLOYER": request.form.get("EMPLOYER", "Employer"),
            "EMPLOYEE": request.form.get("EMPLOYEE", "Employee")
        }
        customization = {
            "JURISDICTION": request.form.get("JURISDICTION", "Default Jurisdiction"),
            "TONE": request.form.get("TONE", "formal")
        }
        clauses = {
            "Job Description": request.form.get("CLAUSE_JOB_DESCRIPTION", ""),
            "Compensation": request.form.get("CLAUSE_COMPENSATION", ""),
            "Benefits": request.form.get("CLAUSE_BENEFITS", ""),
            "Termination Clause": request.form.get("CLAUSE_TERMINATION", ""),
            "Confidentiality Clause": request.form.get("CLAUSE_CONFIDENTIALITY", ""),
            "Non-Compete Clause": request.form.get("CLAUSE_NON_COMPETE", "")
        }
        other_input = request.form.get("OTHER_CLAUSES", "")
        if other_input.strip():
            other_clauses = parse_clauses(other_input)

    elif contract_type == "rental_agreement":
        details = {
            "EFFECTIVE_DATE": request.form.get("EFFECTIVE_DATE", "2025-01-01"),
            "LANDLORD": request.form.get("LANDLORD", "Landlord"),
            "TENANT": request.form.get("TENANT", "Tenant")
        }
        customization = {
            "JURISDICTION": request.form.get("JURISDICTION", "Default Jurisdiction"),
            "TONE": request.form.get("TONE", "formal")
        }
        clauses = {
            "Premises Description": request.form.get("CLAUSE_PREMISES_DESCRIPTION", ""),
            "Rent Payment": request.form.get("CLAUSE_RENT_PAYMENT", ""),
            "Security Deposit": request.form.get("CLAUSE_SECURITY_DEPOSIT", ""),
            "Termination Clause": request.form.get("CLAUSE_TERMINATION", ""),
            "Maintenance Responsibility": request.form.get("CLAUSE_MAINTENANCE_RESPONSIBILITY", "")
        }
        other_input = request.form.get("OTHER_CLAUSES", "")
        if other_input.strip():
            other_clauses = parse_clauses(other_input)
    else:
        return "Unsupported contract type."

    contract_html = generate_contract(contract_type, details, clauses, other_clauses, customization)

    return render_template("result.html", contract=contract_html)


@app.route("/apply", methods=["POST"])
def apply_suggestions():
    """
    Extract the contract (including suggestions) from the request,
    then feed both the main contract and suggestions back to the model to merge them.
    """
    contract_html = request.form.get("contract_html", "No contract generated.")
    if contract_html == "No contract generated.":
        return render_template("result.html", contract=contract_html)
    
    main_body, suggestions_block = extract_suggestions_from_html(contract_html)
    
    if not suggestions_block.strip():
        final_version = main_body
    else:
        final_version = incorporate_suggestions_with_model(main_body, suggestions_block)
    
    return render_template("result.html", contract=final_version)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    """
    Allows iterative modification of the contract. The contract is loaded from localStorage
    and sent to the server with the user's request.
    """
    if request.method == "GET":
        return render_template("chat.html", contract="")
    else:
        contract_html = request.form.get("contract_html", "No contract generated.")
        user_message = request.form.get("user_message", "")
        if contract_html == "No contract generated.":
            return render_template("chat.html", contract=contract_html)

        updated_contract = chat_with_model(contract_html, user_message)
        return render_template("chat.html", contract=updated_contract)

@app.route("/export", methods=["POST"])
def export_docx():
    """
    Exports the contract as a DOCX file with preserved formatting.
    Uses html2docx to convert HTML to DOCX.
    """
    contract_html = request.form.get("contract_html", "No contract generated.")
    if contract_html == "No contract generated.":
        return "No contract generated."

    contract_no_suggestions = remove_suggestions_from_html(contract_html)
    docx_bytes = html2docx(contract_no_suggestions, title)
    
    docx_bytes.seek(0) 
    return send_file(docx_bytes, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document", as_attachment=True, download_name="contract.docx")


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    """
    Summarize & analyze an existing PDF or DOCX.
    """
    if request.method == "GET":
        return render_template("analysis.html")
    else:
        if "file" not in request.files:
            return "No file part."
        file = request.files["file"]
        if file.filename == "":
            return "No file selected."
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            if filename.lower().endswith(".pdf"):
                text_content = extract_text_from_pdf(filepath)
            else:
                text_content = extract_text_from_docx(filepath)

            analysis_result = summarize_and_analyze(text_content)
            return render_template("analysis_result.html", analysis=analysis_result)
        else:
            return "Unsupported file format."
        
import re

def html_to_text(html_content: str) -> str:
    """
    A simple approach to remove HTML tags, leaving plain text.
    For more robust solutions, consider 'BeautifulSoup' or 'html2text'.
    """
    text = re.sub(r'<[^>]*>', '', html_content)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


if __name__ == "__main__":
    app.run(debug=True)
