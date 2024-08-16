import re, os
import sqlparse
import argparse
import json
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='gpt35')
args = parser.parse_args()

llm = args.llm

def extract_sql(query, llm='sensenova'):
    if llm == "sensenova":
        if '```sql' in query:
            return re.findall(r"\`\`\`sql(.*?)\`\`\`", query.replace('\n', ' '))[0]
        else:
            return query.replace('\n', '')
    elif llm == 'llama2':
        if "###" in query:
            return "SELECT " + query.split('###')[0]
        else:
            return query.replace('\n', '')
    elif llm == "sqlcoder":
        res = query
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(
                " SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return "SELECT " + res
    elif llm == "codellama":
        res = query.replace("###","")
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(
                " SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return "SELECT " + res
    elif llm == "puyu" or llm == "gpt35":
        res = query
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return res

def extract_sql_from_text(text):
    sql_pattern = text.replace("\n", " ").replace("ി", " ").split('~~')
    return sql_pattern


import json
num = 5
proj_dir_ = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# input_file = proj_dir_ + f"/data/bird/bird_big_table_{num}_final_simple_ddl.json"
input_file = r"C:\Users\huxiaoru\Documents\WXWork\1688855843288713\Cache\File\2024-03\gpt35_error_sql_info_with_all_error_simple_ddl.json"
proj_dir = os.path.dirname(__file__)
with open(proj_dir + f'/bird_{num}/pred/pred_{llm}_parallel.txt', 'r', encoding='utf-8') as file:
    content = file.readlines()
dev_data = json.load(open(input_file,"r",encoding="utf-8"))
extracted_query = [extract_sql(q, llm) for q in extract_sql_from_text("\n".join(content))]
with open(proj_dir + f'/bird_{num}/pred/final_pred/{llm}_out_post.json', 'w', encoding='utf-8') as file:
    anno = {}
    for i,data in enumerate(extracted_query):
        # print()
        anno[i] = extracted_query[i] + "	----- bird -----	" + dev_data[i]["db_id"]
    # file.write('\n'.join(extracted_query))
    file.write(json.dumps(anno, ensure_ascii=False, indent=4) + "\n")


import os
proj_dir_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# os.system(f'python {proj_dir_root}/bird/llm/src/evaluation_0103.py '
#           f'--db_root_path {proj_dir_root}/bird/dev/dev_databases/ '
#           f'--data_mode dev '
#           f'--meta_time_out 30.0 '
#           f'--predicted_sql_path {proj_dir}/bird_{num}/pred/final_pred/{llm}_out_post.json '
#           f'--ground_truth_path {proj_dir_root}/data/bird/bird_big_table_{num}_final_gold.sql '
#           f'--diff_json_path {input_file} '
#           f'--save_json_path {proj_dir}/bird_{num}/pred/save_pred/{llm}_{num}_result.json')


# os.system(f'python {proj_dir_root}/bird/llm/src/evaluation_ves_0115.py '
#           f'--db_root_path {proj_dir_root}/bird/dev/dev_databases/ '
#           f'--data_mode dev '
#           f'--meta_time_out 600.0 '
#           f'--num_cpus 16 '
#           f'--predicted_sql_path {proj_dir}/bird_{num}/pred/final_pred/{llm}_out_post.json '
#           f'--ground_truth_path {proj_dir_root}/data/bird/bird_big_table_{num}_final_gold.sql '
#           f'--diff_json_path {input_file} '
#           f'--save_json_path {proj_dir}/bird_{num}/pred/save_pred/{llm}_{num}_final_ves.json')


os.system(f'python {proj_dir_root}/bird/llm/src/evaluation_0103.py '
          f'--db_root_path {proj_dir_root}/bird/dev/dev_databases/ '
          f'--data_mode dev '
          f'--meta_time_out 30.0 '
          f'--predicted_sql_path {proj_dir}/bird_{num}/pred/final_pred/{llm}_out_post.json '
          fr'--ground_truth_path C:\Users\huxiaoru\Documents\WXWork\1688855843288713\Cache\File\2024-03\gpt35_error_sql_info_with_all_error_simple_ddl.sql '
          f'--diff_json_path {input_file} '
          f'--save_json_path {proj_dir}/bird_{num}/pred/save_pred/{llm}_{num}_result.json')