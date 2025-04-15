# client.py
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/client-webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("📩 Получено сообщение от прокси:", data)
    return {"status": "received"}
