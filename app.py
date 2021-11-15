from fastapi import FastAPI, Body, Request, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
import shutil
from PyPDF2 import PdfFileReader

app = FastAPI()

class DocumentParts(BaseModel):
    url:str

class Document(BaseModel):
    url: str
    name: str
    parts: List[DocumentParts] = []

# class Item(BaseModel):
#     title: str
#     writers: str
#     year: int
#     email: str
#     type: str
#     sinta_id: int
#     document: Document



@app.get("/")
def Home():
    return {"Data": "API running properly"}

# @app.post("/upload")
# def UploadData(title: Item):
#     return {}

# @app.post("/post-data")
# async def UploadFile(file: UploadFile = File(...)):
#     with open('text.pdf', 'wb') as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     return {"file_name": file.filename}

@app.post("/submit-form")
async def FormHandler(
    prop_title: str = Form(...), prop_writers: str = Form(...),
    prop_email: str = Form(...), prop_year: int = Form(...),
    prop_type: str = Form(...), prop_sintaid: int = Form(...),
    document: UploadFile = File(...)  ):
    # with open("./public/upload/"+document.filename, 'wb') as buffer:
    #     shutil.copyfileobj(document.file, buffer)
    # add parser pdf
    #  open the file
    # target_file = "./public/upload/PENELITIAN_6064836_5 (1).pdf"
    print(document.file)
    # pdf = PdfFileReader(open(document.file, 'rb', encoding='utf-8'))

    # get num of pages
    num_pages = pdf.getNumPages()
    print(num_pages)

    # extract text using loop
    text = ""
    for i in range(num_pages):
        page = pdf.getPage(i)
        text = text + " " + page.extractText()
    
    print(len(text))
    # print(prop_title, document.filename)
