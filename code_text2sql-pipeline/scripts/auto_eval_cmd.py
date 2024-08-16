# coding=utf-8

import argparse
import os
import datetime
import logging

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auto_eval import eval_text2sql_once

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser()

# 添加命令行选项
parser.add_argument("--input_data", type=str, default="results.json")
parser.add_argument("--target_name", type=str, default="sql")

# 解析命令行参数
args = parser.parse_args()
output_dir = os.path.dirname(args.input_data)

t_start=datetime.datetime.now()
eval_text2sql_once(args.input_data,target_name=args.target_name,output_dir=output_dir)
t_end=datetime.datetime.now()

print(f"End evaluating. Time consumed: {(t_end-t_start).total_seconds()}s")