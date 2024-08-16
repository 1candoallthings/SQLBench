import json, tqdm, sys, os, re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from settings import SECRETKEYS
from llms import codellama, Puyu, SenseNova
from llms import Llama2 as llama2
import logging
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='llama2')
args = parser.parse_args()

llm_name = args.llm

def formatting_prompt(sample):
    ddl = sample['ddl']

    template_info =   "/* Given the following database schema: */\n" \
                      "{}"
    template_question = "/* Answer the following: {} */"

    sql = template_info.format(";\n\n".join(ddl.split("; ")))
    prompt = "\n".join(
        [sql, template_question.format(sample['question']) + "\nSELECT "])
    return prompt


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
    llm = llama2()
    pmpts = []
    with open(file_dir + f'/pred_{llm_name}_parallel.txt', 'w',encoding='utf-8') as file:
        for ix in tqdm.tqdm(range(len(input_data))):
            question=input_data[ix]['question']
            prompt = formatting_prompt(input_data[ix])
            pmpts.append(prompt)
            logger.info(prompt)
        result = list(pool.map(llm, pmpts))
        result = '~~'.join(result[i].replace("\n", " ") + "--" + str(i) for i in range(len(result)))
        file.write(str(result)+'\n')
    print(time.time() - stms)
