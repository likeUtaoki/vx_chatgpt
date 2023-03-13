'''
Description: 
Autor: didiplus
Date: 2023-02-20 13:30:45
LastEditors: lin
LastEditTime: 2023-02-25 09:39:33
'''
from fastapi import APIRouter,Request,Header
from core import ResultData,result_success,RedisTools
from utils import verify_token,WXAPI
from fastapi.templating import Jinja2Templates
from typing import Union
router = APIRouter(tags=["登录页面渲染"])

templates = Jinja2Templates(directory="templates")

@router.get("/login",summary="登录页面渲染")
def login(request:Request):
    return templates.TemplateResponse("login_v1.html",{
        'request':request
    })




@router.get("/chatgpt",summary="渲染聊天机器人页面")
def chat(request:Request):
    return templates.TemplateResponse("index.html",{
        'request':request
    })



@router.get("/",summary="渲染聊天机器人页面")
def chat(request:Request):
    return templates.TemplateResponse("chat.html",{
        'request':request
    })


@router.post("/verify_token",response_model=ResultData)
def check_login(access_token:Union[str,None]=Header(None)):
    print(access_token)
    if  access_token !="null" and  verify_token(access_token) :
        return  result_success()
    else:
        return result_success(code=301)
    






