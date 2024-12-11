from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import FileResponse

from pydantic import BaseModel

import shutil
import os

from func.speech_recog.speech_recog import speech_recog
from func.message_response.response import load_model, create_text
# from func.voice_vox.voice_vox import create_voice
from func.sbt.sbt import sbt2_voice
from func.qr.qr_read import decode_qr_code
from func.qr.qr_gen import qr_generate

import sqlite3 as sql

messages = [
    {'role': 'assistant', 'content': "何でも話してね"}
]

app = FastAPI()

dbname = 'memory.db'
conn = sql.connect(dbname)

cur = conn.cursor()
table1 = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="persons"').fetchone()
if table1 is None :        
    cur.execute(
        'CREATE TABLE persons(id INTEGER PRIMARY KEY, name STRING)'
    )
    
table2 = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="messages"').fetchone()
if table2 is None:
    cur.execute(
        'CREATE TABLE messages(id INTEGER PRIMARY KEY AUTOINCREMENT, usr_id INTEGER, message STRING)'
    )

class Item(BaseModel):
    message: str
    id: int

class GenerateBody(BaseModel):
    user_message: str
    

@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/message")
def update_item(item: Item):
    print(item.message, item.id)
    
    return {"response": f"{item.message}. hello you!!"}

@app.post("/sp_rec")
def speech_rec(file: UploadFile = File(...)):
    print(file.filename)
    # 一旦ファイルをほぞんする
    filename = "speechRec_.wav"
    path = f'./tmp/{filename}'
    os.makedirs("./tmp", exist_ok=True)
    with open(path,"wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = speech_recog(wav_path=path)
    
    # create_voice(response)
    
    return {"response": result}

@app.post("/generate")
def generate(item: GenerateBody):
    response = create_text(messages, item.user_message)
    print(response)
    return {"response": response}

@app.get("/tts", response_class=FileResponse)
def tts(text: str, chara_id :int = 0):
    print(text)
    path = sbt2_voice(text=text, chara_id=chara_id)
    return path

# @app.get("/tts", response_class=FileResponse)
# def tts(text: str, speaker_id: int):
#     print(text, speaker_id)
#     path = create_voice(text=text)
#     return path

@app.post("/qr_read")
def qr_read(file: UploadFile = File(...)):
    print(file.filename)
    file_path = f'./tmp/{file.filename}'
    os.makedirs("./tmp", exist_ok=True)
    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    data = decode_qr_code(file_path)
    
    return {"response": data}

@app.post("/qr_gen/{user_id}")
def qr_gen(user_id: int, name: str = Query(..., description="User's name")):
    qr_generate(user_id)
    print(name)
    qr_path = "./qr.png"
    if os.path.exists(qr_path):
        return FileResponse(qr_path, media_type="image/png", filename="qr_code.png")
    else:
        raise HTTPException(status_code=500, detail="QR code generation failed")
    
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app,host="150.59.20.116", port=8000)
