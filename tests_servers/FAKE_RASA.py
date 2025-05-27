from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.post("/webhooks/rest/webhook")
async def mock_rasa_endpoint(request: Request):
    # Здесь можно добавить логирование входящего запроса, если нужно
    # request_data = await request.json()
    # print("Received request:", request_data)
    
    # Фиксированный ответ, который ожидает основной сервер
    response_data = {
        "type": "text",
        "data": "Привет, как дела"
    }
    
    return JSONResponse(content=response_data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5005)