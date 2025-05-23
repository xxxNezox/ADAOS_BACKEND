from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from dotenv import load_dotenv
import os
import asyncio
from typing import Optional

from app.whisper import whisper_router
from app.rasa import rasa_router


load_dotenv()

app = FastAPI()

app.include_router(rasa_router, tags=['rasa'], prefix='/api')

"""
ВОТ ПРИМЕР КАК БУДЕМ ЮЗАТЬ РОУТЕРЫ

from app.whisper import whisper_router
from app.rasa import rasa_router

app.include_router(whisper_router, tags=['whisper'], prefix='/api')
app.include_router(rasa_router, tags=['rasa'], prefix='/api/rasa')
"""

"""
Для тестирования выполните curl -X POST -F "file=@test.m4a" http://localhost:8000/transcribe | jq  в терминале (тестовый войс файл лежит в репе)
"""

# =========================================Примка с клиента==================================
"""Формат запроса
json
{
    user_id: 123123123
    user_text: Пирет! какая погода на улице
}
json
{
    user_id: 1231231312
    user_audio: 
}
"""



async def process_task_async(task_data: dict, processor_url: str, task_type: str):
    """Асинхронная обработка задачи в фоне"""
    try:
        response = requests.post(processor_url, json=task_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error processing {task_type}: {str(e)}")
        return None

@app.post("/api/process-audio")
async def process_audio(user_id: str, audio_bytes: bytes):
    """
    Принимает JSON с user_id и аудио в байтах от клиентского приложения
    и отправляет на сервер "обработчик голоса"
    """
    # Немедленный ответ клиенту
    immediate_response = {
        "status": "accepted",
        "message": "Audio received and processing started",
        "user_id": user_id,
        "processing_id": f"audio_{user_id}_{os.urandom(4).hex()}"
    }
    
    # Запускаем обработку в фоне
    asyncio.create_task(
        process_task_async(
            {
                "user_id": user_id,
                "audio_bytes": audio_bytes.hex(),
                "processing_id": immediate_response["processing_id"]
            },
            os.getenv("VOICE_PROCESSOR_URL"), # http://localhost:8000/transcribe
            "audio"
        )
    )
    
    return JSONResponse(content=immediate_response, status_code=202)

@app.post("/api/process-text")
async def process_text(user_id: str, text: str):
    """
    Принимает JSON с user_id и текстом от клиентского приложения
    и отправляет на сервер "МЯМ раса"
    """
    # Немедленный ответ клиенту
    immediate_response = {
        "status": "accepted",
        "message": "Text received and processing started",
        "user_id": user_id,
        "processing_id": f"text_{user_id}_{os.urandom(4).hex()}"
    }
    
    # Запускаем обработку в фоне
    asyncio.create_task(
        process_task_async(
            {
                "user_id": user_id,
                "text": text,
                "processing_id": immediate_response["processing_id"]
            },
            os.getenv("MYAM_RASA_URL"),
            "text"
        )
    )
    
    return JSONResponse(content=immediate_response, status_code=202)

@app.get("/api/check-status/{processing_id}")
async def check_status(processing_id: str):
    """
    Проверка статуса обработки (заглушка - в реальной реализации нужно хранить статусы)
    """
    return {
        "processing_id": processing_id,
        "status": "in_progress",  # или "completed", "failed"
        "last_updated": "2023-01-01T00:00:00Z"
    }

# =========================================Примка с Wisper==================================

@app.post("/api/process-audio")
async def process_audio(user_id: str, audio_bytes: bytes):
    """
    Принимает JSON с user_id и аудио в байтах, последовательно:
    1. Отправляет аудио на сервер обработки голоса
    2. Полученный текст отправляет на сервер "МЯМ раса"
    3. Возвращает объединенный результат клиенту
    """
    try:
        # 1. Немедленный ответ клиенту о начале обработки
        processing_id = f"audio_{user_id}_{os.urandom(4).hex()}"
        immediate_response = {
            "status": "processing",
            "message": "Audio processing started",
            "user_id": user_id,
            "processing_id": processing_id
        }
        
        # 2. Отправляем аудио на обработку голоса (синхронно, так как нужно дождаться результата)
        voice_processor_url = os.getenv("VOICE_PROCESSOR_URL")
        if not voice_processor_url:
            raise HTTPException(status_code=500, detail="Voice processor URL not configured")
        
        voice_response = requests.post(
            voice_processor_url,
            json={
                "user_id": user_id,
                "audio_bytes": audio_bytes.hex(),
                "processing_id": processing_id
            },
            timeout=30  # Таймаут 30 секунд на обработку аудио
        )
        
        if voice_response.status_code != 200:
            raise HTTPException(
                status_code=voice_response.status_code,
                detail=f"Voice processing failed: {voice_response.text}"
            )
        
        voice_result = voice_response.json()
        recognized_text = voice_result.get("text", "")
        
        if not recognized_text:
            return {
                "status": "completed",
                "user_id": user_id,
                "processing_id": processing_id,
                "voice_result": voice_result,
                "message": "Audio processed but no text recognized",
                "myam_rasa_result": None
            }
        
        # 3. Отправляем распознанный текст на MYAM раса
        myam_rasa_url = os.getenv("MYAM_RASA_URL")
        if not myam_rasa_url:
            raise HTTPException(status_code=500, detail="MYAM rasa URL not configured")
        
        myam_response = requests.post(
            myam_rasa_url,
            json={
                "user_id": user_id,
                "text": recognized_text,
                "processing_id": processing_id
            },
            timeout=30  # Таймаут 30 секунд на обработку текста
        )
        
        myam_result = myam_response.json() if myam_response.status_code == 200 else None
        
        # 4. Формируем финальный ответ
        return {
            "status": "completed",
            "user_id": user_id,
            "processing_id": processing_id,
            "voice_processing": {
                "success": True,
                "recognized_text": recognized_text,
                "details": voice_result
            },
            "myam_rasa_processing": {
                "success": myam_response.status_code == 200,
                "response": myam_result,
                "status_code": myam_response.status_code
            }
        }
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Processing timeout exceeded"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audio processing error: {str(e)}"
        )

# =========================================Примка с rasa==================================