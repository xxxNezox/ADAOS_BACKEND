# ...existing code...
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Users
from Server_error_handler import ServerErrorHandler

whisper_router = APIRouter()
WHISPER_SERVER_URL = "http://localhost:8001/transcribe"

class WhisperRasaResponse(BaseModel):
    type: str
    data: str

@whisper_router.post('/transcribe', response_model=WhisperRasaResponse)
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
    finally:
        await file.close()

    # Отправка запроса в сервис транскрибации
    files_payload = {'file': (file.filename, audio_bytes, file.content_type)}
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
    
    # Обработка ответа Whisper
    try:
        transcription_data = response.json()
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
    transcribed_text = transcription_data['text']

    # Отправка текста в Rasa
    RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook" # пофиксить на env + config
    rasa_payload = {"message": transcribed_text}
    async with httpx.AsyncClient() as client:
        try:
            rasa_response = await client.post(
                RASA_SERVER_URL,
                json=rasa_payload
            )
            rasa_response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise await ServerErrorHandler.handle_http_error(
                e,
                "The server is busy. Please try again later.",
                "message"
            )
        except httpx.RequestError:
            raise await ServerErrorHandler.handle_request_error()
    
    # Обработка ответа Rasa | сделать общие методы с rasa.py
    try:
        rasa_data = rasa_response.json()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Неверный формат JSON от Rasa"
        )

    # Если Rasa возвращает список сообщений, берём первое | - какаято хуйня от гпт
    if isinstance(rasa_data, list) and rasa_data:
        rasa_data = rasa_data[0]
    await ServerErrorHandler.validate_service_response(
        rasa_data, 
        ["data"],  # Обычно Rasa возвращает "text"
        "Rasa"
    )
    return WhisperRasaResponse(type=rasa_data.get("type", "text"), data=rasa_data["data"])
