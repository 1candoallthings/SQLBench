import json, tqdm, sys, os, re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from settings import SECRETKEYS
from llms import codellama, Puyu, SenseNova
from llms import Llama2 as llama2
from llms import *
import logging
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='puyu2_chat_sensecore')
args = parser.parse_args()

llm_name = args.llm

def formatting_prompt(sample):
    ddl = sample['ddl']
    ddl = ddl.split('; ')
    return ';\n\n'.join(ddl)


if __name__ == '__main__':
    proj_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    input_file = proj_dir + "/data/ppl_test_spider_with_foreign_key.json"
    file_dir = os.path.dirname(__file__)
    log_file_path = os.path.join(file_dir, f"data/logs/{llm_name}_parallel_optimization_ddl_foreign_key.log")
    logging.basicConfig(filename=log_file_path, level=logging.INFO, filemode='w')
    logger = logging.getLogger()  
    with open(input_file,"r",encoding="utf-8") as f:
        input_data = json.load(f)

    from multiprocessing import Pool
    import time
    
    stms = time.time()
    pool = Pool(48)
    llm = Internlm2_Chat()
    pmpts = []
    with open(file_dir + f'/data/pred/pred_{llm_name}_parallel_optimization_ddl_foreign_key.txt', 'w',encoding='utf-8') as file:
        for ix in tqdm.tqdm(range(len(input_data))):
            question=input_data[ix]['question']
            # ddls = formatting_prompt(input_data[ix])
            ddls_data = input_data[ix]['simplified_ddl_data']
            ddls = input_data[ix]['simplified_ddl']
            foreign_key = ""
            for foreign_key_data in input_data[ix]["foreign_key"][0].split("\n"):
                foreign_key += f'# {foreign_key_data};\n'
            foreign_key = foreign_key[:-2]
            prompt = f'''### Answer the question by sqlite SQL query only and with no explanation.you must minimize SQL execution time while ensuring correctness.\n### Sqlite SQL tables, with their properties:\n#\n{ddls}#\n### Here are some data information about database references.\n#\n{ddls_data}#\n### Foreign key information of Sqlite SQL tables, used for table joins: \n#\n{foreign_key}\n### {question}\n### SQL: '''
            pmpts.append(prompt)
            logger.info(prompt)
        result = list(pool.map(llm, pmpts))
        result = '~~'.join(result[i].replace("\n", " ") + "--" + str(i) for i in range(len(result)))
        file.write(str(result)+'\n')
    print(time.time() - stms)
