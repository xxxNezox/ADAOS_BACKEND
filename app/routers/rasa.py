import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Users
from app.utils.server_error_handler import ServerErrorHandler

from app.core.config import settings

rasa_router = APIRouter()

class TextRequest(BaseModel):
    user_id: int
    message: str

class TextResponse(BaseModel):
    type: str
    data: str
    file_name: str | None = None

@rasa_router.post('/text', response_model=TextResponse)
async def process_text(
    request: TextRequest, 
    db: AsyncSession = Depends(get_db)
):
    # Проверка пользователя
    if not await Users.user_exists(db, request.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Отправка запроса в Rasa
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.RASA_SERVER_URL,
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
        rasa_data = response.json()[0].get('custom')
        print(rasa_data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Неверный формат JSON от Rasa"
        )
    
    await ServerErrorHandler.validate_service_response(
        rasa_data, 
        ["type", "data", ],
        "Rasa"
    )
    
    print(rasa_data)
    return TextResponse(type=rasa_data['type'], data=rasa_data['data'], file_name=rasa_data.get('file_name'))