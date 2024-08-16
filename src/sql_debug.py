# import debugpy; debugpy.connect(('127.0.0.1', 5688))
import json
import sys
import os
import os.path as osp
from llms.gpt import GPT
import subprocess
from tqdm import tqdm
import argparse

proj_dir = osp.dirname(osp.dirname(osp.abspath(__file__)))


def convert_txt_to_json(pred_txt_path, pred_json_path):
    pred_data = []

    # 处理pred.txt文件
    with open(pred_txt_path, 'r', encoding='utf-8') as pred_file:
        for idx, line in enumerate(pred_file):
            parts = line.strip().split('\t')
            assert len(parts) == 2, f"Invalid line: {line}"
            sql, id = parts
            pred_data.append({
                "id": id, 
                "sql": sql
            })
    # 将pred数据写入pred.json文件
    with open(pred_json_path, 'w', encoding='utf-8') as pred_json_file:
        json.dump(pred_data, pred_json_file, ensure_ascii=False, indent=4)


def sql_debug(debug_data_path, args):
    # Read JSON data from the file
    with open(debug_data_path, 'r', encoding='utf-8') as f:
        debug_data = json.load(f)
    
    llm = GPT(args.model)

    jsonl_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql_debug/token_info.jsonl')
    pred_txt_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql_debug/debugged_sql.txt')
    
    if args.start_idx == 0:
        if osp.exists(pred_txt_path):
            print('请先删除之前生成的txt文件')
            sys.exit(1)
    else:
        print(f'之前预测了一部分，从{args.start_idx}开始继续预测')

    with open(jsonl_path, 'a', encoding='utf-8') as jsonl_file, \
        open(pred_txt_path, 'a', encoding='utf-8') as pred_file:

        for idx, entry in enumerate(tqdm(debug_data, desc='sql_debug')):
            if idx < args.start_idx: continue

# bad instruction following, especially for GPT4
#             prompt = f"""
# ### Write the correct SQLite SQL Query corresponding to the Question based on the database, the Wrong SQL Query and the cause of the error.
# ### Sqlite SQL tables, with their properties:
# #
# # {entry['simplified_ddl']}
# #
# ### Question: {entry['new_question']}
# ### Wrong SQL Query:
# {entry['error_sql']}
# ### Error Information:
# {entry['error_comments']}
# ### Correct SQL: """
            prompt = f"""
### Write the correct SQLite SQL Query given the wrong Query, without any explanation.
### Properties of Sqlite SQL tables:
#
# {entry['simplified_ddl']}
#
### Question: {entry['new_question']}
### Wrong SQL Query:
{entry['error_sql']}
### Error Information:
{entry['error_comments']}
### Correct SQL: """
            
            debugged_sql, info = llm(prompt)
            # 应对不好的指令跟随
            debugged_sql = debugged_sql.replace('```sql', '').replace('```', '').replace('\n', ' ').strip()
            pred_file.write(f"{debugged_sql}\t{entry['id']}\n")  # 把所属的问题id也写入pred.txt  

            # 生成仅包含"id"和token信息的JSON对象
            token_info = {
                "id": entry['id'],
                "input_token": info['input_token'],
                "output_token": info['output_token'],
                "total_token": info['total_token']
            }
            # 写入JSONL文件，每行一个JSON对象
            jsonl_file.write(json.dumps(token_info, ensure_ascii=False) + '\n')
    
    convert_txt_to_json(pred_txt_path, pred_txt_path.replace('.txt', '.json'))
        
    



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='bigtable_dataset')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo')
    parser.add_argument('--start_idx', type=int, default=0)
    
    args = parser.parse_args()
    
    sql_debug(
        osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql_debug/bigtable_sqldebug_dataset.json'),
        args
    )

