from os import times
from fastapi import FastAPI, Body, Request, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel

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
    return {"message": "API running properly"}

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
    import uuid
    import fitz
    import aiofiles
    from TimeStamp import TimeStamp as ts

    # upload file
    out_file = './public/upload/'+(uuid.uuid4().hex)+'.pdf'
    async with aiofiles.open(out_file, 'wb') as output:
        content = await document.read()
        await output.write(content)

    print("Upload file success@", ts.stamp())

    # extracting file
    doc = fitz.open(out_file)
    text = ""
    for page in doc:
        text = text + page.get_text("text") + "\n"  
    
    print("Extracting document",document.filename, " success @", ts.stamp())
    print(len(text))
    # preprocessing text
    from DataProcessing import DataProcessing

    DataProcessor = DataProcessing()
    splitted_doc = DataProcessor.splitDocument(text)
    splitted_doc.insert(0,  {
        "chapter": "JUDUL",
        "text": prop_title
    })

    result = DataProcessor.preprocessingText(splitted_doc)


    response = {
        "message": "success",
        "status": 200,
        "data": result
    }
    return response

