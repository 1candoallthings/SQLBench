# import debugpy; debugpy.connect(('127.0.0.1', 5688))
import json
import sqlite3
import os
import os.path as osp
from tqdm import tqdm
import argparse
import time
import threading
import signal
import re
from llms.gpt import GPT
import itertools
from sql_metadata import Parser

proj_dir = osp.dirname(osp.dirname(osp.abspath(__file__)))



class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Function execution time exceeded")

def run_with_timeout(func, timeout, *args, **kwargs):
    # 设置超时时间
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)  # 设置超时时间为 timeout 秒

    try:
        result = func(*args, **kwargs)  # 执行函数
        signal.alarm(0)  # 成功执行后关闭定时器
        return result
    except TimeoutException:
        return None, None
    finally:
        signal.alarm(0)  # 确保超时定时器在函数执行后被关闭


def execute_query(db_path, query):
    result_set, error = None, None
    query_finished = threading.Event()

    def query_thread():
        nonlocal result_set, error
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            # result_set = set(result)
            result_set = set(itertools.chain.from_iterable(result))  # 0816针对debug性能太低的修改
            conn.close()
        except Exception as e:
            # print('执行sql时发生DBMS汇报的error:', str(e))
            result_set, error = None, "sqlite3.OperationalError: " + str(e)

        finally:
            query_finished.set()  # Notify that the query has finished

    # Start the query in a separate thread
    thread = threading.Thread(target=query_thread)
    thread.start()

    # Wait for the query to complete or timeout after 3 seconds
    query_finished.wait(timeout=3)

    if not query_finished.is_set():
        print("Query execution timed out.")
        result_set, error = None, 'Query execution timed out.'

    return result_set, error


def parse_join_condition(sql_query):
    '''
    输出：['driverStandings.raceId = races.raceId', 'drivers.driverId = driverStandings.driverId']
    '''

    # Step 1: 分词处理
    tokens = sql_query.split()

    # Step 2: 捕获表别名
    alias_map = {}
    for i, token in enumerate(tokens):
        if token.lower() == 'as':
            table_name = tokens[i - 1]
            alias_name = tokens[i + 1]
            alias_map[alias_name] = table_name

    # Step 3: 查找所有ON后面的三个token
    on_conditions = []
    for i, token in enumerate(tokens):
        if token.lower() == 'on':
            # 获取ON后面的三个token
            three_tokens = tokens[i + 1: i + 4]
            # 替换这些token中的别名
            for j in range(len(three_tokens)):
                for alias, table in alias_map.items():
                    three_tokens[j] = three_tokens[j].replace(alias + ".", table + ".")
            # 将处理后的条件加入列表
            on_conditions.append(' '.join(three_tokens))
    
    return on_conditions


def judge_condition_or_dataProcessing_error_by_gpt(question, pred_sql, gold_sql, args):
    prompt = \
    f"""You are an expert in SQL queries. Please choose the error category for incorrect SQL queries based on the Question and the correct SQL query.
    Output the chosen error category from the following choices only, without any explanation.
1. Condition Filter Error: Incorrect filtering of conditions.
2. Data Processing Error: The condition is filtered correctly, but the data processing is wrong. Note that the premise of this error is that the conditional filtering is correct.

Question: {question}
Correct SQL Query: {gold_sql}
Wrong SQL Query: {pred_sql}
"""
    llm = GPT(args.judge_model)
    content, info = llm(prompt)
    # print("gpt对error的judgement:\n", content)

    if 'condition filter error' in content.lower():
        return "Condition Filter Error"
    elif 'data processing error' in content.lower():
        return "Data Processing Error"
    else:
        print('warning: gpt的输出没有被捕获到！')
        return "Condition Filter Error"
    


def parse_error_type(pred_sql, gold_sql, id, sc_data):
    error_type = []

    # 选择sc_data中对应id的数据
    entry = next(item for item in sc_data if item["id"] == id)
    gt_table = entry["gt_table"]
    gold_linked_columns = entry["gold_linked_columns"]

    # 转换为小写以忽略大小写差异
    pred_sql_lower = pred_sql.lower()

    # 比较表
    # pred_tables = set()
    # for table in gt_table:  # (已经解决)这个in的范围不对！直接改用Parse库
    #     if table.lower() in pred_sql_lower:  
    #         pred_tables.add(table.lower())

    pred_tables = set(
        Parser(pred_sql.lower()).tables
    )

    gt_tables = set([table.lower() for table in gt_table])

    # step1. 检查表是否正确
    if pred_tables == gt_tables:
        error_type.append("Table Query Correct")
    else:
        # print('pred_tables:', pred_tables)
        # print('gt_tables:', gt_tables)
        error_type.append("Table Query Error")

        if gt_tables.issubset(pred_tables):
            error_type.append("Excessive Tables")
        elif pred_tables.issubset(gt_tables):
            error_type.append("Missing Tables")
        else:
            error_type.append("Incorrect Tables")
        return error_type  # 如果表错误直接返回

    # 比较列
    # pred_columns = set()
    # for _, column in gold_linked_columns:  # 这个in的范围不对！
    #     if column.lower() in pred_sql_lower:
    #         pred_columns.add(column.lower())

    try:
        pred_columns = set(
            Parser(pred_sql.lower()).columns  # it works
        )
    except:
        print('------------\nwarning: column can not be parsed. set pred_columns to dummy set.\npred_sql:', pred_sql)
        pred_columns = set()

    gt_columns = set([column.lower() for _, column in gold_linked_columns])

    # step2. 检查列是否正确
    if pred_columns == gt_columns:
        error_type.append("Column Selection Correct")
    else:
        # print('pred_columns:', pred_columns)
        # print('gt_columns:', gt_columns)
        error_type.append("Column Selection Error")

        if gt_columns.issubset(pred_columns):
            error_type.append("Excessive Columns")
        elif pred_columns.issubset(gt_columns):
            error_type.append("Missing Columns")
        else:
            error_type.append("Incorrect Columns")
        return error_type  # 如果列错误直接返回

    # step3. 检查join error
    pred_join = set(parse_join_condition(pred_sql.lower()))
    gold_join = set(parse_join_condition(gold_sql.lower()))

    # print('pred_join:', pred_join)
    # print('gold_join:', gold_join)
    if pred_join == gold_join:
        error_type.append("Join Columns Correct")
    else:
        error_type.append("Join Columns Error")
        return error_type  # 如果join error直接返回

    # 用chatgpt判断是condition error还是data processing error
    error_type.append(
        judge_condition_or_dataProcessing_error_by_gpt(entry["new_question"], pred_sql, gold_sql, args)
    )

    return error_type




def get_error_comments(entry):

    def parse_comment_for_execute_error(error_type):
        if error_type[0] == "Table Query Error":
            if error_type[1] == "Excessive Tables":
                comment = "The tables you inquired about are incorrect, you query too many tables."
            elif error_type[1] == "Missing Tables":
                comment = "The tables you inquired about are incorrect, you need to query more tables."
            elif error_type[1] == "Incorrect Tables":
                comment = "The tables you inquired about are incorrect."
        elif error_type[1] == "Column Selection Error":
            if error_type[2] == "Excessive Columns":
                comment = "You have found the correct tables. But you selected too many columns."
            elif error_type[2] == "Missing Columns":
                comment = "You have found the correct tables. But you need to select more columns."
            elif error_type[2] == "Incorrect Columns":
                comment = "You have found the correct tables. But you selected the wrong columns."
        elif error_type[2] == "Join Columns Error":
            comment = "You have found the correct tables. You selected the correct columns. But you combined the wrong rows when JOINing two tables."
        elif error_type[3] == "Condition Filter Error":
            comment = "You have found the correct tables. You selected the correct columns. You combined (JOIN) the correct tables. But an error occurred in the conditional filter."
        elif error_type[3] == "Data Processing Error":
            comment = "You have found the correct tables. You selected the correct columns. You combined (JOIN) the correct tables. You used the correct conditional filtering. But there was an error in your processing of the data."
        else:
            comment = "Warning: Unknown error type."
        return comment

    if entry["error_info"].startswith('sqlite3.OperationalError'):
        comment = entry["error_info"]
    else:
        assert entry["error_info"] == "execute error"            
        comment = parse_comment_for_execute_error(entry["error_type"])

    return comment



def get_accuracy(dir_gold_json, dir_pred_json, db_path, dir_dataset_json, args):
    sc_file_path = '/data1/yyx/text2sql/SQLBench/dataset/bigtable_with_gt_columns(schema_linking).json'  # hard_code
    with open(dir_gold_json, 'r') as gold_file, open(dir_pred_json, 'r') as pred_file, open(dir_dataset_json, 'r') as json_file, open(sc_file_path, 'r') as sc_file:
        gold_data = json.load(gold_file)
        pred_data = json.load(pred_file)
        bigtable_dataset = json.load(json_file)
        sc_data = json.load(sc_file)

    correct_count = 0
    total_count = len(pred_data)
    debug_dataset = []

    # 创建gold_data字典，以便通过id快速查找gold_sql和gold_db
    gold_dict = {entry['id']: (entry['sql'], entry['db_id']) for entry in gold_data}

    for i, pred_entry in tqdm(enumerate(pred_data), desc='evaluate', total=total_count):
        pred_id = pred_entry['id']

        # 应对不好的指令跟随
        pred_sql = pred_entry['sql']
        pred_sql = pred_sql.replace('```sql', '').replace('```', '').replace('\n', ' ').strip()

        # 使用pred_id查找对应的gold_sql和gold_db
        if pred_id in gold_dict:
            gold_sql, gold_db = gold_dict[pred_id]
        else:
            print(f"Warning: No matching gold data found for id {pred_id}")
            continue

        db_file_path = os.path.join(db_path, gold_db, f"{gold_db}.sqlite")

        # Get results for gold and predicted SQL with a timeout of 3 seconds
        gold_result, _ = run_with_timeout(execute_query, 3, db_file_path, gold_sql)
        pred_result, sqlite_error_info = run_with_timeout(execute_query, 3, db_file_path, pred_sql)

        # Compare results
        if gold_result is not None and pred_result is not None and gold_result == pred_result:
            correct_count += 1
            # print(f"Correct Id: {pred_id}", "SQL:", pred_sql)  # 人工检查debug
        else:
            if args.prepare_debug_dataset:
                # Update JSON entry with error_sql and error_info
                if sqlite_error_info:
                    bigtable_dataset[i]["error_sql"] = pred_sql
                    bigtable_dataset[i]["error_info"] = sqlite_error_info
                    bigtable_dataset[i]["error_type"] = None
                else:
                    bigtable_dataset[i]["error_sql"] = pred_sql
                    bigtable_dataset[i]["error_info"] = "execute error"
                    # 人工解析错误，并填充error_type
                    bigtable_dataset[i]["error_type"] = parse_error_type(pred_sql, gold_sql, str(i), sc_data)

                bigtable_dataset[i]["error_comments"] = get_error_comments(bigtable_dataset[i])
                
            debug_dataset.append(bigtable_dataset[i])

    # Save debug dataset
    if args.prepare_debug_dataset:
        os.makedirs(osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql_debug'), exist_ok=True)
        with open(osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql_debug/bigtable_sqldebug_dataset.json'), 'w') as json_file:
            json.dump(debug_dataset, json_file, indent=4)

    accuracy = correct_count / total_count if total_count > 0 else 0
    print(f"Correct count: {correct_count}, Total count: {total_count}, Accuracy: {accuracy:.2%}")
    return accuracy

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='toy')
    parser.add_argument('--model', type=str)
    parser.add_argument('--judge_model', type=str)
    parser.add_argument('--db_path', type=str, help='Path to the BIRD database directory')
    parser.add_argument('--prepare_debug_dataset', action='store_true')
    parser.add_argument('--eval_debugged_sql', action='store_true')

    args = parser.parse_args()

    if args.eval_debugged_sql:
        get_accuracy(
            dir_gold_json=osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/gold.json'),
            dir_pred_json=osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/sql_debug/debugged_sql.json'),
            db_path=args.db_path,
            dir_dataset_json=osp.join(proj_dir, f'dataset/{args.dataset}/bigtable_dataset.json'),
            args=args
        )
    else:
        get_accuracy(
            dir_gold_json=osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/gold.json'),
            dir_pred_json=osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/pred.json'),
            db_path=args.db_path,
            dir_dataset_json=osp.join(proj_dir, f'dataset/{args.dataset}/bigtable_dataset.json'),
            args=args
        )