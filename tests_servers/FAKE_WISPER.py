from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# Модель для входных данных (если audio передается как base64 строка)
class AudioInput(BaseModel):
    audio: str  # base64 encoded audio file

# Модель для ответа
class AudioResponse(BaseModel):
    text: str

@app.post("/asdasd")
async def process_audio(audio_input: AudioInput):
    """
    Эндпоинт для обработки аудио.
    Принимает JSON с полем 'audio' (base64 строка).
    Возвращает JSON с текстовым ответом.
    """
    # Здесь можно добавить логику обработки аудио, если нужно
    # Например: print(f"Received audio with length: {len(audio_input.audio)}")
    
    return JSONResponse(content={"text": "Аудио обработано"})

# Альтернативная версия, если audio передается как файл
@app.post("/transcribe")
async def upload_audio(file: UploadFile = File(...)):
    """
    Эндпоинт для загрузки аудиофайла.
    Принимает файл в multipart/form-data.
    Возвращает JSON с текстовым ответом.
    """
    # Читаем файл (хотя в данном примере мы его не обрабатываем)
    contents = await file.read()
    print(f"Received audio file: {file.filename}, size: {len(contents)} bytes")
    
    return {"text": "Аудио файл получен и обработан"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
