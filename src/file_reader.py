"""
file_reader.py
Extracts raw text from resume/job description files.
Supports: PDF, DOCX, and plain TXT.
"""

import PyPDF2 
import docx
import re


def read_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def clean_pdf_text(text):
    """
    Fixes common PDF extraction issues where words from different
    lines/columns get merged without a space.
    """
    # Replace newlines that are NOT after sentence punctuation with a space
    text = re.sub(r"(?<![.!?:])\n", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def read_docx(file_path):
    """Extract text from a DOCX file."""
    doc = docx.Document(file_path)
    text = "\n".join(para.text for para in doc.paragraphs)
    return text.strip()


def read_txt(file_path):
    """Extract text from a plain TXT file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def extract_text(file_path):
    """
    Detects file type by extension and extracts text accordingly.
    Works for both PDF, DOCX and TXT files.
    """
    if file_path.lower().endswith(".pdf"):
        raw = read_pdf(file_path)
        return clean_pdf_text(raw)
    elif file_path.lower().endswith(".docx"):
        return read_docx(file_path)
    elif file_path.lower().endswith(".txt"):
        return read_txt(file_path)
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")


# Quick manual test — run this file directly to check it works
if __name__ == "__main__":
    sample_path = "data/Tanmayee_Valluru_Resume.pdf"  # change this to your test file
    text = extract_text(sample_path)
    print("Extracted text (first 500 chars):\n")
    print(text[:500])