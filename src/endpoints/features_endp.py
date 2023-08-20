from fastapi import APIRouter, File, UploadFile
from src.models.llm import get_non_complaint_logs
from datetime import datetime
import csv
import PyPDF2
import os

router = APIRouter(
    prefix="",
    tags=["Application"],
    responses={404: {"description": "Not found"}},
)

def parse_csv(file):
    reader = csv.reader(file)
    first_column = [row[0] for row in reader]
    return '\n'.join(first_column)

def parse_txt(file):
    logs = file.read()
    return logs

def parse_pdf(file):
    # Create a PDF object
    pdf = PyPDF2.PdfFileReader(file)
    
    # Get the number of pages
    num_pages = pdf.numPages
    
    # Initialize a variable to store the text
    logs = ""
    
    # Loop through each page and extract the text
    for i in range(num_pages):
        page = pdf.getPage(i)
        logs += page.extractText()
    
    return logs

def create_ruleset(rules: str):
    # Get the current time and format it as a string
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M-%S.txt")
    
    # Create the /data directory if it doesn't exist
    os.makedirs("./data", exist_ok=True)

    # Create the file and write the rules to it
    with open(f"./data/{filename}", "w") as file:
        file.write(rules)


#Function that accepts log file in format CSV/TEXT/PDF and returns the predicted output
@router.post("/validate-logs")
async def validate_logs(file: UploadFile = File(...)):
    try:
        file_type = file.content_type
        logs = ""
        if file_type == "text/csv":
            logs = parse_csv(file.file)
        elif file_type == "text/plain":
            logs = parse_txt(file.file)
        elif file_type == "application/pdf":
            logs = parse_pdf(file.file)
        else:
            return {"ERROR":"FILE TYPE NOT SUPPORTED"}
        
        return get_non_complaint_logs(logs)
    except Exception as e:
        print(e)
        return {"ERROR":"SOME ERROR OCCURRED"}


@router.post("/upload-ruleset")
async def validate_logs(file: UploadFile = File(...)):
    try:
        file_type = file.content_type
        rules = ""
        
        if file_type == "text/plain":
            rules = parse_txt(file.file)
        elif file_type == "application/pdf":
            rules = parse_pdf(file.file)
        else:
            return {"ERROR":"FILE TYPE NOT SUPPORTED"}
        
        create_ruleset(rules)
        return {"SUCCESS":"RULESET SAVED"}
    except Exception as e:
        print(e)
        return {"ERROR":"SOME ERROR OCCURRED"}

