from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.config import settings
from google import genai  # Импорт для работы с Gemini API

gemini_router = APIRouter()

class GeminiPromptRequest(BaseModel):
    prompt: str

class GeminiPromptResponse(BaseModel):
    response: str

@gemini_router.post('/gemini_prompt', response_model=GeminiPromptResponse)
async def process_gemini_prompt(request: GeminiPromptRequest):
    """
    Принимает промпт, отправляет его на Gemini API и возвращает ответ LLM
    """
    try:
        # Создаем клиент с API-ключом из настроек
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Отправляем запрос к Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=request.prompt
        )
        
        if not response.text:
            raise ValueError("Empty response from Gemini API")
        
        return GeminiPromptResponse(response=response.text)
    
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini API request failed: {str(e)}"
        )