
import re, os


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='sensenova')
args = parser.parse_args()

llm = args.llm

def extract_sql(query, llm='sensenova'):
    if llm == "sensenova":
        if '```sql' in query:
            try:
                return re.findall(r"```sql(.*?)```", query.replace('\n', ' '))[0]
            except:
                return re.findall(r"```sql(.*?)", query.replace('\n', ' '))[0]
        elif '```SQL' in query:
            try:
                return re.findall(r"```SQL(.*?)```", query.replace('\n', ' '))[0]
            except:
                return re.findall(r"```SQL(.*?)", query.replace('\n', ' '))[0]
        else:
            return query.replace('\n', '')
    elif llm == "sqlcoder":
        if '<SQLQuery>' in query:
            return re.search(r'<SQLQuery>(.*?)</SQLQuery>', query).group(1)
        elif '<SQL>' in query:
            return re.search(r'<SQL>(.*?)</SQL>', query).group(1)
        else:
            return query.replace('\n', '')
    elif llm == 'llama2' or llm == "codellama":
        if ';' in query:
            res = re.findall(r'(.*?);', query.replace('\n', ' '))[0]
            if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
                return res
            else:
                return "SELECT " + res
        else:
            return query.replace('\n', '')
    elif llm == "puyu":
        return str(query).replace(';', '').replace('ി','').replace('\n','')
        # res = query
        # if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
        #     return res
        # else:
        #     return "SELECT " + res

def extract_sql_from_text(text):
    sql_pattern = text.split('~~')
    return sql_pattern


proj_dir = os.path.dirname(__file__)
with open(proj_dir + f'/pred/pred_{llm}_parallel.txt', 'r', encoding='utf-8') as file:
    content = file.readlines()
    
extracted_query = [extract_sql(q, llm) for q in extract_sql_from_text("\n".join(content))]
with open(proj_dir + f'/pred/final_pred/{llm}_out_post.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(extracted_query))