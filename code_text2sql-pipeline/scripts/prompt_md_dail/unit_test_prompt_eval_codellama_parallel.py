import json, tqdm, sys, os, re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from settings import SECRETKEYS
from llms import codellama, Puyu, SenseNova
from llms import Llama2 as llama2
import logging
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='codellama')
args = parser.parse_args()

llm_name = args.llm

def formatting_prompt(sample):
    ddl = sample['ddl']
    ddl = ddl.split('; ')
    return ';\n\n'.join(ddl)


if __name__ == '__main__':
    proj_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    input_file = proj_dir + "/data/ppl_test.json"
    file_dir = os.path.dirname(__file__)
    log_file_path = os.path.join(file_dir, f"logs/{llm_name}_parallel.log")
    logging.basicConfig(filename=log_file_path, level=logging.INFO, filemode='w')
    logger = logging.getLogger()  
    with open(input_file) as f:
        input_data = json.load(f)

    from multiprocessing import Pool
    import time
    
    stms = time.time()
    pool = Pool(48)
    llm = codellama()
    pmpts = []
    with open(file_dir + f'/pred_{llm_name}_parallel.txt', 'w',encoding='utf-8') as file:
        for ix in tqdm.tqdm(range(len(input_data))):
            question=input_data[ix]['question']
            # ddls = formatting_prompt(input_data[ix])
            ddls = input_data[ix]['simplified_ddl']
            prompt=f'''### Complete sqlite SQL query only and with no explanation\n### Sqlite SQL tables, with their properties:\n#\n{ddls}\n#\n### {question}\nSELECT'''
            pmpts.append(prompt)
            logger.info(prompt)
        result = list(pool.map(llm, pmpts))
        result = '~~'.join(result[i].replace("\n", " ") + "--" + str(i) for i in range(len(result)))
        file.write(str(result)+'\n')
    print(time.time() - stms)