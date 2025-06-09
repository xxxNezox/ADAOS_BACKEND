'''
Здесь будут функции для запросов к выбранной LLM

from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain how AI works in a few words",
)

print(response.text)

'''
from app.core.config import settings

import asyncio
from google import genai
from typing import Union, Dict, Any

async def async_generate_content(
    prompt: str,
    input_data: Union[str, Dict[str, Any]],
    model: str = "gemini-2.0-flash",
    timeout: int = 30,
    api_key: str = settings.GEMINI_API_KEY
) -> str:
    """
    Асинхронно генерирует контент с помощью Gemini API
    
    :param api_key: Ваш API ключ для Gemini
    :param prompt: Промпт/инструкция для LLM
    :param input_data: Входные данные (текст или JSON)
    :param model: Модель для использования (по умолчанию gemini-2.0-flash)
    :param timeout: Таймаут запроса в секундах
    :return: Текст ответа от LLM
    """
    # Создаем клиент (в реальном коде это лучше вынести наружу)
    client = genai.Client(api_key=api_key)
    
    # Формируем содержимое запроса
    if isinstance(input_data, dict):
        # Если это JSON, преобразуем в строку для промпта
        content = f"{prompt}\n\nInput data:\n{str(input_data)}"
    else:
        # Если это текст, просто объединяем с промптом
        content = f"{prompt}\n\n{input_data}"
    
    try:
        # Выполняем асинхронный запрос
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=model,
                    contents=content
                )
            ),
            timeout=timeout
        )
        return response.text
    except asyncio.TimeoutError:
        raise TimeoutError("Request to Gemini API timed out")
    except Exception as e:
        raise Exception(f"Error in Gemini API request: {str(e)}")


# Пример использования
async def main():
    api_key = "YOUR_API_KEY"
    
    # Пример с текстом
    text_response = await async_generate_content(
        api_key=api_key,
        prompt="Summarize this text:",
        input_data="Artificial intelligence is a field of computer science..."
    )
    print("Text response:", text_response)
    
    # Пример с JSON
    json_response = await async_generate_content(
        api_key=api_key,
        prompt="Analyze this data:",
        input_data={"temperature": 25, "humidity": 60, "location": "Moscow"},
        model="gemini-2.0-pro"
    )
    print("JSON response:", json_response)

# Запуск примера
if __name__ == "__main__":
    asyncio.run(main())