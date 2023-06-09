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
    

user_session = dict()

# OpenAI对话模型API (可用)
class ChatGPTModel(Model):
    def __init__(self):
        openai.api_key =settings.OPENAIKEY
        proxy = settings.PROXY
        if proxy:
            openai.proxy = proxy

    def reply(self, query, context=None):
        # acquire reply content
        if not context or not context.get('type') or context.get('type') == 'TEXT':
            logger.info("[CHATGPT] query={}".format(query))
            from_user_id = context['from_user_id']
            if query == '#清除记忆':
                Session.clear_session(from_user_id)
                return '记忆已清除'

            new_query = Session.build_session_query(query, from_user_id)
            logger.debug("[CHATGPT] session query={}".format(new_query))

            # if context.get('stream'):
            #     # reply in stream
            #     return self.reply_text_stream(query, new_query, from_user_id)

            reply_content = self.reply_text(new_query, from_user_id, 0)
            #log.debug("[CHATGPT] new_query={}, user={}, reply_cont={}".format(new_query, from_user_id, reply_content))
            return reply_content

        elif context.get('type', None) == 'IMAGE_CREATE':
            return self.create_img(query, 0)

    def reply_text(self, query, user_id, retry_count=0):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # 对话模型的名称
                messages=query,
                temperature=0.9,  # 值在[0,1]之间，越大表示回复越具有不确定性
                top_p=1,
                frequency_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
                presence_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            )
            reply_content = response.choices[0]['message']['content']
            used_token = response['usage']['total_tokens']
            logger.debug(response)
            logger.info("[CHATGPT] reply={}", reply_content)
            if reply_content:
                # save conversation
                Session.save_session(query, reply_content, user_id, used_token)
            return response.choices[0]['message']['content']
        except openai.error.RateLimitError as e:
            # rate limit exception
            logger.warn(e)
            if retry_count < 1:
                time.sleep(5)
                logger.warn("[CHATGPT] RateLimit exceed, 第{}次重试".format(retry_count+1))
                return self.reply_text(query, user_id, retry_count+1)
            else:
                return "提问太快啦，请休息一下再问我吧"
        except openai.error.APIConnectionError as e:
            logger.warn(e)
            logger.warn("[CHATGPT] APIConnection failed")
            return "我连接不到你的网络"
        except openai.error.Timeout as e:
            logger.warn(e)
            logger.warn("[CHATGPT] Timeout")
            return "我没有收到你的消息"
        except Exception as e:
            # unknown exception
            logger.exception(e)
            Session.clear_session(user_id)
            return "请再问我一次吧"


    def reply_text_stream(self, query, new_query, user_id, retry_count=0):
        try:
            res = openai.Completion.create(
                model="text-davinci-003",  # 对话模型的名称
                prompt=new_query,
                temperature=0.9,  # 值在[0,1]之间，越大表示回复越具有不确定性
                #max_tokens=4096,  # 回复最大的字符数
                top_p=1,
                frequency_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
                presence_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
                stop=["\n\n\n"],
                stream=True
            )
            return self._process_reply_stream(query, res, user_id)

        except openai.error.RateLimitError as e:
            # rate limit exception
            logger.warn(e)
            if retry_count < 1:
                time.sleep(5)
                logger.warn("[CHATGPT] RateLimit exceed, 第{}次重试".format(retry_count+1))
                return self.reply_text_stream(query, user_id, retry_count+1)
            else:
                return "提问太快啦，请休息一下再问我吧"
        except openai.error.APIConnectionError as e:
            logger.warn(e)
            logger.warn("[CHATGPT] APIConnection failed")
            return "我连接不到你的网络"
        except openai.error.Timeout as e:
            logger.warn(e)
            logger.warn("[CHATGPT] Timeout")
            return "我没有收到你的消息"
        except Exception as e:
            # unknown exception
            logger.exception(e)
            Session.clear_session(user_id)
            return "请再问我一次吧"


    def _process_reply_stream(
            self,
            query: str,
            reply: dict,
            user_id: str
    ) -> str:
        full_response = ""
        for response in reply:
            if response.get("choices") is None or len(response["choices"]) == 0:
                raise Exception("OpenAI API returned no choices")
            if response["choices"][0].get("finish_details") is not None:
                break
            if response["choices"][0].get("text") is None:
                raise Exception("OpenAI API returned no text")
            if response["choices"][0]["text"] == "<|endoftext|>":
                break
            yield response["choices"][0]["text"]
            full_response += response["choices"][0]["text"]
        if query and full_response:
            Session.save_session(query, full_response, user_id)


    def create_img(self, query, retry_count=0):
        try:
            logger.info("[OPEN_AI] image_query={}".format(query))
            response = openai.Image.create(
                prompt=query,    #图片描述
                n=1,             #每次生成图片的数量
                size="256x256"   #图片大小,可选有 256x256, 512x512, 1024x1024
            )
            image_url = response['data'][0]['url']
            logger.info("[OPEN_AI] image_url={}".format(image_url))
            return image_url
        except openai.error.RateLimitError as e:
            logger.warn(e)
            if retry_count < 1:
                time.sleep(5)
                logger.warn("[OPEN_AI] ImgCreate RateLimit exceed, 第{}次重试".format(retry_count+1))
                return self.reply_text(query, retry_count+1)
            else:
                return "提问太快啦，请休息一下再问我吧"
        except Exception as e:
            logger.exception(e)
            return None


class Session(object):
    @staticmethod
    def build_session_query(query, user_id):
        '''
        build query with conversation history
        e.g.  [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
        :param query: query content
        :param user_id: from user id
        :return: query content with conversaction
        '''
        session = user_session.get(user_id, [])
        if len(session) == 0:
            system_prompt = settings.CHARACTER_DESC
            system_item = {'role': 'system', 'content': system_prompt}
            session.append(system_item)
            user_session[user_id] = session
        user_item = {'role': 'user', 'content': query}
        session.append(user_item)
        return session

    @staticmethod
    def save_session(query, answer, user_id, used_tokens=0):
        max_tokens = settings.CONVERSATION_MAX_TOKENS
        if not max_tokens or max_tokens > 4000:
            # default value
            max_tokens = 1000
        session = user_session.get(user_id)
        if session:
            # append conversation
            gpt_item = {'role': 'assistant', 'content': answer}
            session.append(gpt_item)

        if used_tokens > max_tokens and len(session) >= 3:
            # pop first conversation (TODO: more accurate calculation)
            session.pop(1)
            session.pop(1)

    @staticmethod
    def clear_session(user_id):
        user_session[user_id] = []



