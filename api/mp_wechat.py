from fastapi import APIRouter,Query,Request
from core import RedisTools
from config import settings
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message
from wechatpy.events import ScanEvent,SubscribeScanEvent
from wechatpy.replies import TextReply
from utils import chatbot
import hashlib
from loguru import logger
from starlette.responses import HTMLResponse
from concurrent.futures import ThreadPoolExecutor
from models.chatgpt.chatgpt_model import ChatGPTModel

thread_pool = ThreadPoolExecutor(max_workers=8)
cache = {}


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
        match (rec_msg.type):
            case "text":
                return WechatSubsribeAccount().handle(rec_msg)
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
    except :
        return HTMLResponse('success')


async def handlerText(rec_msg):
    reply = TextReply()
    reply.source = rec_msg.target
    reply.target = rec_msg.source
    msg_content = rec_msg.content
    # 判断是否相同请求,缓存请求
    s=hashlib.md5()
    s.update(msg_content.encode("utf-8"))
    question =s.hexdigest()
    match (msg_content):
        case "mp_chatgpt":
            reply.content = "git@gitee.com:didiplus/mp_chatgpt.git"
            return reply.render()
        case _:
            if  await RedisTools().hasKey(key=question):
                if  await  RedisTools().get_value(question) == "" or await RedisTools().get_value(question) is None:
                    reply.content = "OpenAI卖力运算中，15s后再来问我哦"
                else:
                    reply.content = await RedisTools().get_value(question)
            else:
                reply.content = chatbot.ask(msg_content)
                await RedisTools().set_value(question,reply.content)
            return reply.render()
        



class WechatSubsribeAccount():


    def handle(self, msg, count=0):
        reply = TextReply()
        reply.source = msg.target
        reply.target = msg.source    
        context = dict()
        context['from_user_id'] = msg.source
        key = msg.source
        res = cache.get(key)
        if msg.content == "继续":
            if not res or res.get("status") == "done":
                reply.content = "目前不在等待回复状态，请输入对话"
                return reply.render()
            if res.get("status") == "waiting":
                 reply.content = "还在处理中，请稍后再试"
                 return reply.render()
            elif res.get("status") == "success":
                cache[key] = {"status":"done"}
                reply.content = res.get("data")
                return reply.render() 
            else:
                reply.content = "目前不在等待回复状态，请输入对话"
                return reply.render()
        elif not res or res.get('status') == "done":
            thread_pool.submit(self._do_send, msg.content, context)
            reply.content = "已开始处理，请稍等片刻后输入\"继续\"查看回复"
            return reply.render()
        else:
            if res.get('status') == "done":
                reply.content =  res.get("data")
                thread_pool.submit(self._do_send, msg.content, context)
                return reply.render()
            else:
                reply.content = "上一句对话正在处理中，请稍后输入\"继续\"查看回复"
                return reply.render()


    def _do_send(self,query,context):
        key = context['from_user_id']
        cache[key] = {"status": "waiting"}
        reply_text = ChatGPTModel().reply(query,context)
        logger.info('[WX_Public] reply content: {}'.format(reply_text))
        cache[key] = {"status": "success", "data": reply_text}


