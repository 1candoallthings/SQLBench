import json, tqdm, sys, os, re
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from settings import SECRETKEYS
from llms import codellama, Llama2, Puyu, SenseNova

import sqlparse
sqlparse.format

def formatting_prompt(sample):
    ddl = sample['ddl']
    linked_tables = sample['linked_tables']
    linked_columns = sample['linked_columns']
    split_ddl = ddl.split(";")
    res_ddl = []
    global cnt
    for one_ddl in split_ddl:
        hit = 0
        for one_table in linked_tables:
            if f"TABLE {one_table.lower()} (".lower() in one_ddl.lower():
                cnt += 1
                hit = 1
                ddl_template = "CREATE TABLE {table_name} ({column_definitions});"
                pattern = re.compile(r'(.*?)CREATE TABLE (\w+) \((.+)\);')
                all_columns = pattern.match(one_ddl+';')[3].split(",")
                all_columns[0] = " " + all_columns[0]
                valid_columns = []
                for one_column in linked_columns:
                    for col_type in all_columns:
                        if f" {one_column.lower()} " in col_type.lower() or f"({one_column.lower()})" in col_type.lower():
                            valid_columns.append(col_type)
                one_ddl = ddl_template.format(table_name=one_table.lower(), column_definitions=','.join(valid_columns))
        if hit:
            res_ddl.append(one_ddl)
    ddl = ";".join(res_ddl)

    return f"<INST>{sample['instruction']}</INST><DATABASE>{ddl}</DATABASE><Question>{sample['question']}</Question><SQL>SELECT "



def parallel_call(inps):
    querys, api = inps[0], inps[1]
    llm=Llama2()
    res = []
    for q in querys:
        out = llm(q, core_pod_ip=api)
        res.append(out)
    return res    


if __name__ == '__main__':
    proj_dir = os.path.dirname(os.path.dirname(__file__))
    input_file = proj_dir + "/data/ppl_test.json"
    with open(input_file) as f:
        input_data=json.load(f)
    # global cnt 
    # cnt = 0
    # # Your algo
    # for sample in tqdm.tqdm(input_data):
    #     prompt_target = formatting_prompt(sample)
    # print(cnt)
    # llm=Llama2()
    # print(llm(prompt_target))

    # from multiprocessing import Pool 
    # pool = Pool(3)
    # print(list(pool.map(parallel_call, zip([['请用一句话解释万有引力'], ['请用2句话解释万有引力'], ['请用3句话解释万有引力']], SECRETKEYS['llama2']))))
    from typing import List, Optional
    import requests
    import yaml
    import time
    import json
    import sys
    import sqlite3
    from sqlalchemy import create_engine, text
    
    llm = SenseNova()
    stms = time.time()
    with open(proj_dir + '/utils/database-spider/dev.json','r',encoding='utf-8') as f:
        dev=json.load(f)
    with open('pred_nova_wo_tab.txt', 'w',encoding='utf-8') as file:
        for ix, item in enumerate(tqdm.tqdm(dev)):
            # if ix < 957:
            #     continue
            db_id=item['db_id']
            question=item['question']
            db_url = f'sqlite:////{proj_dir}/utils/database-spider/database-dev/{db_id}/{db_id}.sqlite'
            engine = create_engine(db_url)
            connection = engine.connect()
            query = text("""
                SELECT name
                FROM sqlite_master
                WHERE type='table';
            """)
            output_text = ""
            result = connection.execute(query)
            for row in result:
                table_name = row[0]
                # if input_data[ix]['linked_tables'] and not table_name in input_data[ix]['linked_tables']:
                #     continue
                output_text += f"# {table_name}("
                columns_query = text(f"PRAGMA table_info({table_name});")
                columns_result = connection.execute(columns_query)
                for i, column_row in enumerate(columns_result):
                    column_name = column_row[1]  # Use integer index 1 for the 'name' column
                    if i != 0:
                        output_text += f",{column_name}"
                    else:
                        output_text += f"{column_name}"
                output_text += ");\n"
            output_text = output_text[:-2] + "." + output_text[-1]
            prompt=f'''### Complete sqlite SQL query only and with no explanation\n### Sqlite SQL tables, with their properties:\n#\n{output_text}#\n### {question}\n SELECT'''
            input_data[ix]['simplified_ddl'] = output_text
            # print(prompt)
            # result=llm(prompt)
            # print('return', result)

            # result = ' '.join(result.splitlines())
            # file.write(str(result)+'\n')
            connection.close()
    json.dump(input_data, open(proj_dir + "/data/ppl_test.json", "w", encoding='utf-8'), ensure_ascii=False, indent=4)
    print(time.time() - stms)