from os import times
from sqlalchemy.sql import text as sql_txt
from sqlalchemy.sql.schema import ForeignKey
from fastapi import FastAPI, Body, Request, UploadFile, File, Form
from fastapi.responses import ORJSONResponse, RedirectResponse
from typing import List, Optional, Text
from pydantic import BaseModel
import databases
import sqlalchemy
import re
import pandas as pd

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
document_part = sqlalchemy.Table(
    "document_part",
    metadata,
    sqlalchemy.Column("document_part_id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("document_part_path", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("document_part_filename", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("document_part_name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("doc_id", sqlalchemy.Integer, ForeignKey('document.document_id'))
)
bag_of_words = sqlalchemy.Table(
    "bag_of_words",
    metadata,
    sqlalchemy.Column("token_id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("token", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("frequency", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("document_occurence", sqlalchemy.Integer, nullable=False)
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

class BagOfWords(BaseModel):
    token_id: int
    token: str
    frequency: int
    document_occurence: int

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
    # return ({
    #     "message": "Unggah dokumen berhasil",
    #     "doc_id" : doc_id
    # })
    url= '/generate-data/document/'+str(doc_id)
    return RedirectResponse(url)


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

    # save every parts' pre processing results
    
    tokens = result["Hasil Pra-pengolahan Teks"]["Stemming"]
    for token in tokens:
        # save into .txt
        writes=""
        filename = "{0}_{1}.txt".format(re.sub(r'.pdf', '', doc[2]), token['title'])
        file_path = './chapter/'+filename
        
        with open(file_path, 'w') as file:
            writes = writes + (" ".join((token['content'])))
            file.write(writes)
        file.close()

        # insert document_parts into database
        insertQuery = document_part.insert().values(
            document_part_path = file_path,
            document_part_filename = filename,
            document_part_name = token['title'],
            doc_id = doc_id
        )
        await database.execute(insertQuery)

        print("Saving splitted document {0} success @ {1}".format(filename, ts.stamp()))

    # return ({
    #     "message" : "Pemrosesan Dokumen menjadi data siap olah berhasil",
    #     "result": result
    # })

    # redirect to vectorization route
    url= '/vectorize-data/document/'+str(doc_id)
    return RedirectResponse(url)

def generateDictioonary(keys, values):
    return {keys[i]: values[i] for i in range(len(keys))}


@app.post("/vectorize-data/document/{doc_id}")
async def VectorizeDocument(doc_id: int):
    query = document_part.select().where(document_part.c.doc_id == doc_id)
    docs = await database.fetch_all(query)
    # print(docs)
    query = bag_of_words.select()
    bow = pd.DataFrame(await database.fetch_all(query), columns=['id','token', 'freq', 'occur'])
    del bow['id']
    # print(bow)
    from Vectorizer import Vectorizer
    vectorizer = Vectorizer()
    tokens = []
    for row in docs:
        tokens.append(vectorizer.tfGenerator(row[1])) 
    
    # print(tokens[1])
    nbow = pd.concat(tokens, ignore_index=True)

    nbow = nbow.groupby(by=['token']).agg({'freq':'sum', 'occur':'sum'}).reset_index()
    # print(nbow)
    # df = pd.DataFrame([tokens, list(1 for i in range(len(tokens)))], columns=['token', 'freq'])
    with engine.connect() as con:
        for index, row in nbow.iterrows():
            query = '''INSERT OR REPLACE INTO bag_of_words (token, frequency, document_occurence)
            VALUES (:token, :frequency, :document_occurence) ON CONFLICT(token) DO
            UPDATE SET frequency = (SELECT frequency FROM bag_of_words WHERE token=excluded.token)+excluded.frequency,
            document_occurence = (select document_occurence from bag_of_words where token=excluded.token)+excluded.document_occurence;
            '''
            statement = sql_txt(query)
            values = { "token": row[0], "frequency": int(row[1]), "document_occurence": int(row[2]) }
            con.execute(statement, **values)
            # await con.execute(query)
            
    
    
    result = vectorizer.tfCounter(tokens, bow)
    
    # for i in range(len(docs)):
    #     filepath = (re.sub(r'.txt', '.csv', docs[i][1]))
    #     filepath = (re.sub(r'/chapter/', '/grouped-tf/', filepath))
    #     result[i].to_csv(filepath, index=False)


    
    
    # for term, freq in result['bow'].items():
    #     insertWordQuery = bag_of_words.insert().values(
    #         token=term,
    #         frequency=freq
    #     )
    #     insertWordQuery.on_duplicate_key_update(

    #     )
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
    # print(doc_id)
