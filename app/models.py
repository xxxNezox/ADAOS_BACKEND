from .database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func

class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)


# Вот внизу чисто мусор на всякий случай емае

# from .database import Base
# from sqlalchemy import TIMESTAMP, Column, String, Boolean
# from sqlalchemy.sql import func
# from fastapi_utils.guid_type import GUID, GUID_SERVER_DEFAULT_POSTGRESQL


# class Note(Base):
#     __tablename__ = 'notes'
#     id = Column(GUID, primary_key=True,
#                 server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
#     title = Column(String, nullable=False, unique=True)
#     content = Column(String, nullable=False)
#     category = Column(String, nullable=True)
#     published = Column(Boolean, nullable=False, server_default='True')
#     createdAt = Column(TIMESTAMP(timezone=True),
#                        nullable=False, server_default=func.now())
#     updatedAt = Column(TIMESTAMP(timezone=True),
#                        default=None, onupdate=func.now())

