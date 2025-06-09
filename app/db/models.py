from sqlalchemy import Column, Integer
from .database import Base

class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)

    @classmethod
    async def create_user(cls, session: AsyncSession) -> 'Users':
        """Создает нового пользователя и возвращает его объект."""
        new_user = cls()
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    @classmethod
    async def user_exists(cls, session: AsyncSession, user_id: int) -> bool:
        """Проверяет существование пользователя по ID. Возвращает True/False."""
        query = select(cls.user_id).where(cls.user_id == user_id)
        result = await session.execute(query)
        return bool(result.scalar_one_or_none())