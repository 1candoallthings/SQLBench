# import debugpy; debugpy.connect(('127.0.0.1', 5688))
import re
import json
import sys
import os
import os.path as osp
from llms.gpt import GPT
import subprocess
from tqdm import tqdm
import argparse
from sql_metadata import Parser
import numpy as np
import time
from eval import execute_query, run_with_timeout

proj_dir = osp.dirname(osp.dirname(osp.abspath(__file__)))


def check_and_report_performance(opted_jsonl_path, bigtable_data_path, db_path):
    with open(bigtable_data_path, 'r', encoding='utf-8') as file:
        bigtable_dataset = json.load(file)

    with open(opted_jsonl_path, 'r', encoding='utf-8') as file:
        correct_count = 0
        average_CVES = 0
        for line in file:
            entry = json.loads(line.strip())
            pred_sql = entry['pred_sql']
            opted_sql = entry['sql']

            gold_db = bigtable_dataset[int(entry['id'])]['db_id']
            db_file_path = os.path.join(db_path, gold_db, f"{gold_db}.sqlite")
            
            # 执行pred_sql
            start_time = time.time()
            pred_result, pred_error = run_with_timeout(execute_query, 3, db_file_path, pred_sql)
            pred_time = time.time() - start_time if pred_error is None else None

            # 执行opted_sql
            start_time = time.time()
            opted_result, opted_error = run_with_timeout(execute_query, 3, db_file_path, opted_sql)
            opted_time = time.time() - start_time if opted_error is None else None

            # 判断结果是否一致
            if pred_result is not None and opted_result is not None and pred_result == opted_result:
                correct_count += 1

                print(f"Results are consistent for id {entry['id']}.")
                if pred_time is not None:
                    print(f"Execution time for pred_sql: {pred_time:.4f} seconds.")
                if opted_time is not None:
                    print(f"Execution time for opted_sql: {opted_time:.4f} seconds.")

                average_CVES += np.sqrt(pred_time / opted_time)
            else:
                print(f"Results differ or an error occurred for id {entry['id']}.")
                if pred_error:
                    print(f"Error in pred_sql execution: {pred_error}")
                if opted_error:
                    print(f"Error in opted_sql execution: {opted_error}")
        
        print(f"Correct count: {correct_count}")
        print(f"Average CVES: {average_CVES / correct_count}")

                
            



def eval_CVES():
    # 读取sql_optimization路径下生成的optimized_sql

    # 参考schema_linking.py中统计RES的for循环框架
    pass

def sql_optimization(args):

    # step1. 读取pred sql，并且参考debug_dataset，选择pred sql为执行正确的集合
    with open(osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/pred.json'), 'r', encoding='utf-8') as file:
        pred_data = json.load(file)    
    with open(osp.join(proj_dir, f'dataset/{args.dataset}/bigtable_dataset.json'), 'r', encoding='utf-8') as file:
        bigtable_dataset = json.load(file)
    with open(osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql_debug/bigtable_sqldebug_dataset.json'), 'r', encoding='utf-8') as file:
        debug_dataset = json.load(file)

    # 筛选那些不在debug_dataset中的id
    correct_id = [idx for idx in range(len(pred_data)) if str(idx) not in [entry['id'] for entry in debug_dataset]]
    print('len(correct_id):', len(correct_id))

    jsonl_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql_optimization/token_info.jsonl')
    opted_jsonl_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql_optimization/opted_sql.jsonl')
    os.makedirs(osp.dirname(opted_jsonl_path), exist_ok=True)

    llm = GPT(args.model)
    
    # if osp.exists(opted_jsonl_path):
    #     print('请先删除之前生成的jsonl文件')
    #     sys.exit(1)

    with open(jsonl_path, 'a', encoding='utf-8') as jsonl_file, \
        open(opted_jsonl_path, 'a', encoding='utf-8') as opted_jsonl_file:

        for entry in tqdm(pred_data, desc='SQL optimization'):
            if int(entry['id']) not in correct_id: 
                continue

            bigtable_entry = bigtable_dataset[int(entry['id'])]
#             prompt = f"""
# ### Rewrite and optimize the given SQL query to improve SQL query efficiency and minimize SQL execution time while ensuring correctness. Only output SQL query, do not output any other content.
# ### Here are some reference cases:

# # Question: List out the age of users who are located in Vienna, Austria and obtained the badge.
# # SQL Query: SELECT Age FROM users WHERE Location = 'Vienna, Austria' AND Id IN (SELECT UserId FROM badges)
# # New SQL Query: SELECT u.Age FROM users AS u INNER JOIN badges AS b ON u.Id = b.UserId WHERE u.Location = 'Vienna, Austria'
# # Explanation: By applying a JOIN operation instead of a subquery with IN, efficiency can be improved, as the database may execute the JOIN and filtering processes concurrently in just one operation without the need to store the intermediate results to filter the primary query.

# ### Sqlite SQL tables, with their properties:
# {bigtable_entry['simplified_ddl']}
# ### Question: {bigtable_entry['new_question']}
# ### SQL Query: {entry['sql']}
# ### New SQL Query:
# """

            prompt = f'''### Answer the question by sqlite SQL query only and with no explanation. You must minimize SQL execution time while ensuring correctness.
### Sqlite SQL tables, with their properties:
#\n{bigtable_entry['simplified_ddl']}#\n### {bigtable_entry['new_question']}\n### SQL: '''

            opted_sql, info = llm(prompt)
            # 应对不好的指令跟随
            opted_sql = opted_sql.replace('```sql', '').replace('```', '').replace('\n', ' ').strip()
            # 生成仅包含"id"和token信息的JSON对象
            token_info = {
                "id": entry['id'],
                "input_token": info['input_token'],
                "output_token": info['output_token'],
                "total_token": info['total_token']
            }
            # 写入JSONL文件，每行一个JSON对象
            jsonl_file.write(json.dumps(token_info, ensure_ascii=False) + '\n')
            # 写入结果
            opted_jsonl_file.write(json.dumps({"id": entry['id'], "pred_sql": entry['sql'], "sql": opted_sql}, ensure_ascii=False) + '\n')




if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='bigtable_dataset')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo')
    parser.add_argument('--db_path', type=str, default='/data1/yyx/text2sql/CodeS/data/sft_data_collections/bird/dev/dev_databases')
    
    args = parser.parse_args()

    sql_optimization(args) 
    check_and_report_performance(
        osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql_optimization/opted_sql.jsonl'),
        osp.join(proj_dir, f'dataset/{args.dataset}/bigtable_dataset.json'),
        args.db_path
    )
