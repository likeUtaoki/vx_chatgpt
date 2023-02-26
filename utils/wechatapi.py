'''
Description: 
Autor: didiplus
Date: 2023-02-18 14:33:57
LastEditors: lin
LastEditTime: 2023-02-25 09:47:28
'''
import aiohttp
import asyncio
import hashlib
import json
from core import RedisTools
from loguru import logger
from config import settings
from wechatpy import WeChatClient


class WXAPI:


    def __init__(self) -> None:
        self.clinet = WeChatClient(appid=settings.APPID,secret=settings.APPSECRET)

    def generate_qrcode(self,scene):
        res = self.clinet.qrcode.create({
            'expire_seconds': 1800,
            'action_name': 'QR_STR_SCENE',
            'action_info': {
                'scene': {'scene_str': scene},
            }            
        })
        logger.info("获取二维码tickit：{}".format(res))
        return res
    
    def generate_qrcode_url(self,scene):
        try:
            qrcode_data = self.generate_qrcode(scene)
            res = self.clinet.qrcode.get_url(qrcode_data.get("ticket"))
            logger.info("获取临时二维码成功:{}".format(res))
            return res
        except Exception as e:
            logger.error("获取临时二维码出错：{}".format(e))

    @classmethod
    def check_signature(self,signature:str,timestamp:str,nonce:str,token:str):
        """
        签名认证
        """
        tmp = [token,timestamp,nonce]
        tmp.sort()
        res = hashlib.sha1("".join(tmp).encode("utf-8")).hexdigest()
        return True if res  == signature else False 

    @classmethod
    async def __request(self,url,data=None,method="get"):
        async with aiohttp.ClientSession() as session:
            if method == "get":
                async with session.get(url) as resp:
                    res = await resp.json()
                    logger.info("请求结果:{}".format( res))
                    return res
            elif method == "post":
                async with session.post(url=url,data=json.dumps(data)) as resp:
                    res = await resp.json()
                    logger.info("请求结果:{}".format( res))
                    return res
    @classmethod
    async def async_access_token(self):
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(settings.APPID,settings.APPSECRET)
        if await RedisTools().is_existsKey("access_token"):
            return await RedisTools().get_value("access_token")
        else:
            res = await self.__request(url)
            await RedisTools().set_value("access_token",res.get("access_token"))
            return res.get("access_token")
    

    @classmethod
    async def async_generate_qrcode(self,scene):
        logger.info("scene:{}".format(scene))
        """
        获取ticket
        return 
        {
            "ticket":"gQH47joAAAAAAAAAASxodHRwOi8vd2VpeGluLnFxLmNvbS9xL2taZ2Z3TVRtNzJXV1Brb3ZhYmJJAAIEZ23sUwMEmm3sUw==",
            "expire_seconds":60,
            "url":"http://weixin.qq.com/q/kZgfwMTm72WWPkovabbI"
        }
        """
        token = await self.access_token()
        url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token={}".format(token)
        data = {
            "expire_seconds": 60,
            "action_name": "QR_STR_SCENE",
            "action_info": {
                "scene": {
                    "scene_str":scene,
                    
                }
            }
        }
        res = await self.__request(url,data,method="post")
        return res.get("ticket")
    

    @classmethod
    async def async_get_qrcode_url(self,scene):
        ticket = await self.generate_qrcode(scene)
        return "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={}".format(ticket)

    

    @classmethod
    async def async_get_user_info(self,openid:str):
        """
        获取用户基本信息
        https://api.weixin.qq.com/cgi-bin/user/info
        """
        token  = await self.access_token()
        url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}".format(token,openid)
        res = await  self.__request(url)
        return res