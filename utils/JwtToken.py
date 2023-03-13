'''
Description: 
Autor: didiplus
Date: 2023-02-24 13:22:06
LastEditors: lin
LastEditTime: 2023-02-24 14:28:52
'''
from fastapi import HTTPException,Security
from typing import Union
from datetime import timedelta,datetime
import jwt
from jwt import PyJWKError
from config import settings
from loguru import logger
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from passlib.context import CryptContext

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




class AuthHandler():

    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'],deprecated="auto")
    secret = settings.SECRET_KEY

    def get_password_hash(self,password:str) ->str:

        return self.pwd_context.hash(password)
    

    def verify_password(self, plain_password:str, hashed_password:str)->bool:

        return self.pwd_context.verify(plain_password,hashed_password)
    

    def encode_token(self,user_id) ->str:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0,minutes=5),
            "iat": datetime.utcnow(),
            "sub": user_id
        }

        return jwt.encode(
            payload,
            self.secret,
            algorithm=settings.ALGORITHM
        )
    
    def decode_token(self,token:str):
        
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail='Invalid token')


    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)