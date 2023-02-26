'''
Description: 
Autor: didiplus
Date: 2023-02-19 22:15:15
LastEditors: lin
LastEditTime: 2023-02-24 15:50:37
'''
'''
Description: 
Autor: didiplus
Date: 2023-02-19 22:15:15
LastEditors: lin
LastEditTime: 2023-02-24 15:38:43
'''
from typing import Optional
from pydantic import BaseModel


class WechatMessageModel(BaseModel):
    ToUserName: Optional[str]
    FromUserName:Optional[str]
    CreateTime:Optional[int]
    MsgType:Optional[str]
    Event:Optional[str]
    Latitude:Optional[str]
    Longitude:Optional[str]
    Precision:Optional[str]
    raw:Optional[str]
    