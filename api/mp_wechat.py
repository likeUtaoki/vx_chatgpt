from fastapi import APIRouter,Query,Request
from core import RedisTools
from config import settings
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message
from wechatpy.events import ScanEvent,SubscribeScanEvent
from wechatpy.replies import TextReply
from utils import generate_response
from loguru import logger
from starlette.responses import HTMLResponse


router = APIRouter(prefix="/mp",tags=["微信公众号接口"])


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


@router.post("/signature")
async def signature_post(request:Request):
    try:
        rec_msg = parse_message(await request.body())
        print(rec_msg)
        match (rec_msg.type):
            case "text":
                return handlerText(rec_msg)
            case "event":
                reply = TextReply()
                reply.source = rec_msg.target
                reply.target = rec_msg.source
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


def handlerText(rec_msg):
    reply = TextReply()
    reply.source = rec_msg.target
    reply.target = rec_msg.source
    match (rec_msg.content):
        case "mp_chatgpt":
            reply.content = "git@gitee.com:didiplus/mp_chatgpt.git"
            return reply.render()
        case _:
            reply.content = generate_response(rec_msg.content)
            return reply.render()


