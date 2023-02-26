'''
Description: 
Autor: didiplus
Date: 2023-02-22 10:10:24
LastEditors: lin
LastEditTime: 2023-02-24 15:36:06
'''



from revChatGPT.V1 import Chatbot
from loguru import logger
import uuid
import openai
from config import settings


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




openai.api_key =settings.OPENAIKEY
def generate_response(prompt):
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


        
    

