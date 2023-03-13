'''
Description: 
Autor: didiplus
Date: 2023-02-22 10:10:24
LastEditors: lin
LastEditTime: 2023-02-24 15:36:06
'''



from revChatGPT.V3 import Chatbot
from loguru import logger
import uuid,json
import openai,time
from config import settings
from typing import List
from httpx import AsyncClient
from collections import defaultdict



class Model(object):
    def reply(self,query,context =None):
        """
        model auto-reply content
        :param req: received message
        :return: reply content
        """
        raise NotImplementedError

def  chat_gpt_api(prompt:str):

    chatbot = Chatbot(config={
       "session_token":settings.SESSION_TOKEN,
       "conversation_id":uuid.uuid1()
    })

    prev_text = ""
    for data in chatbot.ask(prompt):
        message = data["message"][len(prev_text) :]
        logger.info(message)
        prev_text = data["message"]
    return prev_text



chatbot = Chatbot(api_key="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")


openai.api_key =settings.OPENAIKEY
def generate_response_v1(prompt):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt,
    temperature=0.7,
    max_tokens=3000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    message = response.choices[0].text
    return message.strip()




def chatgpt_turbo(messages):

    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        temperature=0.8,
        max_tokens=3000,
        stream=True,
        messages=messages
    )
    logger.info("chatgpt返回的结果:{}".format(completion))
    return completion


async def stream_request(val:List[dict[str,str]]):
    """
    :param val 对话内容
    :return 
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer  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" 
    }

    params  ={
        "model": "gpt-3.5-turbo",
        "messages":val,
        "temperature":0.8,
        "n":1,
        "max_tokens": 3000,
        "stream":True
    }

    async with AsyncClient() as clinet:
        async with clinet.stream("POST",url,headers=headers,json=params,timeout=60) as respones:
            async for line in respones.aiter_lines():
                if line.strip() == "":
                    continue

                line = line.replace("data: ", "")
                if  line.strip() == "[DONE]":
                    break
                data = json.loads(line)
                print(data)
                if data.get("choices") is None or len(data.get("choices")) == 0 or data.get("choices")[0].get("delta").get("finish_reason") is not None:
                    return
                yield data.get("choices")[0]
    




