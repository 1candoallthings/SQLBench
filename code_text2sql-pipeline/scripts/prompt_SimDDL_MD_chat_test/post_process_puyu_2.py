
import re, os


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='baidu')
args = parser.parse_args()

llm = args.llm

def extract_sql(query, llm='sensenova'):
    if llm == "sensenova":
        if '```sql' in query:
            return re.findall(r"\`\`\`sql(.*?)\`\`\`", query.replace('\n', ' '))[0]
        else:
            return query.replace('\n', '')
    elif llm == 'llama2':
        if "###" in query:
            return "SELECT " + query.split('###')[0]
        else:
            return query.replace('\n', '')
    # elif llm == "sqlcoder":
    #     res = query
    #     if res.lower().startswith("SELECT".lower()) or res.lower().startswith(
    #             " SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
    #         return res
    #     else:
    #         return "SELECT " + res
    elif llm == "codellama":
        query = query.replace("#", "")
        if ';' in query:
            res = re.findall(r'(.*?);', query.replace('\n', ' '))[0]
            if res.lower().startswith("SELECT".lower()) or res.lower().startswith(
                    " SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
                return res
            else:
                return "SELECT " + res
        else:
            return query.replace('\n', '')
    elif llm == 'llama2':
        match = re.findall(r"```(.*?)```", query.replace('\n', ' '))
        if match:
            return match[0]
        if ';' in query:
            res = re.findall(r'(.*?);', query.replace('\n', ' '))[0].strip()
            if res.lower().startswith("SELECT".lower()):
                return res
            else:
                return "SELECT " + res
        elif '###' in query:
            res = re.findall(r'(.*?)###', query.replace('\n', ' '))[0].strip()
            if res.lower().startswith("SELECT".lower()):
                return res
            else:
                return "SELECT " + res
        else:
            return query.replace('\n', '')
    elif llm == "puyu" or llm == "puyu_1024" or llm == "sqlcoder":
        res = query
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return res
    elif llm == "puyu2_sensecore":
        res = query.split(";")[0].replace("<|im_end|>","").replace("<|im_start|>","")
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return res
    elif llm == "puyu2_chat_sensecore":
        # query = query.split(";")[0].replace("<|im_end|>", "").replace("<|im_start|>", "")
        res = query.split(";")[0].replace("<|im_end|>", "").replace("<|im_start|>", "").replace("```","").replace("sql","")
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(
                " SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return res
    elif llm == "puyu2_gauss_sft":
        # query = query.split(";")[0].replace("<|im_end|>", "").replace("<|im_start|>", "")
        res = query.split(";")[0].replace("<|im_end|>", "").replace("<|im_start|>", "").replace("`","").replace("sql","").replace(") SELECT","SELECT")
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(
                " SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return res
    elif llm == "puyu2_gauss_sft_notemplete":
        # query = query.split(";")[0].replace("<|im_end|>", "").replace("<|im_start|>", "")
        res = query.split(";")[0].replace(" ","").replace("<|im_end|>", "").replace("<|im_start|>", "").replace("```","").replace("sql","").replace("#","")
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(
                " SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return res
    elif llm == "baidu":
        if '```sql' in query:
            return re.findall(r"```sql(.*?)```", query.replace('\n', ' '))[0]

def extract_sql_from_text(text):
    sql_pattern = text.replace("\n", " ").replace("ി", " ").split('~~')
    return sql_pattern


import json
proj_dir = os.path.dirname(__file__)
# name = "_optimization_ddl_foreign_key_0204_question_zhishuai"
name = ""
with open(proj_dir + f'/data_0402/pred/pred_{llm}_parallel{name}.txt', 'r', encoding='utf-8') as file:
    content = file.readlines()
# dev_data = json.load(open(r"G:\AutoTask\SQL_benchmark\data\BIRD-SQL\dev\dev\dev.json","r",encoding="utf-8"))
extracted_query = [extract_sql(q, llm) for q in extract_sql_from_text("\n".join(content))]
with open(proj_dir + f'/data_0402/pred/final_pred/{llm}_out_post{name}.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(extracted_query))
    # file.write(json.dumps(anno, ensure_ascii=False, indent=4) + "\n")


import os

os.system(f'python G:/AutoTask/text2sql/test-suite-sql-eval-master/evaluation_1206_test.py '
          fr'--gold G:\AutoTask\text2sql\text2sql-dev\data\spider\test_data\dev_gold.sql '
          f'--pred {proj_dir}/data_0402/pred/final_pred/{llm}_out_post{name}.txt '
          fr'--db G:\AutoTask\text2sql\text2sql-dev\data\spider\test_database/ '
          f'--save {proj_dir}/data_0402/pred/save_results/{llm}_out_post_results{name}.json '
          f'--etype exec')