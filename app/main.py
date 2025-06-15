from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import engine, Base
from app.db.models import Users

from app.routers.rasa import rasa_router
from app.routers.whisper import whisper_router
from app.routers.client import client_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def create_test_user():
    """Создание тестового пользователя при старте приложения"""
    async with AsyncSession(engine) as session:
        # Проверяем существование пользователя
        existing_user = await session.get(Users, 1)
        if not existing_user:
            test_user = Users(user_id=1)
            session.add(test_user)
            await session.commit()
            print("Тестовый пользователь создан")
        else:
            print("Тестовый пользователь уже существует")

# @app.on_event("startup")
# async def startup():
#     # Создаём таблицы
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
    
#     # Создаём тестового пользователя
#     await create_test_user()

app.include_router(rasa_router, prefix="/api", tags=["rasa"])
app.include_router(whisper_router, prefix="/api", tags=["whisper"])
app.include_router(client_router, prefix="/api", tags=["client"])