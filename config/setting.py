'''
Description: 
Autor: didiplus
Date: 2023-02-18 13:42:59
LastEditors: lin
LastEditTime: 2023-02-24 15:45:21
'''
import secrets
from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv
import os
from pydantic import BaseSettings

load_dotenv(".env")

class Settings(BaseSettings):
    DEBUG: bool = True  # 开发模式配置
    TITLE: str = "FastAPI对接微信公众号"  # 项目文档
    DESCRIPTION: str = ""  # 描述
    VERSION: str = "v1.0"  # 版本
    GLOBAL_ENCODING: str = 'utf-8'  # 全局编码

    # Uvicorn
    UVICORN_HOST: str = '0.0.0.0'
    UVICORN_PORT: int = 80
    UVICORN_RELOAD: bool = True


    #JWT
    SECRET_KEY="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 6000

    # Redis
    REDIS_HOST: str = os.environ.get("REDIS_HOST") #
    REDIS_PORT: int = os.environ.get("REDIS_PORT")
    REDIS_PASSWORD: str = os.environ.get("REDIS_PASSWORD")
    REDIS_DATABASE: int = 2
    REDIS_TIMEOUT: int = 10
    REDIS_URL: str = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE}"

    # loguru
    LOGGER_DIR: str = "logs"  # 日志文件夹名
    LOGGER_NAME: str = '{time:YYYY-MM-DD_HH-mm-ss}.log'  # 日志文件名 (时间格式)
    LOGGER_LEVEL: str = 'DEBUG'  # 日志等级: ['DEBUG' | 'INFO']
    LOGGER_ROTATION: str = "12:00"  # 日志分片: 按 时间段/文件大小 切分日志. 例如 ["500 MB" | "12:00" | "1 week"]
    LOGGER_RETENTION: str = "7 days"  # 日志保留的时间: 超出将删除最早的日志. 例如 ["1 days"]
    
    #微信公众号
    TOKEN =  os.environ.get("TOKEN")
    APPID:str =  os.environ.get("APPID") #微信公众号APPID
    APPSECRET:str = os.environ.get("APPSECRET") #微信公众号APPSECRET

    #ChatGPT
    OPENAIKEY:str =os.environ.get("OPENAIKEY")
    SESSION_TOKEN =os.environ.get("SESSION_TOKEN")
    CHARACTER_DESC:str = "你是ChatGPT, 一个由OpenAI训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。"
    CONVERSATION_MAX_TOKENS:int =1000
    PROXY:str =""
    class Config:
        case_sensitive = True  # 区分大小写


@lru_cache
def get_settings():
    """ 读取配置优化写法 """
    return Settings()


settings = Settings()