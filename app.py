from os import times

from sqlalchemy.sql.schema import ForeignKey

from fastapi import FastAPI, Body, Request, UploadFile, File, Form
from fastapi.responses import ORJSONResponse, RedirectResponse
from typing import List, Optional, Text
from pydantic import BaseModel
import databases
import sqlalchemy

DATABASE_URL = "sqlite:///./docs_similarity_cbr.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
proposal = sqlalchemy.Table(
    "proposal",
    metadata,
    sqlalchemy.Column("proposal_id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("proposal_title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("proposal_writer", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("proposal_year", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("proposal_email", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("proposal_type", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("proposal_sintaid", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("proposal_doc_id", sqlalchemy.Integer, ForeignKey('document.document_id'))
)
document = sqlalchemy.Table(
    "document",
    metadata,
    sqlalchemy.Column("document_id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("document_path", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("document_filename", sqlalchemy.String, nullable=False)
)
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

app = FastAPI(default_response_class=ORJSONResponse)

class Document(BaseModel):
    document_id: int
    document_path: str
    document_filename: str
    
class DocumentPart(BaseModel):
    document_part_id: int
    document_part_path: str
    document_part_filename: str
    document_part_name: str
    doc_id: Document

class Proposal(BaseModel):
    proposal_id: int
    proposal_title: str
    proposal_writer: str
    proposal_year: int
    proposal_email: str
    proposal_type: str
    proposal_sintaid: int
    proposal_doc_id: int


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
def Home():
    return {"message": "API running properly"}


@app.get("/proposal", response_model=List[Proposal])
async def ReadProposals():
    query = proposal.select()
    return await database.fetch_all(query)


@app.post("/submit-form", response_class=RedirectResponse, status_code=307)
async def FormHandler(
    prop_title: str = Form(...), prop_writers: str = Form(...),
    prop_email: str = Form(...), prop_year: int = Form(...),
    prop_type: str = Form(...), prop_sintaid: int = Form(...),
    prop_doc: UploadFile = File(...)  ):
    import uuid
    import aiofiles
    from TimeStamp import TimeStamp as ts

    # upload file
    fname = (uuid.uuid4().hex)
    out_file = './public/upload/'+fname+'.pdf'
    async with aiofiles.open(out_file, 'wb') as output:
        content = await prop_doc.read()
        await output.write(content)

    print("Upload file success@", ts.stamp())

    # upload docs in database
    insertDocQuery = document.insert().values(
        document_path=out_file,
        document_filename=fname+'.pdf'
    )
    doc_id = await database.execute(insertDocQuery)
    insertPropQuery = proposal.insert().values(
        proposal_title=prop_title,
        proposal_writer=prop_writers,
        proposal_year=prop_year,
        proposal_email=prop_email,
        proposal_type=prop_type,
        proposal_sintaid = prop_sintaid,
        proposal_doc_id=doc_id
    )
    await database.execute(insertPropQuery)
    
    # redirect to extraction route
    return ({
        "message": "Unggah dokumen berhasil",
        "doc_id" : doc_id
    })
    # url= '/generate-data/document/'+str(doc_id)
    # return RedirectResponse(url)


# @app.post("/generate-data/document/{doc_id}", response_model=Document)
@app.post("/generate-data/document/{doc_id}")
async def DataGeneration(doc_id: int):
    query = document.select().where(document.c.document_id == doc_id)
    doc = await database.fetch_one(query)
    title_query = proposal.select().where(proposal.c.proposal_doc_id == doc_id)
    prop = await database.fetch_one(title_query)
    print(prop[1])
    # extracting file
    import fitz
    import aiofiles
    from TimeStamp import TimeStamp as ts

    docs = fitz.open(doc[1])
    text = ""
    for page in docs:
        text = text + page.get_text("text") + "\n"  
    
    print("Extracting document {0} success @ {1}\n{2} characters extracted.\n".format(doc[2], ts.stamp(), len(text)))
    # preprocessing text
    from DataProcessing import DataProcessing

    DataProcessor = DataProcessing()
    splitted_doc = DataProcessor.splitDocument(text)
    splitted_doc.insert(0,  {
        "chapter": "JUDUL",
        "text": prop[1]
    })

    result = DataProcessor.preprocessingText(splitted_doc)
    return ({
        "message" : "Pemrosesan Dokumen menjadi data siap olah berhasil",
        "result": result
    })

    # redirect to vectorization route
    # url= '/vectorize-data/document/'+str(doc_id)
    # return RedirectResponse(url)

    
    

@app.post("/vectorize-data/document/{doc_id}")
async def VectorizeDocument(doc_id: int):
    # from Vectorizer import Vectorizer
    # vectorizer = Vectorizer()
    # tfs = vectorizer.tfCounter(result["Hasil Pra-pengolahan Teks"]["Stemming"])
    
    # i=0
    # for dictionary in tfs:
    #     with open('./chapter/'+fname+'_'+splitted_doc[i]["chapter"]+'.csv', 'w') as f:
    #         writes="term, frequency\n"
    #         for term, freq in dictionary.items():
    #             writes= writes + ("\"{0}\", {1}\n".format(term, freq))
    #         f.write(writes)
    #     f.close()
    #     i += 1
        
    
    # query all part of document ./chapter
        # SELECT url_path as path, document_id as doc_id from DocumentParts
        

    # response = {
    #     "message": "success",
    #     "data": result
    # }
    # return [response]
    print(doc_id)
