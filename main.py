from fastapi import FastAPI, HTTPException
from models import RegisterClient, IncomingMessage
from database import SessionLocal, Client
import aiohttp

app = FastAPI()

@app.post("/register")
async def register_client(data: RegisterClient):
    db = SessionLocal()
    client = db.query(Client).filter(Client.user_id == data.user_id).first()
    if client:
        client.client_url = data.client_url
    else:
        client = Client(user_id=data.user_id, client_url=data.client_url)
        db.add(client)
    db.commit()
    db.close()
    return {"status": "registered"}

@app.post("/rasa-webhook")
async def rasa_webhook(msg: IncomingMessage):
    db = SessionLocal()
    client_url = msg.client_url

    if not client_url:
        client = db.query(Client).filter(Client.user_id == msg.user_id).first()
        if not client:
            db.close()
            raise HTTPException(status_code=404, detail="Client URL not found")
        client_url = client.client_url
    db.close()

    payload = {
        "user_id": msg.user_id,
        "message": msg.message
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(client_url, json=payload) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=502, detail=f"Client error: {await resp.text()}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"status": "delivered"}
