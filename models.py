from pydantic import BaseModel

class RegisterClient(BaseModel):
    user_id: str
    client_url: str

class IncomingMessage(BaseModel):
    user_id: str
    message: str
    client_url: str | None = None
