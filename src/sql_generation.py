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

def convert_txt_to_json(pred_txt_path, pred_json_path, gold_txt_path, gold_json_path):
    pred_data = []
    gold_data = []

    # 处理pred.txt文件
    with open(pred_txt_path, 'r', encoding='utf-8') as pred_file:
        for idx, line in enumerate(pred_file):
            sql = line.strip()
            pred_data.append({
                "id": str(idx),  # 使用索引作为id
                "sql": sql
            })
    # 将pred数据写入pred.json文件
    with open(pred_json_path, 'w', encoding='utf-8') as pred_json_file:
        json.dump(pred_data, pred_json_file, ensure_ascii=False, indent=4)

    # 处理gold.txt文件
    with open(gold_txt_path, 'r', encoding='utf-8') as gold_file:
        for idx, line in enumerate(gold_file):
            # 假设格式为 `new_query\t db_id`
            parts = line.strip().split('\t')
            assert len(parts) == 2, f"Invalid line: {line}"
            new_query, db_id = parts
            gold_data.append({
                "id": str(idx),  # 使用索引作为id
                "sql": new_query,
                "db_id": db_id
            })
    # 将gold数据写入gold.json文件
    with open(gold_json_path, 'w', encoding='utf-8') as gold_json_file:
        json.dump(gold_data, gold_json_file, ensure_ascii=False, indent=4)


def text2sql(args):

    with open(osp.join(proj_dir, f'dataset/{args.dataset}/bigtable_dataset.json'), 'r', encoding='utf-8') as file:
        data = json.load(file)

    llm = GPT(args.model)

    os.makedirs(osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}'), exist_ok=True)

    jsonl_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/token_info.jsonl')
    pred_txt_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/pred.txt')
    gold_txt_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/gold.txt')

    if args.start_idx == 0:
        if osp.exists(pred_txt_path) or osp.exists(gold_txt_path):
            print('请先删除之前生成的txt文件')
            sys.exit(1)
    else:
        print(f'之前预测了一部分，从{args.start_idx}开始继续预测')

    with open(jsonl_path, 'a', encoding='utf-8') as jsonl_file, \
        open(pred_txt_path, 'a', encoding='utf-8') as pred_file, \
        open(gold_txt_path, 'a', encoding='utf-8') as gold_file:

        # 遍历JSON中的数据并填入prompt模板
        for idx, entry in enumerate(tqdm(data, desc='text2sql')):
            if idx < args.start_idx: continue

            prompt = f'''### Answer the question by sqlite SQL query only and with no explanation.
### Sqlite SQL tables, with their properties:
#\n{entry['simplified_ddl']}#\n### {entry['new_question']}\n### SQL: '''
            
            pred_sql, info = llm(prompt)

            # 应对不好的指令跟随
            pred_sql = pred_sql.replace('```sql', '').replace('```', '').replace('\n', ' ').strip()

            # 将生成的SQL和gold SQL添加到文件中
            pred_file.write(pred_sql + '\n')
            gold_file.write(f"{entry['new_query']}\t{entry['db_id']}\n")

            # 生成仅包含"id"和token信息的JSON对象
            token_info = {
                "id": entry['id'],
                "input_token": info['input_token'],
                "output_token": info['output_token'],
                "total_token": info['total_token']
            }
            # 写入JSONL文件，每行一个JSON对象
            jsonl_file.write(json.dumps(token_info, ensure_ascii=False) + '\n')

    convert_txt_to_json(pred_txt_path, pred_txt_path.replace('.txt', '.json'), gold_txt_path, gold_txt_path.replace('.txt', '.json'))
    

def get_accuracy(dir_gold_sql, dir_pred_sql, db_path):
    '''使用斌哥给的evaluation_suite. 目前有无法处理`这个字符的bug'''
    cmd_str = f"""
    python /data1/yyx/text2sql/SQLBench_Supplementary_Material/code_text2sql-pipeline/utils/evaluation.py --gold {dir_gold_sql} --pred {dir_pred_sql} --db {db_path} --etype exec
    """
    result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
    acc = float([ans for ans in result.stdout.split('\n')[-2].split(' ') if ans][-1])

    return acc


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='toy')
    parser.add_argument('--model', type=str)
    parser.add_argument('--start_idx', type=int, default=0)

    args = parser.parse_args()
    text2sql(args)

    # # just a hack
    # convert_txt_to_json(
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/bigtable_dataset-gpt-3.5-turbo/pred.txt', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/bigtable_dataset-gpt-3.5-turbo/pred.json', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/bigtable_dataset-gpt-3.5-turbo/gold.txt', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/bigtable_dataset-gpt-3.5-turbo/gold.json',
    # )

    # convert_txt_to_json(
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/bigtable_dataset-gpt-4-turbo/pred.txt', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/bigtable_dataset-gpt-4-turbo/pred.json', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/bigtable_dataset-gpt-4-turbo/gold.txt', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/bigtable_dataset-gpt-4-turbo/gold.json',
    # )

    # convert_txt_to_json(
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/toy-gpt-3.5-turbo/pred.txt', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/toy-gpt-3.5-turbo/pred.json', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/toy-gpt-3.5-turbo/gold.txt', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/toy-gpt-3.5-turbo/gold.json',
    # )

    # convert_txt_to_json(
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/toy-gpt-4-turbo/pred.txt', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/toy-gpt-4-turbo/pred.json', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/toy-gpt-4-turbo/gold.txt', 
    #     '/data1/yyx/text2sql/SQLBench/src/text2sql_results/toy-gpt-4-turbo/gold.json',
    # )

