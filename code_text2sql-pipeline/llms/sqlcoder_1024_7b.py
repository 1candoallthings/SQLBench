import requests
import ast
import time
import jsonlines
import requests
import json
import time


class SQLCoder7B:
    def __init__(self):
        pass

    def __call__(self,
                 prompt,
                 # model= "nova-ptc-xl-v1", # "nova-ptc-xl-v2-1-0-8k-internal",
                 temperature=1e-7,
                 top_p=0.9,
                 max_new_tokens=256,
                 repetition_penalty=1.02,
                 stream=False,
                 *args, **kwargs):
        url = 'http://cluster-proxy.sh.sensetime.com:20050/generate'  ## 这里对应前面配置的管理机端口号 若有新的llm屌用只改动19939即可

        data = {
            "inputs": prompt,
            "parameters": {
                "do_sample": False,
                "temperature": temperature,
                "top_k": 1,
                "max_new_tokens": max_new_tokens,
                "repetition_penalty": repetition_penalty,
            }
        }
        response = requests.post(url, json=data)

        time.sleep(0.1)
        if response.status_code == 200:
            try:
                res = response.json()
            except:
                raise Exception('Response can not be parsed !')
            # print("puyuprompt:", prompt)
            # print("puyuresult:", res["generated_text"][0].rstrip("</s>"))
            return res["generated_text"][0].rstrip("</s>")
        else:
            raise Exception('No response returned by SenseNova !')


if __name__=='__main__':
    llm=SQLCoder7B()
    print(llm('请用一句话解释万有引力', max_new_tokens=512))
