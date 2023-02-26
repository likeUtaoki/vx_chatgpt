'''
Description: 
Autor: didiplus
Date: 2023-02-18 13:38:19
LastEditors: lin
LastEditTime: 2023-02-24 21:24:25
'''


from fastapi import FastAPI
from core import RedisTools
import aioredis

from config import settings
from loguru import logger

# async def register_redis(app: FastAPI):
#     redis: RedisTools = await init_redis_pool()  # redis
#     app.state.redis = redis



# # 参考: https://github.com/grillazz/fastapi-redis/tree/main/app
# async def init_redis_pool() -> RedisTools:
#     """ 连接redis """
#     result = await RedisTools.from_url(url=settings.REDIS_URL, encoding=settings.GLOBAL_ENCODING, decode_responses=True)
#     logger.info("初始化redis成功")
#     return result


async def register_redis(app:FastAPI):
    pool = aioredis.ConnectionPool.from_url(
        url=settings.REDIS_URL,decode_responses=True
    )



async def init_redis_pool():
    pool = aioredis.ConnectionPool.from_url(
        url=settings.REDIS_URL,decode_responses=True
    )
    result = await aioredis.Redis()