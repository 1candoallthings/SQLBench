import re, os
import sqlparse
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='llama2')
args = parser.parse_args()

llm = args.llm

def extract_sql(query, llm='sensenova'):
    if llm == "sensenova":
        if '```sql' in query:
            return re.findall(r"\`\`\`sql(.*?)\`\`\`", query.replace('\n', ' '))[0]
        else:
            return query.replace('\n', '')
    elif llm == 'sqlcoder' or llm == 'codellama' or llm == "llama2":
        if 'sql' in query:
            # print(query)
            try:
                res = re.findall(r'sql(.*?)```', query.replace('\n', ' '))[0]
            except:
                res = re.findall(r'sql(.*?)', query.replace('\n', ' '))[0]
            if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
                return res
            else:
                return "SELECT " + res
        elif '```' in query:
            res = re.findall(r'(.*?)```', query.replace('\n', ' '))[0]
            if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
                return res
            else:
                return "SELECT " + res
        else:
            return query.replace('\n', '')

def extract_sql_from_text(text):
    sql_pattern = text.replace("\n", " ").split('~~')
    return sql_pattern

import json
proj_dir = os.path.dirname(__file__)
# with open(proj_dir + f'/spider/pred/pred_{llm}_parallel_01.txt', 'r', encoding='utf-8') as file:
#     content = file.readlines()
# # dev_data = json.load(open(r"G:\AutoTask\SQL_benchmark\data\BIRD-SQL\dev\dev\dev.json","r",encoding="utf-8"))
# extracted_query = [extract_sql(q, llm) for q in extract_sql_from_text("\n".join(content))]
# with open(proj_dir + f'/spider/pred/final_pred/{llm}_out_post_01.txt', 'w', encoding='utf-8') as file:
#     anno = {}
#     # for i,data in enumerate(extracted_query):
#     #     # print()
#     #     anno[i] = extracted_query[i] + "	----- bird_1 -----	" + dev_data[i]["db_id"]
#     file.write('\n'.join(extracted_query))
#     # file.write(json.dumps(anno, ensure_ascii=False, indent=4) + "\n")


import os

os.system(f'python G:/AutoTask/text2sql/test-suite-sql-eval-master/evaluation_1206_test.py '
          f'--gold G:/AutoTask/text2sql-pipeline/data/dev_gold.sql '
          f'--pred {proj_dir}/spider/pred/final_pred/{llm}_out_post_2.txt '
          f'--db G:/AutoTask/SQL_benchmark/data/Spider/spider/database/ '
          f'--save {proj_dir}/spider/pred/save_result/{llm}_save_result2.json '
          f'--etype exec')