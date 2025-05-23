from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.exc import IntegrityError
from .database import get_db

router = APIRouter()


'''
1. юзер отправляет свой айди и войс
2. сервер отправляет это висперу
3. ответ виспера перенаправляется в расу
4. ответ расы отправляем юзеру

юзер -> сервер -> виспер -> сервер -> *отправляем текст от имени юзера* (раса -> сервер -> юзер)

Это похоже на обычный текстовый запрос от юзера:
раса -> сервер -> юзер

'''
@router.get('/')
def get_notes(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):
    ...