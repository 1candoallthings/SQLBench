import requests
import time
import os
import openai

#openai.api_type = "azure"
#openai.api_base = "https://wangxiang.openai.azure.com/"
#openai.api_version = "2023-05-15"


class GPT:

    def __init__(self, keys=None):
        self._key = None

    def __call__(self,
                 prompt,
                 *args, **kwargs):

        response = openai.ChatCompletion.create(
            # engine="gpt-35-turbo-16k",  # engine = "deployment_name".
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=200,
        )

        time.sleep(0.1)
        try:
            # print(f"prompt: {prompt}")
            # print(f"result: {response['choices'][0]['message']['content']}")
            return response['choices'][0]['message']['content']
        except:
            time.sleep(1)
            response = openai.ChatCompletion.create(
                # engine="gpt-35-turbo-16k",  # engine = "deployment_name".
                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=200,
            )
            # print(f"prompt: {prompt}")
            # print(f"result: {response['choices'][0]['message']['content']}")
            return response['choices'][0]['message']['content']


if __name__ == '__main__':
    llm = GPT()
    print(llm('请用一句话解释万有引力'))