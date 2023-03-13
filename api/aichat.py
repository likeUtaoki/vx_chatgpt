'''
Description: 
Autor: didiplus
Date: 2023-02-19 09:38:15
LastEditors: lin
LastEditTime: 2023-02-24 14:48:15
'''
from fastapi import APIRouter,WebSocket, WebSocketDisconnect,Request,Body
from utils import manager,generate_response_v1,verify_token,chatbot
from collections import defaultdict

router = APIRouter(tags=["ChatGPT接口"])


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket,token:str):
    if verify_token(token):
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await manager.send_personal_message(generate_response_v1(data), websocket)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    else:
        await manager.send_personal_message("token过期了,请重新登录",websocket)



@router.websocket("/chat")
async def chat(websocket: WebSocket):
    
    try:
        await manager.connect(websocket)
        while True:
            question = await websocket.receive_text()
            await manager.send_personal_message(chatbot.ask_stream(question),websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


        


@router.post("/chat-process")

async def chat_process():
    from utils.ChatGPT import chatbot

    res = chatbot.ask("你好")
    print(res)





    




