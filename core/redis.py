'''
Description: 
Autor: didiplus
Date: 2023-02-18 13:39:29
LastEditors: lin
LastEditTime: 2023-02-25 09:20:34
'''


from aioredis import Redis
from typing import Union,Optional
from config import settings
class RedisTools(Redis):

    def __init__(self):
        super().__init__(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DATABASE,
            socket_timeout=settings.REDIS_TIMEOUT
            )

    async def is_existsKey(self,key:str)->bool:
        
        return True if  await self.get(name=key) is not None  else False
    
    async def hasKey(self,key:str) ->bool:
        return await self.is_existsKey(key)

    async def set_value(self,key:str,value:str,ex=7200)->None:
        await self.set(name=key,value=value,ex=ex)
    

    async def get_value(self,key:str) ->str:
        res = await self.get(name=key)
        return str(res,encoding="utf-8")