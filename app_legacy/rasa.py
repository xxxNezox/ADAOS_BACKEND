# rasa.py (обновленная версия)
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Users
from Server_error_handler import ServerErrorHandler

rasa_router = APIRouter()

class TextRequest(BaseModel):
    user_id: int
    message: str

class TextResponse(BaseModel):
    type: str
    data: str

RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"

@rasa_router.post('/text', response_model=TextResponse)
async def process_text(
    request: TextRequest, 
    db: AsyncSession = Depends(get_db)
):
    # Проверка пользователя
    user = await db.get(Users, request.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Отправка запроса в Rasa
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                RASA_SERVER_URL,
                json={"message": f"{request.message}"}
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
        rasa_data = response.json()
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
    return TextResponse(type=rasa_data['type'], data=rasa_data['data'])