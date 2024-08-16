#!/bin/sh

DATASET=bigtable_dataset
MODEL=gpt-3.5-turbo
DB_PATH=/data1/yyx/text2sql/CodeS/data/sft_data_collections/bird/dev/dev_databases

# # step1.1 SQL Generation
# python sql_generation.py --dataset $DATASET --model $MODEL

# step1.2 eval and generate SQL Debugging Dataset
python eval.py --dataset $DATASET --model $MODEL \
 --db_path $DB_PATH \
 --prepare_debug_dataset --judge_model gpt-3.5-turbo

# # step2.1 SQL Debugging
python sql_debug.py --dataset $DATASET --model $MODEL  # 改好了bug，冲！

# # # step2.2 eval the debugged sql
python eval.py --dataset $DATASET --model $MODEL \
 --db_path $DB_PATH \
 --eval_debugged_sql

# # step3 SQL optimization
# python sql_optimization.py --dataset $DATASET --model $MODEL --db_path $DB_PATH

# # step4 sql2text
# python sql2text.py --dataset $DATASET --model $MODEL --eval_model gpt-3.5-turbo

# # step5 schema linking
# python schema_linking.py --dataset $DATASET --model $MODEL