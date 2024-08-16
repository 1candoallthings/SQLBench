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


#             prompt = f"""<Instruction>
# You are an expert in database analysis and processing of SQL statements.
# I will provide an SQL statement and relevant evidence. You need to help me analyze what problem this SQL statement is solving.
# Here are some reference cases:
# SQL: SELECT list_id FROM lists_users WHERE user_id = 85981819 ORDER BY list_creation_date_utc ASC LIMIT 1
# question: What is the list ID that was first created by user 85981819?
# SQL: SELECT COUNT (T2.user_id) FROM movies AS T1 INNER JOIN ratings AS T2 ON T1.movie_id = T2.movie_id WHERE T1.movie_title = 'Pavee Lackeen: The Traveller Girl' AND T2.rating_score = 4
# question: How many users gave \"Pavee Lackeen: The Traveller Girl\" movie a rating score of 4?
# Please answer strictly in the following format and do not change the format arbitrarily:
# question: This is a problem description.
# </Instruction>
# <SQL>{gold_sql}</SQL>
# """    



def eval_sql2text(args):
   
    llm = GPT(args.eval_model)
    print(f'Loading model {args.eval_model} for evaluation...')
    
    # 输入与输出文件路径
    pred_question_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql2text/pred_question.jsonl')
    eval_result_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql2text/pred_question_with_eval.json')

    # 打开JSONL文件进行处理
    with open(pred_question_path, 'r', encoding='utf-8') as file:
        pred_questions = [json.loads(line) for line in file]

    eval_results = []
    correct_count1, correct_count2, total_count = 0, 0, len(pred_questions)

    # 遍历每个条目，生成判断并将结果存储
    for entry in tqdm(pred_questions, total=len(pred_questions), desc='Evaluating SQL2Text'):
        pred_question, gold_question = entry['pred_question'], entry['gold_question']
        
        prompt1 = f"""Determine whether the following two sentences ask the same question and whether their corresponding answers are the same.
sentences1: {gold_question}
sentences2: {pred_question}
Just output True or False, do not output anything else.
"""
        eval_result1, _ = llm(prompt1)

        prompt2 = f"""Determine whether the following two sentences ask the same question and whether their corresponding answers are the same.
sentences1: {pred_question}
sentences2: {gold_question}
Just output True or False, do not output anything else.
"""
        eval_result2, _ = llm(prompt2)
        
        # 将判断结果添加到entry中，并加入eval_results列表
        entry['eval_result1'] = eval_result1.strip()
        entry['eval_result2'] = eval_result2.strip()
        if 'true' in entry['eval_result1'].lower():
            correct_count1 += 1
        if 'true' in entry['eval_result2'].lower():
            correct_count2 += 1
        
        eval_results.append(entry)

    # 将带有判断结果的新列表写入JSON文件
    with open(eval_result_path, 'w', encoding='utf-8') as eval_file:
        eval_file.write(json.dumps(eval_results, ensure_ascii=False))

    accuracy1 = correct_count1 / total_count if total_count > 0 else 0
    accuracy2 = correct_count2 / total_count if total_count > 0 else 0
    print(f"Correct count1: {correct_count1}, Total count: {total_count}, Accuracy: {accuracy1:.2%}")
    print(f"Correct count2: {correct_count2}, Total count: {total_count}, Accuracy: {accuracy2:.2%}")


def sql2text(args):

    with open(osp.join(proj_dir, f'dataset/{args.dataset}/bigtable_dataset.json'), 'r', encoding='utf-8') as file:
        data = json.load(file)

    llm = GPT(args.model)
    print(f'Loading model {args.model} for SQL2Text...')

    os.makedirs(osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql2text'), exist_ok=True)

    jsonl_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql2text/token_info.jsonl')
    sql2text_result_path = osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql2text/pred_question.jsonl')

    if osp.exists(sql2text_result_path):
        print('请先删除之前生成的jsonl文件')
        sys.exit(1)

    with open(jsonl_path, 'a', encoding='utf-8') as jsonl_file, \
        open(sql2text_result_path, 'a', encoding='utf-8') as result_file:

        for idx, entry in tqdm(enumerate(data), total=len(data), desc='SQL2Text'):

            gold_sql = entry['new_query']
            gold_question = entry['new_question']
            prompt = f"""
You are an expert in database analysis and processing of SQL statements.
I will provide an SQL statement and relevant evidence. You need to help me analyze what problem this SQL statement is solving.
Here are some reference cases:
SQL: SELECT list_id FROM lists_users WHERE user_id = 85981819 ORDER BY list_creation_date_utc ASC LIMIT 1
question: What is the list ID that was first created by user 85981819?
SQL: SELECT COUNT (T2.user_id) FROM movies AS T1 INNER JOIN ratings AS T2 ON T1.movie_id = T2.movie_id WHERE T1.movie_title = 'Pavee Lackeen: The Traveller Girl' AND T2.rating_score = 4
question: How many users gave \"Pavee Lackeen: The Traveller Girl\" movie a rating score of 4?
Please answer without any explanation:
SQL: {gold_sql}
question:
"""         
            pred_question, info = llm(prompt)

            # 生成仅包含"id"和token信息的JSON对象
            token_info = {
                "id": entry['id'],
                "input_token": info['input_token'],
                "output_token": info['output_token'],
                "total_token": info['total_token']
            }
            # 写入JSONL文件，每行一个JSON对象
            jsonl_file.write(json.dumps(token_info, ensure_ascii=False) + '\n')
            # 将生成的问题和索引也追加到result_file中
            result_file.write(json.dumps({"id": str(idx), "pred_question": pred_question, "gold_question": gold_question}, ensure_ascii=False) + '\n')



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='toy')
    parser.add_argument('--model', type=str)
    parser.add_argument('--eval_model', type=str)

    args = parser.parse_args()
    sql2text(args)
    eval_sql2text(args)