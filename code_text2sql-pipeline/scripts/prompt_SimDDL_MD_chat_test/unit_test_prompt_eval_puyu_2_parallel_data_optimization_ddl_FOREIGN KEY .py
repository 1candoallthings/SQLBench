import json, tqdm, sys, os, re, sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from settings import SECRETKEYS
from llms import codellama, Puyu, SenseNova, codellama_1024
from llms import *
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='puyu2')
args = parser.parse_args()

llm_name = args.llm


def formatting_prompt(sample):
    ddl = sample['ddl']
    ddl = ddl.split('; ')
    return ';\n\n'.join(ddl)


if __name__ == '__main__':
    proj_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    input_file = proj_dir + "/data/spider/ppl_spider_test.json"
    file_dir = os.path.dirname(__file__)
    log_file_path = os.path.join(file_dir,
                                 f"data_0402/logs/{llm_name}_parallel_optimization_ddl_foreign_key_0204_question_zhishuai.log")
    logging.basicConfig(filename=log_file_path, level=logging.INFO, filemode='w')
    logger = logging.getLogger()
    with open(input_file, "r") as f:
        input_data = json.load(f)

    from multiprocessing import Pool
    import time

    stms = time.time()
    pool = Pool(48)
    llm = Internlm2()
    pmpts = []
    with open(
            file_dir + f'/data_0402/pred/pred_{llm_name}_parallel_optimization_ddl_foreign_key_0204_question_zhishuai.txt',
            'w',
            encoding='utf-8') as file:
        for ix in tqdm.tqdm(range(len(input_data))):
            question = input_data[ix]['question']
            # ddls = formatting_prompt(input_data[ix])
            db = input_data[ix]['db']
            # 动态加载前三行数据
            simplified_ddl_data = []
            # 读取数据库
            mydb = sqlite3.connect(
                fr"G:\AutoTask\text2sql\text2sql-dev\data\spider\test_database/{db}/{db}.sqlite")  # 链接数据库
            cur = mydb.cursor()
            # 表
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            Tables = cur.fetchall()  # Tables 为元组列表
            for table in Tables:
                # 列
                cur.execute(f"select * from {table[0]}")
                col_name_list = [tuple[0] for tuple in cur.description]
                # print(col_name_list)
                db_data_all = []
                # 获取前三行数据
                for i in range(3):
                    db_data_all.append(cur.fetchone())
                # ddls_data
                test = ""
                for idx, column_data in enumerate(col_name_list):
                    # print(list(db_data_all[2])[idx])
                    try:
                        test += f"{column_data}[{list(db_data_all[0])[idx]},{list(db_data_all[1])[idx]},{list(db_data_all[2])[idx]}],"
                    except:
                        test = test
                simplified_ddl_data.append(f"{table[0]}({test[:-1]})")
            ddls_data = "# " + ";\n# ".join(simplified_ddl_data) + ";\n"
            ddls = input_data[ix]['simplified_ddl']
            foreign_key = ""
            for foreign_key_data in input_data[ix]["foreign_key"][0].split("\n"):
                foreign_key += f'# {foreign_key_data};\n'
            foreign_key = foreign_key[:-2]
            # prompt = f'''### Answer the question by sqlite SQL query only and with no explanation.you must minimize SQL execution time while ensuring correctness.\n### Sqlite SQL tables, with their properties:\n#\n{ddls}#\n### Here are some data information about database references.\n#\n{ddls_data}#\n### Foreign key information of Sqlite SQL tables, used for table joins: \n#\n{foreign_key}\n#\n### Question: {question}\n### SQL: '''
            prompt = f'''### Answer the question by sqlite SQL query only and with no explanation.you must minimize SQL execution time while ensuring correctness.\n### Sqlite SQL tables, with their properties:\n#\n{ddls}#\n### Here are some data information about database references.\n#\n{ddls_data}#\n### Foreign key information of Sqlite SQL tables, used for table joins: \n#\n{foreign_key}\n#\n### {question}\n### SQL: '''

            pmpts.append(prompt)
            logger.info(prompt)
        result = list(pool.map(llm, pmpts))
        result = '~~'.join(result[i].replace("\n", " ") + "--" + str(i) for i in range(len(result)))
        file.write(str(result) + '\n')
    print(time.time() - stms)
