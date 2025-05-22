from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./clients.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    user_id = Column(String, primary_key=True, index=True)
    client_url = Column(String)

Base.metadata.create_all(bind=engine)
