from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import Users
from typing import Dict, Any
from app.core.config import settings

from app.utils.LLM import async_generate_content

GEMINI_API_KEY = settings.GEMINI_API_KEY

client_router = APIRouter()

class UserCreateResponse(BaseModel):
    user_id: int
    
class CodeErrorRequest(BaseModel):
    user_id: int
    code: str
    execution_result: Dict[str, Any]

class CodeFixResponse(BaseModel):
    code: str
    comments: str


@client_router.post('/fix_code_error', response_model=CodeFixResponse)
async def fix_code_error(
    request: CodeErrorRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Исправление ошибки в коде с помощью LLM
    """
    try:
        # Проверка пользователя
        user = await Users.get_by_id(db, request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Формируем структурированные данные для LLM
        llm_input = {
            "original_code": request.code,
            "error_details": request.execution_result
        }

        prompt = """
        Analyze this code error and provide:
        1. Fixed code in 'code' field
        2. Explanation in 'comments' field
        
        Error context:
        - The code failed with the provided error
        - Return JSON format with 'code' and 'comments' keys
        """

        # Используем нашу асинхронную функцию
        llm_response = await async_generate_content(
            api_key=GEMINI_API_KEY,
            prompt=prompt,
            input_data=llm_input,
        )

        # Преобразуем ответ в JSON (может потребоваться дополнительная обработка)
        if isinstance(llm_response, str):
            import json
            llm_response = json.loads(llm_response)

        return CodeFixResponse(
            code=llm_response.get("code", request.code),  # Возвращаем оригинал, если нет исправления
            comments=llm_response.get("comments", "No fixes provided by LLM")
        )

    except HTTPException:
        raise
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="LLM service timeout"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )
    

@client_router.post('/init_user', response_model=UserCreateResponse)
async def create_new_user(
    db: AsyncSession = Depends(get_db)
):
    """Создает нового пользователя и возвращает его ID."""
    try:
        new_user_id = await Users.create_user(db)
        return UserCreateResponse(user_id=new_user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании пользователя: {str(e)}"
        )