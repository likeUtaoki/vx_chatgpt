'''
Description: 
Autor: didiplus
Date: 2023-02-18 14:10:35
LastEditors: lin
LastEditTime: 2023-02-25 18:19:58
'''
from fastapi import APIRouter,Query,Request
from core import RedisTools
from utils import WXAPI,create_access_token,chatgpt_turbo
from core import result_success,ResultData,RedisTools
from starlette.responses import HTMLResponse
from loguru import logger
import uuid
from config import settings
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message
from wechatpy.events import ScanEvent,SubscribeScanEvent
from wechatpy.replies import TextReply
router = APIRouter(prefix="/wxmp",tags=["测试微信公众号接口"])


@router.get("/signature",description="验证服务器")
async def signature(
    signature:str=Query(description="签名"),
    echostr:int =Query(description="随机数字类型"),
    timestamp:str = Query(description="时间戳"),
    nonce:str = Query(description="")
    ):
    """
    微信公众号签名
    """
    try:
        check_signature(settings.TOKEN,signature,timestamp,nonce)
        return echostr
    except InvalidSignatureException :
        # 处理异常情况或忽略
        pass



@router.get("/weChatQrCode",summary="公众号临时二维码",response_model=ResultData)
async def qrcode():
    #设置场景id
    login_id =str(uuid.uuid4()).replace("-","")
    #qrcode_url = await WXAPI().async_generate_qrcode(login_id) #异步获取方式
    qrcode_url =  WXAPI().generate_qrcode_url(login_id)
    return result_success(data={"qrcode_url":qrcode_url,"scene_value":login_id})


@router.post("/signature")
async def signature_post(request:Request):
    try:
        rec_msg = parse_message(await request.body())
        print(rec_msg.type)
        match (rec_msg.type):
            case "text":
                reply = TextReply()
                reply.source = rec_msg.target
                reply.target = rec_msg.source
                reply.content = chatgpt_turbo(rec_msg.content)
                return reply.render()
            case "event":
                reply = TextReply()
                reply.source = rec_msg.target
                reply.target = rec_msg.source
                logger.info("场景id:{}".format(rec_msg.scene_id))
                if  not await RedisTools().is_existsKey(rec_msg.scene_id):
                    await RedisTools().set_value(rec_msg.scene_id,rec_msg.source)
                if isinstance(rec_msg,ScanEvent):
                    logger.info("用户关注:{}".format(rec_msg.source))
                    reply.content = "登录成功，欢迎回来"
                    return reply.render()
                elif isinstance(rec_msg,SubscribeScanEvent):
                    reply = TextReply()
                    reply.content = "欢迎关注,登录成功"
                    return reply.render()                  
    except:
        return HTMLResponse('success')




@router.get("/",summary="轮询获取登录状态",response_model=ResultData)
async def scanStatus(wechat_flag:str=Query()):
    #如果redis中有ticket凭证则说明用户已扫码说明登陆成功
    if await RedisTools().hasKey(wechat_flag):
        openid = await RedisTools().get_value(wechat_flag)
        token = create_access_token({"sub": openid})
        logger.info("token:{}".format(token))
        await RedisTools().delete(wechat_flag)
        return result_success(data={"token":token})
    return result_success(code=301)







