"""
resume.py
Handles resume file validation and text extraction (PDF / DOCX / TXT).
"""
 
import docx2txt
from pypdf import PdfReader
 
 
def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
 
 
def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[1].lower()
    if ext == "pdf":
        return _extract_pdf(filepath)
    elif ext == "docx":
        return docx2txt.process(filepath) or ""
    elif ext == "txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    raise ValueError(f"Unsupported file type: {ext}")
 
 
def _extract_pdf(filepath):
    reader = PdfReader(filepath)
    pages_text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages_text.append(page_text)
    return "\n".join(pages_text)
 
