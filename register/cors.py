'''
Description: 
Autor: didiplus
Date: 2023-02-18 13:34:15
LastEditors: lin
LastEditTime: 2023-02-18 13:35:17
'''

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def register_cors(app:FastAPI):
    """
    跨域请求 -- https://fastapi.tiangolo.com/zh/tutorial/cors/
    https://www.cnblogs.com/poloyy/p/15347578.html
    """

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许访问的源
        allow_credentials=True,  # 支持 cookie
        allow_methods=("*"),  # 允许使用的请求方法
        allow_headers=("*"),  # 允许携带的 Headers        
    )
