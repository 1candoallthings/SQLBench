# coding:utf-8

import openai
import pyperclip
from settings import SECRETKEYS


class WebGPT:
    def __call__(self, prompt,*args,**kwargs):
        # print(f"### PROMPT START ---\n\n{prompt}\n\n### PROMPT END ---")
        pyperclip.copy(prompt)
        # answer = input("粘贴ChatGPT网页版的答案: ")
        input("Prompt已经复制至系统剪贴板，请将该Prompt粘贴到ChatGPT网页版, 获得答案后再将答案复制至剪贴板，系统将从剪贴板自动读取答案\n完成后请按下Enter键继续...")
        answer = pyperclip.paste()
        return answer


class CompletionGPT:
    def __init__(self,keys=SECRETKEYS['openai']):
        self.load_key(key=keys[-1])

    @staticmethod
    def load_key(key):
        openai.api_key = key

    def __call__(self, prompt,
                 model='text-davinci-003', temperature=0, max_tokens=640,*args,**kwargs):
        '''

        :param prompt: options ["gpt-3.5-turbo-16k",'text-davinci-003']
        :param model:
        :param temperature:
        :param max_tokens:
        :param args:
        :param kwargs:
        :return:
        '''
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        answer=response.choices[0].text.strip()
        return answer


class ChatCompletionGPT:
    def __init__(self,keys=SECRETKEYS['openai']):
        self.load_key(key=keys[-1])

    @staticmethod
    def load_key(key):
        openai.api_key = key

    def __call__(self, prompt,
                 model='gpt-4', temperature=0, max_tokens=640,*args,**kwargs):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        answer=response.choices[0].message.content.strip()
        return answer


class Api2dCompletionGPT:
    def __init__(self,keys=SECRETKEYS['api2d']):
        self.load_key(key=keys[-1])
        openai.api_base = "https://openai.api2d.net/v1"

    @staticmethod
    def load_key(key):
        openai.api_key = key

    def __call__(self, prompt,model='text-davinci-003', temperature=0, max_tokens=640,*args,**kwargs):
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        answer=response.choices[0].text.strip()
        return answer


class Api2dChatCompletionGPT:
    def __init__(self,keys=SECRETKEYS['api2d']):
        self.load_key(key=keys[-1])
        openai.api_base = "https://openai.api2d.net/v1"

    @staticmethod
    def load_key(key):
        openai.api_key = key

    def __call__(self, prompt,model='gpt-4-0613', temperature=0, max_tokens=640,*args,**kwargs):
        completion = openai.ChatCompletion.create(model=model,
                                                  messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                            {"role": "user", "content": prompt}],
                                                  temperature=temperature,
                                                  max_tokens=max_tokens,
                                                  )
        ans=completion.choices[0].message.content

        return ans


if __name__=='__main__':
    # agent = ChatCompletionGPT()
    agent=CompletionGPT()
    # agent=Api2dCompletionGPT()

    print(agent('解释万有引力'))