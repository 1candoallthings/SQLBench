import re, os
import sqlparse
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='puyu')
args = parser.parse_args()

llm = args.llm

def extract_sql(query, llm='sensenova'):
    if llm == "sensenova":
        if '```sql' in query:
            return re.findall(r"\`\`\`sql(.*?)\`\`\`", query.replace('\n', ' '))[0]
        else:
            return query.replace('\n', '')
    elif llm == 'codellama' or llm == "puyu":
        if '```' in query:
            res = re.findall(r'(.*?)```', query.replace('\n', ' '))[0]
            if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
                return res
            else:
                return "SELECT " + res
        else:
            return query.replace('\n', '')
    # elif llm == "puyu":
    #     res = query
    #     if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
    #         return res
    #     else:
    #         return "SELECT " + res

def extract_sql_from_text(text):
    sql_pattern = text.replace("\n", " ").split('~~')
    return sql_pattern

import json
proj_dir = os.path.dirname(__file__)
with open(proj_dir + f'/spider/pred/pred_{llm}_parallel.txt', 'r', encoding='utf-8') as file:
    content = file.readlines()
# dev_data = json.load(open(r"G:\AutoTask\SQL_benchmark\data\BIRD-SQL\dev\dev\dev.json","r",encoding="utf-8"))
extracted_query = [extract_sql(q, llm) for q in extract_sql_from_text("\n".join(content))]
with open(proj_dir + f'/spider/pred/final_pred/{llm}_out_post.txt', 'w', encoding='utf-8') as file:
    anno = {}
    # for i,data in enumerate(extracted_query):
    #     # print()
    #     anno[i] = extracted_query[i] + "	----- bird_1 -----	" + dev_data[i]["db_id"]
    file.write('\n'.join(extracted_query))
    # file.write(json.dumps(anno, ensure_ascii=False, indent=4) + "\n")


import os

os.system(f'python G:/AutoTask/text2sql/test-suite-sql-eval-master/evaluation.py '
          f'--gold G:/AutoTask/text2sql-dev/exams/official_demo/gold_example.txt '
          f'--pred {proj_dir}/spider/pred/final_pred/{llm}_out_post.txt '
          f'--db G:/AutoTask/SQL_benchmark/data/Spider/spider/database/ '
          f'--etype exec')