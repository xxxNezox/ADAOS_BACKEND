import models
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.exc import IntegrityError
from database import get_db
import asyncio

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import httpx
from database import get_db
from models import Users
from pydantic import BaseModel
from typing import Optional

rasa_router = APIRouter()

# Схема для запроса
class TextRequest(BaseModel):
    user_id: int
    message: str

# Схема для ответа
class TextResponse(BaseModel):
    type: str
    data: str


# Конфигурация RASA (вынесите в settings.py)
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"


@rasa_router.post('/text', response_model=TextResponse)
async def process_text(
    request: TextRequest, 
    db: AsyncSession = Depends(get_db)
):
    # 1. Проверка существования пользователя
    user = await db.get(Users, request.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # 2. Отправка запроса в Rasa
    async with httpx.AsyncClient() as client:
        try:
            rasa_response = await client.post(
                RASA_SERVER_URL,
                json={"message": f"{request.message}"}
            )
            rasa_response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail="The server is busy. Please try again later."
            )
    
    # 3. Обработка ответа от Rasa
    rasa_ans = rasa_response.json()
    if not rasa_ans or not isinstance(rasa_ans, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Неверный формат от РАСА"
        )
    print(rasa_ans)
    return TextResponse(type=rasa_ans['type'], data=rasa_ans['data'])


