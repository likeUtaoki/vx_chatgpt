'''
Description: 
Autor: didiplus
Date: 2023-02-18 13:54:28
LastEditors: lin
LastEditTime: 2023-02-18 14:16:05
'''
import os
import logging
from loguru import logger
from config import settings




# 将已写好的logging集成到loguru中
class InterceptHandler(logging.Handler):

    def emit(self,record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth +=1
        
        logger.opt(depth=depth,exception=record.exc_info).log(level,record.getMessage())


def logger_init():
    """日志初始化"""
    logging.basicConfig(handlers=[InterceptHandler()],level=0)
    # 详见: https://loguru.readthedocs.io/en/stable/overview.html#features
    # logger.add(
    #     #logger_file(),  # 保存日志信息的文件路径
    #     encoding=settings.GLOBAL_ENCODING,  # 日志文件编码
    #     level=settings.LOGGER_LEVEL,  # 文件等级
    #     rotation=settings.LOGGER_ROTATION,  # 日志分片: 按 时间段/文件大小 切分日志. 例如 ["500 MB" | "12:00" | "1 week"]
    #     retention=settings.LOGGER_RETENTION,  # 日志保留的时间: 超出将删除最早的日志. 例如 ["1 days"]
    #     enqueue=True  # 在
    # )