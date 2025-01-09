from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import shutil
import os
from func.speech_recog.speech_recog import speech_recog
from func.message_response.response import load_model, create_text
# from func.voice_vox.voice_vox import create_voice
from func.sbt.sbt import sbt2_voice
from func.qr.qr_read import decode_qr_code
from func.qr.qr_gen import qr_generate
from func.db.add_db import pull_user
import sqlite3 as sql
from dotenv import load_dotenv
load_dotenv()
API_HOME = os.getenv("API_HOME")
messages = [
    {'role': 'assistant', 'content': "何でも話してね"}
]


app = FastAPI()

# dbname = 'memory.db'
# conn = sql.connect(dbname)

# cur = conn.cursor()
# table1 = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="persons"').fetchone()
# if table1 is None :        
#     cur.execute(
#         'CREATE TABLE persons(id INTEGER PRIMARY KEY, name STRING)'
#     )
    
# table2 = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="messages"').fetchone()
# if table2 is None:
#     cur.execute(
#         'CREATE TABLE messages(id INTEGER PRIMARY KEY AUTOINCREMENT, usr_id INTEGER, message STRING)'
#     )

class Item(BaseModel):
    message: str
    id: int

class GenerateBody(BaseModel):
    user_message: str
    user_id: int

    

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
    print(f"user_message: {item.user_message}, user_id: {item.user_id}")
    try:
        user_id = int(item.user_id)
        response = create_text(messages, item.user_message, user_id)
        print(response)
        return {"response": response}
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid user_id format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/tts", response_class=FileResponse)
def tts(text: str, chara_id: int = 0):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty.")
    try:
        path = sbt2_voice(text=text, chara_id=chara_id)
        return path
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Error during TTS processing: {str(e)}")

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
    UserID = data
    UserName = pull_user(UserID)
    print(f"UserName: {UserName}")
    return {"response": UserName, "user_id": UserID}

@app.post("/qr_gen/{user_id}")
def qr_gen(user_id: int, name: str = Query(..., description="User's name")):
    qr_generate(user_id, name)
    print(name)
    qr_path = "./qr.png"
    if os.path.exists(qr_path):
        return FileResponse(qr_path, media_type="image/png", filename="qr_code.png")
    else:
        raise HTTPException(status_code=500, detail="QR code generation failed")
    
if __name__ == "__main__":
    import uvicorn
    from func.sbt.sbt import load_models
    load_models()
    uvicorn.run(app,host=API_HOME, port=8000)
