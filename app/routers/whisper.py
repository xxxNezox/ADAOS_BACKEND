import httpx
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db 
from app.db.models import Users
from app.utils.server_error_handler import ServerErrorHandler

from app.core.config import settings

whisper_router = APIRouter()

class WhisperRasaResponse(BaseModel):
    type: str
    data: str
    file_name: str | None = None


@whisper_router.post('/transcribe', response_model=WhisperRasaResponse)
async def transcribe_audio(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Проверка пользователя
    if not await Users.user_exists(db, user_id):
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
                settings.WHISPER_SERVER_URL,
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
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.RASA_SERVER_URL,
                json={"message": f"{transcribed_text}"}
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise await ServerErrorHandler.handle_http_error(
                e,
                "The server is busy. Please try again later.",
                "message"  # Rasa может использовать другой ключ для ошибок
            )
        except httpx.RequestError:
            raise await ServerErrorHandler.handle_request_error()
    
    # Обработка ответа
    try:
        rasa_data = response.json()[0].get('custom')
        print(rasa_data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Неверный формат JSON от Rasa"
        )
    
    await ServerErrorHandler.validate_service_response(
        rasa_data, 
        ["type", "data"],
        "Rasa"
    )
    
    print(rasa_data)
    return WhisperRasaResponse(type=rasa_data['type'], data=rasa_data['data'], file_name=rasa_data.get('file_name'))