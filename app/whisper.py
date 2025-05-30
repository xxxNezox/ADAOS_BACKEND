import httpx
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Users


whisper_router = APIRouter()

# Конфигурация Whisper (рекомендуется вынести в settings.py или переменные окружения)
WHISPER_SERVER_URL = "http://localhost:8001/transcribe"


# Схема для ответа от сервиса транскрибции
class TranscribeResponse(BaseModel):
    text: str


@whisper_router.post('/transcribe', response_model=TranscribeResponse)
async def transcribe_audio(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. Проверка существования пользователя
    user = await db.get(Users, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # 2. Чтение файла и отправка запроса в сервис транскрибции
    try:
        audio_bytes = await file.read()
        printer('Проверка аудио', audio_bytes)
    finally:
        await file.close() # Важно закрыть файл после чтения

    files_payload = {'file': (file.filename, audio_bytes, file.content_type)}
    printer('Файл пейлоад', files_payload)
    async with httpx.AsyncClient() as client:
        try:
            whisper_service_response = await client.post(
                WHISPER_SERVER_URL,
                files=files_payload,
                timeout=30.0 # Установка таймаута, например, 60 секунд, для длительных операций транскрибции
            )
            whisper_service_response.raise_for_status()  # Проверка на HTTP ошибки (4xx, 5xx)
        except httpx.HTTPStatusError as e:
            # Ошибка, возвращенная самим сервисом транскрибции (например, неверный формат файла, внутренняя ошибка сервиса)
            # В соответствии со стилем примера, используем общее сообщение, сохраняя оригинальный status_code.
            detail_message = "Сервис транскрибции не смог обработать ваш запрос. Пожалуйста, попробуйте позже."
            try:
                # Попытка извлечь более конкретное сообщение об ошибке, если сервис его предоставил
                error_data = e.response.json()
                if "error" in error_data:
                    detail_message = error_data["error"]
            except Exception:
                # Если не удалось получить детали, используем стандартное сообщение
                pass
            
            raise HTTPException(
                status_code=e.response.status_code,
                detail=detail_message
            )
        except httpx.RequestError:
            # Ошибка соединения с сервисом транскрибции (например, сервис недоступен, таймаут сети)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервис транскрибции недоступен. Пожалуйста, попробуйте позже."
            )
    
    # 3. Обработка ответа от сервиса транскрибции
    try:
        transcription_data = whisper_service_response.json()
        printer('transcription_data', transcription_data)
    except ValueError: # Если ответ не является валидным JSON
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Неверный формат JSON от сервиса транскрибции."
        )
    
    # Проверка структуры ответа, аналогично примеру с Rasa
    if not transcription_data or not isinstance(transcription_data, dict) or "text" not in transcription_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Неверный или неполный формат ответа от сервиса транскрибции."
        )
    
    # Вывод ответа от сервиса транскрибции в консоль, как в примере
    print(f"Ответ от сервиса транскрибции: {transcription_data}") 
    
    return TranscribeResponse(text=transcription_data['text'])


def printer(name, status):
    print('='*40)
    print(f'Имя исполняемого куска: {name}')
    print(f'Ответ куска: {status}')
    print('========================================================================')
    