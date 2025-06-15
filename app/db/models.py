from sqlalchemy import Column, Integer
from .database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)

    @classmethod
    async def create_user(cls, session: AsyncSession) -> int:
        """Создает нового пользователя и возвращает его id."""
        new_user = cls()
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user.user_id 

    @classmethod
    async def user_exists(cls, session: AsyncSession, user_id: int) -> bool:
        """Проверяет существование пользователя по ID. Возвращает True/False."""
        user = await session.get(cls, user_id)
        return user is not None