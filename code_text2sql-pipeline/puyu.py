# !/usr/bin/env python
# -*- coding: utf-8 -*-
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
                 model= "nova-ptc-xl-v1", # "nova-ptc-xl-v2-1-0-8k-internal",
                 temperature=0.1,
                 top_p=0.9,
                 max_new_tokens=256,
                 repetition_penalty=1.05,
                 stream=False,
                 *args, **kwargs):
        #替换敏感词
        prompt_desen=prompt.replace('Master', 'Bachelor')
        print('-*-S'*20)
        print(f"Puyu Prompt:\n{prompt_desen}")
        print('--' * 30+' Fin Prompt ')
        url = 'http://euclid-70b.mtc.sensetime.com/'
        context = "<|User|>:" + prompt + "\n<|Bot|>:"
        data = {
            "inputs": context,
            "parameters": {
                "do_sample": False,
                "temperature": temperature,
                "top_p": top_p,
                "max_new_tokens": max_new_tokens,
                "repetition_penalty": repetition_penalty,
            }
        }
        Flag = 1
        headers = {
            'Content-Type': 'application/json'
        }
        item = ""
        while Flag:
            time.sleep(0.3)
            try:
                response = requests.post(url, headers=headers, json=data)
                # print(response)
                tmp = ast.literal_eval(response.text)
                if 'generated_text' in response.text:
                    # item = tmp[0]['generated_text']
                    item = tmp[0]['generated_text']

                Flag = 0
            except:
                Flag = 0
                item = 'generated_text'
        return item
        # if ans.text:
        #     try:
        #         ans_text=json.loads(ans.text)

        #     except:
        #         raise Exception('Response can not be parsed !')

        #     if 'data' in ans_text:
        #         if 'choices' in ans_text['data']:
        #             prompt_out=ans_text['data']['choices'][0]['message']
        #             print(f"SenseNova Answer:\n{prompt_out}")
        #             print('-*-E' * 20)
        #             return prompt_out
        #         else:
        #             raise Exception(ans_text)
        #     else:
        #         raise Exception(ans_text)
        # else:
        #     raise Exception('No response returned by SenseNova !')

if __name__ == '__main__':
    llm = Puyu()
    # print(llm('请用一句话解释万有引力',model='nova-ptc-xl-v1',max_new_tokens=512))
    from multiprocessing import Pool
    pool = Pool(1)
    # print(list(pool.map(llm, ['写python快排函数'])))

    input_file = r"G:\AutoTask\text2sql-pipeline\data\shangzi_autotask_20231221.json" # 数据路径
    result_file = open("shangzi_autotask_20231221.json","w",encoding="utf-8") # 最终结果保存路径

    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    anno_all = []
    for i, data in enumerate(input_data):
        anno = {}
        question = data["question"]
        prompt= """
        你是一个策略模型，我会给定你一些工具集和一个问题，你需要理解问题的含义并选择合适的工具执行。
        注意，你首先要判断问题是否为复杂问题，如果是的话，你需要将其拆解为多个子问题进行回答，不要一次性给出答案。
        
        工具集中的每个工具定义如下:
        {
            "tool_list": [
                {
                "get_sql": {
                    "description": "需要进行sql查询。",
                    "input": "none",
                    "output": "返回的结果sql_result_01"
                }
            }, 
            {
                "calculate": {
                    "description": "用于生成python计算公式。",
                    "input": "需要生成python公式的问题。",
                    "output": "执行后的结果calculate_01"
                }
            },
            {
                "document_retrieval": {
                    "description": "用于从文章中检索相关的内容。",
                    "input": "需要检索的问题。",
                    "output": "检索后的答案document_01"
                }
            }
            ]
        }"
        
        请使用下面这个格式,注意不需要生成其他信息:
        question_01:这是拆分的第一个子问题
        tool_01:子问题调用的工具
        answer_01:这是子问题的答案
        question_02:这是拆分的第二个子问题
        tool_02:子问题调用的工具
        answer_02:这是子问题的答案
        stop
        
        以下是回答的示例:
        question: 已知上海市5月份高中阶段的学生数量是该月实有人口数量的一半，那么请问如果要满足全国高中阶段教育毛入学率的标准，高中入学人数应该是多少？
        question_01:上海市5月份高中阶段的学生数量是该月实有人口数量的一半是多少。
        tool_01:get_sql
        answer_01:sql_result_01 
        question_02:查询下满足全国高中阶段教育毛入学率的标准是多少。
        tool_02:document_retrieval
        answer_02:document_01 
        question_03:高中入学人数应该是多少。
        tool_03:calculate
        answer_03:calculate_01 
        stop
        
        下面正式开始:
        """
        prompt += question
        result = llm(prompt=prompt, max_new_tokens=256)
        anno["question_id"] = data["question_id"]
        anno["question"] = data["question"]
        anno["pred_result"] = result
        anno_all.append(anno)
        print(result)
    result_file.write(json.dumps(anno_all, ensure_ascii=False, indent=4) + "\n")
    idx= 0

    headers = {
        'Content-Type': 'application/json'
        }
    item = {}
    item["instruction"] = ''
    context = "<|User|>:"+item["instruction"]+"\n<|Bot|>:"

    data = {
                "inputs": context,
                "parameters": {
                    "do_sample": False,
                    "max_new_tokens": 256
                }
            }



