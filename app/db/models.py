from sqlalchemy import Column, Integer
from .database import Base

class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
