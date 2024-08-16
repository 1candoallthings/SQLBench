import os
proj_dir = os.path.dirname(__file__)
os.system(f'python G:/AutoTask/text2sql/test-suite-sql-eval-master/evaluation.py '
          f'--gold G:/AutoTask/text2sql-dev/exams/official_demo/gold_example.txt '
          f'--pred {proj_dir}/spider/pred/final_pred/llama2_out_post01.txt '
          f'--db G:/AutoTask/SQL_benchmark/data/Spider/spider/database/ '
          f'--etype exec')