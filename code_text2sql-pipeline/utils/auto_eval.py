import json
import subprocess
import os, sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from settings import root_path,DATABASE_PATH
from tqdm import tqdm


def generate_sql_gold_pred_files(db_ids,gold_sqls,predicted_sqls,output_dir):

    dir_gold_sql=os.path.join(output_dir,'gold_sql.txt')
    dir_pred_sql=os.path.join(output_dir,'pred_sql.txt')

    with open(dir_gold_sql, 'w') as f1:
        f1.write("\n".join([gold_sql + "\t" + db_id for db_id, gold_sql in zip(db_ids,gold_sqls)]))

    with open(dir_pred_sql, 'w') as f2:
        f2.write("\n".join(predicted_sqls))

    return dir_gold_sql,dir_pred_sql


def get_accuracy(dir_gold_sql,dir_pred_sql):
    cmd_str = f"""  # TODO
    python {root_path}/utils/test-suite-sql-eval-master/evaluation.py --gold {dir_gold_sql} --pred {dir_pred_sql} --db {DATABASE_PATH} --etype exec
    """
    result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
    acc = float([ans for ans in result.stdout.split('\n')[-2].split(' ') if ans][-1])
    return acc


def eval_text2sql_step_by_step(input_dir,target_name='PREDICTED SQL',output_dir=os.path.join(root_path, 'cache')):
    if input_dir.split(".")[-1]=='json':
        with open(input_dir) as fi:
            records = json.load(fi)
    elif input_dir.split(".")[-1]=='csv':
        records = pd.read_csv(input_dir)
        records.rename(columns={'NLQ':'question','GOLD SQL':'gold_sql','DATABASE':'db'},inplace=True)
        records=[record for _, record in records.iterrows()]
    else:
        return

    print("Auto Eval-Step-by-Step Starts...")
    dir_score_log=os.path.join(output_dir,'scores.log')
    dir_score_csv=os.path.join(output_dir,'scores.csv')
    with open(dir_score_log,'w') as fs:
        fs.write(f"Index\tQuestion\tScore\n")

    scores = []
    for idx,record in tqdm(enumerate(records)):
        gold_sql_dir, pred_sql_dir = generate_sql_gold_pred_files([record['db']], [record['gold_sql']],
                                                                  [record[target_name]],
                                                                  output_dir=output_dir)
        record_acc=get_accuracy(gold_sql_dir, pred_sql_dir)
        assert record_acc in [0.0, 1.0]

        scores.append({'index':idx,'question':record['question'],'score':record_acc})
        with open(dir_score_log,'a') as fs:
            fs.write(f"{idx}\t{record['question']}\t{record_acc}\n")

    df_scores=pd.DataFrame(scores)
    df_scores.to_csv(dir_score_csv)

    avg_score=df_scores['score'].mean()
    with open(dir_score_log, 'a') as fs:
        fs.write(f"\n\n\n==============================\nAverage Accuracy: {avg_score}\nNumber Question: {len(scores)}\n")
    print("Auto Eval-Step-by-Step Finished.")


def eval_text2sql_once(input_dir,target_name='PREDICTED SQL',output_dir=os.path.join(root_path, 'cache')):
    if input_dir.split(".")[-1]=='json':
        with open(input_dir) as fi:
            records = json.load(fi)
    elif input_dir.split(".")[-1]=='csv':
        records = pd.read_csv(input_dir)
        records.rename(columns={'NLQ':'question','GOLD SQL':'gold_sql','DATABASE':'db'},inplace=True)
        records=[record for _, record in records.iterrows()]
    else:
        return

    print("Auto Eval-Once Starts...")
    gold_sql_dir, pred_sql_dir = generate_sql_gold_pred_files([record['db'] for record in records],
                                                              [record['gold_sql'] for record in records],
                                                              [record[target_name] for record in records],
                                                              output_dir=output_dir)
    avg_score = get_accuracy(gold_sql_dir, pred_sql_dir)  # TODO

    dir_score_log = os.path.join(output_dir, 'scores_once.log')
    with open(dir_score_log, 'w') as fs:
        fs.write(f"\n\n==============================\nAverage Accuracy: {avg_score}\nNumber Question: {len(records)}\n")
    print('Auto Eval-Once Finished.')


if __name__=='__main__':
    # eval_text2sql_once("../cache/GPT4_zero_shot.csv")
    # eval_text2sql_step_by_step("../cache/GPT4_zero_shot.csv")
    eval_text2sql_once("./cache/unit_ppl_test_filled_example.json",target_name='init_sql')
    # eval_text2sql_step_by_step("../cache/unit_ppl_test_filled_example.json",target_name='init_sql')

