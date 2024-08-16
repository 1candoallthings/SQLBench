import json, tqdm, sys, os, re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from settings import SECRETKEYS
from llms import *
from llms import Llama2 as llama2
import logging
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='gpt35')
args = parser.parse_args()

llm_name = args.llm

def formatting_prompt(sample):
    ddl = sample['ddl']
    ddl = ddl.split('; ')
    return ';\n\n'.join(ddl)


if __name__ == '__main__':
    num = 5
    proj_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # input_file = proj_dir + f"/data/bird/bird_big_table_{num}_final_simple_ddl.json"
    input_file = r"C:\Users\huxiaoru\Documents\WXWork\1688855843288713\Cache\File\2024-03\gpt35_error_sql_info_with_all_error_simple_ddl.json"
    file_dir = os.path.dirname(__file__)
    log_file_path = os.path.join(file_dir, f"bird_{num}/logs/{llm_name}_parallel.log")
    logging.basicConfig(filename=log_file_path, level=logging.INFO, filemode='w')
    logger = logging.getLogger()  
    with open(input_file,"r",encoding="utf-8") as f:
        input_data = json.load(f)

    from multiprocessing import Pool
    import time
    
    stms = time.time()
    pool = Pool(1)
    llm = GPT()
    pmpts = []
    with open(file_dir + f'/bird_{num}/pred/pred_{llm_name}_parallel.txt', 'w',encoding='utf-8') as file:
        for ix in tqdm.tqdm(range(len(input_data))):
            question=input_data[ix]['question']
            # ddls = formatting_prompt(input_data[ix])
            ddls = input_data[ix]['simplified_ddl']
            prompt = f'''### Answer the question by sqlite SQL query only and with no explanation\n### Sqlite SQL tables, with their properties:\n#\n{ddls}#\n### {question}\n### SQL: '''
            pmpts.append(prompt)
            logger.info(prompt)
        result = list(pool.map(llm, pmpts))
        result = '~~'.join(result[i].replace("\n", " ") + "--" + str(i) for i in range(len(result)))
        file.write(str(result)+'\n')
    print(time.time() - stms)
