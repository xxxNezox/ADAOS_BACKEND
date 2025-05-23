from app import models, note
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, get_db
from dotenv import load_dotenv
import os
import requests
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(note.router, tags=['Notes'], prefix='/api/notes')


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with SQLAlchemy"}

@app.get("/api/db-healthchecker")
def db_healthchecker(db: Session = Depends(get_db)):
    try:
        # Attempt to execute a simple query to check database connectivity
        db.execute("SELECT 1")
        return {"message": "Database is healthy"}
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database is not reachable")

@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    try:
        #Make a GET request to the JSONPlaceholder API
        response = requests.get(f"https://jsonplaceholder.typicode.com/posts/{post_id}")
        #Check if the request was successful (status code 200)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="API call failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.get('/crypto-price-ethereum')
async def get_crypto_price():
    try:
        api_key = os.getenv("api_key")
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")

        url = (
            "https://api.coingecko.com/api/v3/simple/token_price/ethereum"
            "?contract_addresses=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
            f"&vs_currencies=usd&x_cg_demo_api_key={api_key}"
        )
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="API call failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))















