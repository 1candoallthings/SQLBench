
import re, os


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
    elif llm == 'llama2' or llm == "codellama":
        if ';' in query:
            res = re.findall(r'(.*?);', query.replace('\n', ' '))[0]
            if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
                return res
            else:
                return "SELECT " + res
        else:
            return query.replace('\n', '')
    elif llm == "puyu":
        return str(query).replace(';', '').replace('ി','').replace('\n','')

def extract_sql_from_text(text):
    sql_pattern = text.split('~~')
    return sql_pattern


proj_dir = os.path.dirname(__file__)
with open(proj_dir + f'/bird/pred/pred_{llm}_parallel.txt', 'r', encoding='utf-8') as file:
    content = file.readlines()

extracted_query = [extract_sql(q, llm) for q in extract_sql_from_text("\n".join(content))]
with open(proj_dir + f'/bird/pred/final_pred/{llm}_out_post.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(extracted_query))

import os

os.system(f'python G:/AutoTask/SQL_benchmark/data/BIRD-SQL/DAMO-ConvAI/bird/llm/src/evaluation.py '
          f'--db_root_path G:/AutoTask/SQL_benchmark/data/BIRD-SQL/DAMO-ConvAI/bird/llm/data/dev/dev_databases/ '
          f'--predicted_sql_path {proj_dir}/bird/pred/final_pred/{llm}_out_post.txt '
          f'--ground_truth_path G:/AutoTask/SQL_benchmark/data/BIRD-SQL/DAMO-ConvAI/bird/llm/data/dev/ '
          f'--diff_json_path G:/AutoTask/SQL_benchmark/data/BIRD-SQL/DAMO-ConvAI/bird/llm/data/dev/dev.json')