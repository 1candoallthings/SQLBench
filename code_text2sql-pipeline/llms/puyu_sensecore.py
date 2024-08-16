import requests
import ast
import time
import jsonlines
import requests
import json
import time


class Puyu:
    def __init__(self):
        pass

    def __call__(self,
                 prompt,
                 core_pod_ip='10.119.49.106',
                 temperature=0.001,
                 top_p=0.9,
                 max_new_tokens=256,
                 repetition_penalty=1.05,
                 stream=False,
                 *args, **kwargs):


        server = "http://101.230.144.204:8008/api/generate"
        headers = {"Content-Type": "application/json"}
        endpoint = f"http://{core_pod_ip}:2345/generate"  # cci tgi-gpu8
        context = "<|User|>:" + prompt + "\n<|Bot|>:"
        request_body = {
            "endpoint": endpoint,
            "inputs": context,
            "parameters": {
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": True,
                "max_new_tokens": max_new_tokens,
                "top_k": 1,
                "repetition_penalty": repetition_penalty,
                "stop": [
                    #  "</s>",
                    #  "User:",
                ]
            }
        }
        response = requests.post(server, headers=headers, json=request_body, stream=stream)
        print(response)
        time.sleep(0.1)
        if response.status_code == 200:
            try:
                res = response.json()
            except:
                raise Exception('Response can not be parsed !')

            return res["generated_text"].rstrip("</s>")
        else:
            raise Exception('No response returned by SenseNova !')


if __name__=='__main__':
    llm=Puyu()
    print(llm('请用一句话解释万有引力', max_new_tokens=512))

