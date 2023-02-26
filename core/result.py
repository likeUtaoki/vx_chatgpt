'''
Description: 
Autor: didiplus
Date: 2023-02-18 14:51:09
LastEditors: lin
LastEditTime: 2023-02-22 22:06:18
'''
from typing import TypeVar,Generic,Optional,Any,List
from loguru import logger
from pydantic import BaseModel
from pydantic.generics import GenericModel

def result_success(code: int = 200, msg: str = "操作成功", **kwargs) -> dict:
    """返回结果"""
    kwargs.update({'code': code, 'msg': msg})
    logger.debug(kwargs)
    return kwargs


def result_success_no_log(code: int = 200, msg: str = "操作成功", **kwargs) -> dict:
    """返回结果"""
    kwargs.update({'code': code, 'msg': msg})
    return kwargs

SchemasType = TypeVar("SchemasType", bound=BaseModel)

class Result(GenericModel,Generic[SchemasType]):
    code:int
    msg:str


class ResultData(GenericModel, Generic[SchemasType]):
    """ 带data的结果 """
    code: int
    msg: str
    data: Optional[Any]
    status: str="Success"
