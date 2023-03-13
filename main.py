'''
Description: 
Autor: didiplus
Date: 2023-02-18 13:36:42
LastEditors: lin
LastEditTime: 2023-02-23 23:09:17
'''
import uvicorn
from fastapi import FastAPI
from register import *
from loguru import logger
from starlette.staticfiles import StaticFiles
from config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    debug=settings.DEBUG,
    title=settings.TITLE,
)

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许访问的源
        allow_credentials=True,  # 支持 cookie
        allow_methods=("*"),  # 允许使用的请求方法
        allow_headers=("*"),  # 允许携带的 Headers        
)


app.mount("/static",StaticFiles(directory="static"),name="static")

async def create_app():
    """ 注册中心 """

    logger_init()  # 日志初始化
    register_router(app)
    await register_redis(app) #注册redis
    logger.info("startup over")  # 初始化日志


@app.on_event("startup")
async def startup():
    logger.info("startup")
    await create_app()



@app.on_event("shutdown")
async def shutdown():
    pass



if __name__ == '__main__':
    """
    app	运行的 py 文件:FastAPI 实例对象
    host	访问url，默认 127.0.0.1
    port	访问端口，默认 8080
    reload	热更新，有内容修改自动重启服务器
    debug	同 reload
    reload_dirs	设置需要 reload 的目录，List[str] 类型
    log_level	设置日志级别，默认 info
    """
    uvicorn.run(
        app='main:app',
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        reload=settings.UVICORN_RELOAD
    )
