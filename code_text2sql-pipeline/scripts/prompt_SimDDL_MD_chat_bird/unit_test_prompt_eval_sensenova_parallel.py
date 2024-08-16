import json, tqdm, sys, os, re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from settings import SECRETKEYS
from llms import codellama, Puyu, SenseNova
from llms import Llama2 as llama2
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='SenseNova')
args = parser.parse_args()

llm_name = args.llm


def formatting_prompt(sample):
    ddl = sample['ddl']
    ddl = ddl.split('; ')
    return ';\n\n'.join(ddl)


if __name__ == '__main__':
    proj_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    num = 2
    input_file = proj_dir + f"/data/bird/bird_big_table_{num}_final_simple_ddl.json"
    file_dir = os.path.dirname(__file__)
    log_file_path = os.path.join(file_dir, f"bird_{num}/logs/{llm_name}_parallel_1225_01.log")
    logging.basicConfig(filename=log_file_path, level=logging.INFO, filemode='w')
    logger = logging.getLogger()
    with open(input_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    from multiprocessing import Pool
    import time

    stms = time.time()
    pool = Pool(1)
    llm = SenseNova()
    pmpts = []
    with open(file_dir + f'/bird_{num}/pred/pred_{llm_name}_parallel_1225_01.txt', 'w', encoding='utf-8') as file:
        for ix in tqdm.tqdm(range(len(input_data))):
            question = input_data[ix]['new_question']
            # ddls = formatting_prompt(input_data[ix])
            ddls = input_data[ix]['simplified_ddl']
            prompt = f'''### Answer the question by sqlite SQL query only and with no explanation\n### Sqlite SQL tables, with their properties:\n#\n{ddls}#\n### {question}\n### SQL: '''
            pmpts.append(prompt)
            logger.info(prompt)
        result = list(pool.map(llm, pmpts))
        result = '~~'.join(result[i].replace("\n", " ") + "--" + str(i) for i in range(len(result)))
        file.write(str(result) + '\n')
    print(time.time() - stms)