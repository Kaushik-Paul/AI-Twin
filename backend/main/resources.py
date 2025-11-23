import os
from pypdf import PdfReader
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.normpath(os.path.join(base_dir, "..", "data"))

# Read Resume PDF
try:
    resume_path = os.path.join(data_dir, "resume.pdf")
    reader = PdfReader(resume_path)
    resume = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            resume += text
except FileNotFoundError:
    resume = "Resume not available"

# Read Linkedin PDF
try:
    linkedin_path = os.path.join(data_dir, "linkedin.pdf")
    reader = PdfReader(linkedin_path)
    linkedin = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            linkedin += text
except FileNotFoundError:
    linkedin = "linkedin profile not available"

# Read other data files
with open(os.path.join(data_dir, "summary.txt"), "r", encoding="utf-8") as f:
    summary = f.read()

with open(os.path.join(data_dir, "style.txt"), "r", encoding="utf-8") as f:
    style = f.read()

with open(os.path.join(data_dir, "facts.json"), "r", encoding="utf-8") as f:
    facts = json.load(f)