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

proj_dir = osp.dirname(osp.dirname(osp.abspath(__file__)))

def calculate_RES(gt_tables, linked_tables):
    # 确保输入是集合类型
    gt_tables = set(gt_tables)
    linked_tables = set(linked_tables)
    
    # 计算1(T_n, T_hat_n)
    if gt_tables.issubset(linked_tables):
        indicator = 1
    else:
        indicator = 0
    
    # 计算R(T_n, T_hat_n)
    if len(linked_tables) > 0:  # 防止除零错误
        r_value = np.sqrt(len(gt_tables) / len(linked_tables))
    else:
        r_value = 0
    
    # RES = 1(T_n, T_hat_n) * R(T_n, T_hat_n)
    RES = indicator * r_value
    
    return RES


def extract_tab_from_sql(sql, ddl):   

    ele_query = " ".join([i for i in re.split(r'[^\w\s*]', sql)]).split()
    ele_query = [i.lower() for i in ele_query]
    split_ddl = ddl.split(";\n")
    linked_tables = []
    all_tables = []
    for it in split_ddl:
        all_tables.append(it[2:it.index('(')])
    for one_table in all_tables:
        one_table = one_table.lower()
        if one_table in ele_query:
            linked_tables.append(one_table)

    return linked_tables



def schema_linking(args):

    # step1. 读取sql generation时生成的pred_sql作为presql
    with open(osp.join(proj_dir, f'src/text2sql_results/{args.dataset}-{args.model}/pred.json'), 'r', encoding='utf-8') as file:
        pred_data = json.load(file)    
    with open(osp.join(proj_dir, f'dataset/{args.dataset}/bigtable_dataset.json'), 'r', encoding='utf-8') as file:
        bigtable_dataset = json.load(file)
    with open('/data1/yyx/text2sql/SQLBench/dataset/bigtable_with_gt_columns(schema_linking).json', 'r', encoding='utf-8') as file:  # hard-code
        sc_data = json.load(file)

    average_RES = 0
    for entry in pred_data:
        id = int(entry['id'])
        pred_sql = entry['sql']
        gt_tables = sc_data[id]["gt_table"]
        # linked_tables = extract_tab_from_sql(pred_sql, bigtable_dataset[id]['simplified_ddl'])
        try:
            linked_tables = Parser(pred_sql).tables
        except:
            print(f"Error: {pred_sql}")
            linked_tables = []

        RES_value = calculate_RES(gt_tables, linked_tables)
        average_RES += RES_value
        
    average_RES /= len(pred_data)
    print(f"Average RES: {average_RES}")

        


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='bigtable_dataset')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo')

    args = parser.parse_args()
    schema_linking(args)
