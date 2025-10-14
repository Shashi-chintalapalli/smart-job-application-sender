import pdfplumber
from docx import Document
from langchain_community.document_loaders import TextLoader
import tempfile
import os
import re

def parse_file(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    if ext == ".pdf":
        return parse_pdf(tmp_path)
    elif ext == ".docx":
        return parse_docx(tmp_path)
    elif ext == ".txt":
        return parse_txt(tmp_path)
    else:
        raise ValueError("Unsupported file type")

def parse_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def parse_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs]).strip()

def parse_txt(file_path):
    loader = TextLoader(file_path)
    doc = loader.load()
    return doc.page_content.strip()

def extract_hr_email_and_company(text):
    match = re.search(r'[\w\.-]+@([\w\.-]+)', text)
    if match:
        email = match.group(0)
        domain = match.group(1)
        company = domain.split('.')[0].replace("-", " ").title()
        return email, company
    return None, None
