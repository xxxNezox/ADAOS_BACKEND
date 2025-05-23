from . import schemas, models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.exc import IntegrityError
from .database import get_db

rasa_router = APIRouter()

'''
Базовый текстовый запрос от юзера

юзер -> сервер -> раса -> сервер -> юзер

Формат запроса
json
{
    user_id: 123123123
    user_text: Пирет! какая погода на улице
}

Возвращает раса
json
{
    user_text: text
    Tag: code/text
}
'''

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import httpx
from .database import get_db
from .models import Users
from pydantic import BaseModel
from typing import Optional

# Схема для запроса
class TextRequest(BaseModel):
    user_id: int
    text: str

# Схема для ответа
class RasaResponse(BaseModel):
    recipient_id: str
    text: Optional[str] = None
    custom: Optional[dict] = None

# Конфигурация RASA (вынесите в settings.py)
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"

@rasa_router.post('/text', response_model=RasaResponse)
async def process_text(
    request: TextRequest,
    db: Session = Depends(get_db)
):
    """
    Обработка текстового сообщения пользователя с перенаправлением в RASA
    
    - Проверяет существование пользователя
    - Отправляет сообщение в RASA
    - Возвращает ответ от RASA
    """
    
    # Проверка существования пользователя
    user = db.query(Users).filter(Users.user_id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Подготовка данных для RASA
    rasa_payload = {
        "sender": str(request.user_id),
        "message": request.text
    }

    try:
        # Отправка запроса в RASA
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RASA_SERVER_URL,
                json=rasa_payload,
                timeout=10.0
            )
            response.raise_for_status()
            
            rasa_data = response.json()
            
            # Обработка ответа RASA (пример для простого текстового ответа)
            if rasa_data:
                return RasaResponse(
                    recipient_id=str(request.user_id),
                    text=rasa_data[0].get("text"),
                    custom=rasa_data[0].get("custom")
                )
            
            return RasaResponse(recipient_id=str(request.user_id))

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RASA service error: {str(e)}"
        )