'''
Description: 
Autor: didiplus
Date: 2023-02-24 13:22:06
LastEditors: lin
LastEditTime: 2023-02-24 14:28:52
'''
from fastapi import HTTPException,status
from typing import Union
from datetime import timedelta,datetime
import jwt
from jwt import PyJWKError
from config import settings
from loguru import logger

def create_access_token(data:dict,expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow()+expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt



def verify_token(token:str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            return False
    except Exception as e:
        logger.warning("token报错:{}".format(e))
        return False
    return True