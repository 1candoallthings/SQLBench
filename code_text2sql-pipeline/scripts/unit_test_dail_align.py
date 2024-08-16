import json, tqdm, sys, os, re

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from settings import SECRETKEYS
from utils import codellama, Puyu, SenseNova
from utils import Llama2 as llama2

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='llama2')
args = parser.parse_args()

llm_name = args.llm

def formatting_prompt(sample):
    ddl = sample['ddl']

    template_info =   "/* Given the following database schema: */\n" \
                      "{}"
    template_question = "/* Answer the following: {} */"

    sql = template_info.format("\n\n".join(ddl.split(";")))
    prompt = "\n\n".join(
        [sql, template_question.format(sample['question']) + "\nSELECT "])
    return prompt


def parallel_call(inps):
    querys, api = inps[0], inps[1]
    llm = eval(llm_name)()
    res = []
    for q in tqdm.tqdm(querys):
        out = llm(q, core_pod_ip=api)
        res.append(out.replace("\n", '  '))
    return res


if __name__ == '__main__':
    proj_dir = os.path.dirname(os.path.dirname(__file__))
    input_file = proj_dir + "/data/ppl_test.json"
    with open(input_file) as f:
        input_data = json.load(f)
    global cnt
    cnt = 0
    # Your algo
    prompt_target = []
    for sample in tqdm.tqdm(input_data):
        prompt_target.append(formatting_prompt(sample))
    # print(cnt)
    # llm=Llama2()
    # print(llm(prompt_target))

    from multiprocessing import Pool
    num_key = len(SECRETKEYS[llm_name])
    assert num_key > 1
    num_pmpt = len(prompt_target)
    proc_unit = num_pmpt // num_key
    pool = Pool(num_key)
    ans = list(pool.map(parallel_call,
                zip([prompt_target[i * proc_unit : (i+1) * proc_unit] for i in range(num_key)],
                    SECRETKEYS[llm_name])))
    llm = eval(llm_name)()
    res = []
    for q in tqdm.tqdm(range(num_pmpt - num_pmpt % num_key, num_pmpt)):
        out = llm(prompt_target[q], core_pod_ip=SECRETKEYS[llm_name][-1])
        res.append(out.replace("\n", '  '))
    ans.append(res)
    print(llm_name)
    with open(f'pred_{llm_name}_dailpmpt.txt', 'w',encoding='utf-8') as file:
        result = '\n'.join(['\n'.join(item) for item in ans])
        file.write(result)
    
    # from typing import List, Optional
    # import requests
    # import yaml
    # import time
    # import json
    # import sys
    # import sqlite3
    # from sqlalchemy import create_engine, text

    # llm = SenseNova()
    # stms = time.time()
    # with open(proj_dir + '/utils/database-spider/dev.json','r',encoding='utf-8') as f:
    #     dev=json.load(f)
    # with open('pred_nova_wo_tab.txt', 'w',encoding='utf-8') as file:
    #     for ix, item in enumerate(tqdm.tqdm(dev)):
    #         # if ix < 957:
    #         #     continue
    #         db_id=item['db_id']
    #         question=item['question']
    #         db_url = f'sqlite:////{proj_dir}/utils/database-spider/database-dev/{db_id}/{db_id}.sqlite'
    #         engine = create_engine(db_url)
    #         connection = engine.connect()
    #         query = text("""
    #             SELECT name
    #             FROM sqlite_master
    #             WHERE type='table';
    #         """)
    #         output_text = ""
    #         result = connection.execute(query)
    #         for row in result:
    #             table_name = row[0]
    #             # if input_data[ix]['linked_tables'] and not table_name in input_data[ix]['linked_tables']:
    #             #     continue
    #             output_text += f"# {table_name}("
    #             columns_query = text(f"PRAGMA table_info({table_name});")
    #             columns_result = connection.execute(columns_query)
    #             for i, column_row in enumerate(columns_result):
    #                 column_name = column_row[1]  # Use integer index 1 for the 'name' column
    #                 if i != 0:
    #                     output_text += f",{column_name}"
    #                 else:
    #                     output_text += f"{column_name}"
    #             output_text += ");\n"
    #         output_text = output_text[:-2] + "." + output_text[-1]
    #         prompt=f'''### Complete sqlite SQL query only and with no explanation\n### Sqlite SQL tables, with their properties:\n#\n{output_text}#\n### {question}\n SELECT'''
    #         # print(prompt)
    #         result=llm(prompt)
    #         print('return', result)

    #         result = ' '.join(result.splitlines())
    #         file.write(str(result)+'\n')
    #         connection.close()
    # print(time.time() - stms)