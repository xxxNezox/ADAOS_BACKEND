# whisper.py (обновленная версия)
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Users
from Server_error_handler import ServerErrorHandler

whisper_router = APIRouter()
WHISPER_SERVER_URL = "http://localhost:8001/transcribe"

class TranscribeResponse(BaseModel):
    text: str

@whisper_router.post('/transcribe', response_model=TranscribeResponse)
async def transcribe_audio(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Проверка пользователя
    user = await db.get(Users, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Чтение файла
    try:
        audio_bytes = await file.read()
        ###printer('Проверка аудио', audio_bytes)
    finally:
        await file.close()

    # Отправка запроса в сервис транскрибации
    files_payload = {'file': (file.filename, audio_bytes, file.content_type)}
    ###printer('Файл пейлоад', files_payload)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                WHISPER_SERVER_URL,
                files=files_payload,
                timeout=30.0
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise await ServerErrorHandler.handle_http_error(e)
        except httpx.RequestError:
            raise await ServerErrorHandler.handle_request_error()
    
    # Обработка ответа
    try:
        transcription_data = response.json()
        ###printer('transcription_data', transcription_data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Неверный формат JSON от сервиса транскрибции."
        )
    
    await ServerErrorHandler.validate_service_response(
        transcription_data, 
        ["text"],
        "сервиса транскрибции"
    )
    
    print(f"Ответ от сервиса транскрибции: {transcription_data}") 
    return TranscribeResponse(text=transcription_data['text'])

def printer(name, status):
    print('='*40)
    print(f'Имя исполняемого куска: {name}')
    print(f'Ответ куска: {status}')
    print('========================================================================')