import json, tqdm, sys, os, re
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from settings import SECRETKEYS
from utils import codellama, Llama2, Puyu, SenseNova


if __name__ == '__main__':
    from typing import List, Optional
    import requests
    import yaml
    import time
    import json
    import sys
    import sqlite3
    from sqlalchemy import create_engine, text
    
    proj_dir = os.path.dirname(os.path.dirname(__file__))
    llm = Puyu()
    stms = time.time()
    with open(proj_dir + '/utils/database-spider/dev.json','r',encoding='utf-8') as f:
        dev=json.load(f)
    with open('pred_puyu_out_mdprompt.txt', 'w',encoding='utf-8') as file:
        for ix, item in enumerate(tqdm.tqdm(dev)):
            # if ix < 160:
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
            print(prompt)
            result=llm(prompt)
            print(result)

            result = ' '.join(result.splitlines())
            file.write(str(result)+'\n')
            connection.close()
    print(time.time() - stms)