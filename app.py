from logging import raiseExceptions
from os import times
from sqlalchemy.sql import text as sql_txt
from sqlalchemy.sql.schema import ForeignKey
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import ORJSONResponse, JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Text
from pydantic import BaseModel
import databases
import sqlalchemy
import re
import pandas as pd
import json

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
    sqlalchemy.Column("doc_id", sqlalchemy.Integer, ForeignKey('document.document_id')),
    sqlalchemy.Column("document_part_tokens", sqlalchemy.Text, nullable=False)
)
bag_of_words = sqlalchemy.Table(
    "bag_of_words",
    metadata,
    sqlalchemy.Column("token", sqlalchemy.String, primary_key=True, nullable=False),
    sqlalchemy.Column("frequency", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("document_occurence", sqlalchemy.Integer, nullable=False)
)
case_bases = sqlalchemy.Table(
    "case_bases",
    metadata,
    sqlalchemy.Column("record_id", sqlalchemy.String, primary_key=True, nullable=False),
    sqlalchemy.Column("doc_id", sqlalchemy.Integer, ForeignKey('document.document_id')),
    sqlalchemy.Column("doc_part_name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("sim_doc_id", sqlalchemy.Integer, ForeignKey('document.document_id')),
    sqlalchemy.Column("sim_doc_part_name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("cos_sim_value", sqlalchemy.REAL, nullable=False),
    sqlalchemy.Column("config_used", sqlalchemy.String, nullable=False),

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
    document_part_tokens: str

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
    token: str
    frequency: int
    document_occurence: int

class CaseBases(BaseModel):
    record_id: int
    doc_id: int
    doc_part_name: str
    sim_doc_id: int
    sim_doc_part_name: str
    cos_sim_value: float
    config_used: str

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
def Home():
    return {"detail": "API running properly"}


@app.get("/proposal", response_model=List[Proposal])
async def ReadProposals():
    query = proposal.select()
    proposals =  await database.fetch_all(query)
    if not proposals:
        raise HTTPException(status_code=404, detail="Belum ada data ajuan di dalam basis data")
    return jsonable_encoder(proposals)


@app.post("/submit-form", response_class=RedirectResponse, status_code=307)
async def FormHandler(
    prop_title: str = Form(...), prop_writers: str = Form(...),
    prop_email: str = Form(...), prop_year: int = Form(...),
    prop_type: str = Form(...), prop_sintaid: int = Form(...),
    prop_doc: UploadFile = File(...)  ):
    try:
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
        
        return jsonable_encoder({
            "detail": "Unggah dokumen berhasil",
            "doc_id" : doc_id
        })
        # url= '/generate-data/document/'+str(doc_id)
        # return RedirectResponse(url)
    except OSError:
        raise HTTPException(status_code=500, detail="Gagal mengunggah berkas ke dalam server")


# @app.post("/generate-data/document/{doc_id}", response_model=Document)
@app.post("/generate-data/document/{doc_id}")
async def DataGeneration(doc_id: int):
    query = document.select().where(document.c.document_id == doc_id)
    doc = await database.fetch_one(query)
    title_query = proposal.select().where(proposal.c.proposal_doc_id == doc_id)
    prop = await database.fetch_one(title_query)
    if len(doc) == 0 and len(prop)==0:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    else:        
        # print(prop[1])
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
            token_name = "{0}_{1}.csv".format(re.sub(r'.pdf', '', doc[2]), token['title'])
            file_path = './chapter/'+filename
            token_path = './grouped-tf/'+token_name
            
            with open(file_path, 'w') as file:
                writes = writes + (" ".join((token['content'])))
                file.write(writes)
            file.close()

            # insert document_parts into database
            insertQuery = document_part.insert().values(
                document_part_path = file_path,
                document_part_filename = filename,
                document_part_name = token['title'],
                document_part_tokens = token_path,
                doc_id = doc_id
            )
            await database.execute(insertQuery)

            print("Saving splitted document {0} success @ {1}".format(filename, ts.stamp()))

        return jsonable_encoder({
            "detail" : "Pemrosesan Dokumen menjadi data siap olah berhasil",
            "result": result
        })

        # redirect to vectorization route
        # url= '/similarity-cbr/document/'+str(doc_id)
        # return RedirectResponse(url)


@app.post("/similarity-cbr/document/{doc_id}")
async def SimiarityCbr(doc_id: int, config: str = Form(...)):
    from Vectorizer import Vectorizer
    vectorizer = Vectorizer()
    # work flow 
    # retrieve bow and number of all document parts
    query = bag_of_words.select()
    bow = pd.DataFrame(await database.fetch_all(query), columns=['token', 'frequency', 'occur'], index=None)
    del bow['frequency']

    # retrieve new document
    query = document_part.select().where(document_part.c.doc_id == doc_id)
    docs = await database.fetch_all(query)

    if len(docs) == 0 :
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    else:
        # generate tokens of searched doc
        token_paths = list(row[1] for row in docs)
        output_paths = list(row[5] for row in docs)
        
        tokens = vectorizer.tfGenerator(token_paths)

        # saving token into csv for faster computation
        for i in range (len(tokens)):
            tokens[i].to_csv(output_paths[i], index=None)

        # concating all tokens
        nbow = pd.concat(tokens, ignore_index=True)
        # grouping every terms => insert to database
        nbow = nbow.groupby(by=['token']).agg({'frequency':'sum', 'occur':'sum'}).reset_index()
        # insert every term to database => bag_of_words
        with engine.connect() as con:
            query = '''INSERT OR REPLACE INTO bag_of_words (token, frequency, document_occurence)
                VALUES (:token, :frequency, :document_occurence) ON CONFLICT(token) DO
                UPDATE SET frequency = (SELECT frequency FROM bag_of_words WHERE token=excluded.token)+excluded.frequency,
                document_occurence = (select document_occurence from bag_of_words where token=excluded.token)+excluded.document_occurence;
                '''
            statement = sql_txt(query)
            for index, row in nbow.iterrows():
                values = { "token": row[0], "frequency": int(row[1]), "document_occurence": int(row[2]) }
                con.execute(statement, **values)

        # retrieve base case document
        query = document_part.select()
        n = len(await database.fetch_all(query))

        # with bow, count idf of every bow
        idf_dict = vectorizer.IdfGenerator(bow, n, config)
        
        # weight used for retrieval (searched doc)
        weights_doc = vectorizer.tfIdf(tokens, idf_dict)
        id_doc = list(row[0] for row in docs)
        dict_doc = {}
        for i in range(len(docs)):
            dict_doc[id_doc[i]] = weights_doc[i]

        # retrieve all document except new document for searching
        query = document_part.select().where(document_part.c.doc_id != doc_id)
        base_docs = await database.fetch_all(query)   
        if len(base_docs) == 0:
            raise HTTPException(status_code=404, detail="Dokumen basis kasus tidak ditemukan")
        else:
            # use path of every document
            base_tokens = vectorizer.tfGenerator(list(row[5] for row in base_docs)) # list of base document's path
            # generate weight of all base docs
            weights_base = vectorizer.tfIdf(base_tokens, idf_dict)
            id_base = list(row[0] for row in base_docs)
            dict_base = {}
            for i in range(len(base_docs)):
                dict_base[id_base[i]] = weights_base[i]
            # do similarity detection using CBR
            from SimDocs import SimDocs
            docsim = SimDocs()

            # design result => dataframe (doc_part_name, sim_part_name, cos_sim)
            result = docsim.CbrDocsSearch(dict_doc, dict_base)
            reused = []
            for df in result['reused']:
                frame = pd.DataFrame(df)
                reused.append(json.loads(frame.to_json(orient='index')))
            return jsonable_encoder({
                "retrieved": json.loads(pd.DataFrame(result['retrieved']).to_json(orient='index')),
                "reused": reused,
                "final_result": json.loads(pd.DataFrame(result['result']).to_json(orient='index'))
            })

