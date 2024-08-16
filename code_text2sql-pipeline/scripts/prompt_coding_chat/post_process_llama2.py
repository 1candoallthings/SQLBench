import re, os
import sqlparse
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='llama2')
args = parser.parse_args()

llm = args.llm

def extract_sql(query, llm='sensenova'):
    if llm == "sensenova":
        if '```sql' in query:
            return re.findall(r"\`\`\`sql(.*?)\`\`\`", query.replace('\n', ' '))[0]
        else:
            return query.replace('\n', '')
    elif llm == 'llama2':
        res = query
        if "/*" in query:
            res = query.split("/*")
            rese = ""
            for data in res:
                if "select" in data.lower():
                    rese = data
                    break
                else:
                    rese = res[1]
            return rese
        elif 'begin{code}' in res:
            try:
                sql_out = re.findall(r"begin{code}(.*?); ", res.replace('\n', ' '))[0]
                return sql_out
            except:
                sql_out = re.findall(r"begin{code}(.*?)", res.replace('\n', ' '))[0]
                return sql_out
        elif "``` SELECT" in res:
            try:
                sql_out = re.findall(r"```(.*?)```", res.replace('\n', ' '))[0]
                return sql_out
            except:
                sql_out = re.findall(r"```(.*?)", res.replace('\n', ' '))[0]
                return sql_out
        elif ";" in res:
            res = query.split(";")[0]
            return res
        else:
            return res
    elif llm == "sqlcoder":
        res = query
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(
                " SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return "SELECT " + res
    elif llm == "codellama":
        res = query
        if "/*" in query:
            res = query.split("/*")[0]
            return res
        else:
            return res
    elif llm == "puyu":
        if "/* SQL Query here */" in query:
            query = str(query).split("/* SQL Query here */")[1]
        elif "``` SELECT" in query:
            try:
                query = re.findall(r"```(.*?)```", query.replace('\n', ' '))[0]
            except:
                query = re.findall(r"```(.*?)", query.replace('\n', ' '))[0]
                return query
        return str(query).replace(';', '').replace('ി','').replace('\n','')

def extract_sql_from_text(text):
    sql_pattern = text.replace("\n", " ").split('~~')
    return sql_pattern


proj_dir = os.path.dirname(__file__)
with open(proj_dir + f'/pred/pred_{llm}_parallel.txt', 'r', encoding='utf-8') as file:
    content = file.readlines()
    
extracted_query = [sqlparse.format(extract_sql(q, llm), reindent=False) for q in extract_sql_from_text("\n".join(content))]
with open(proj_dir + f'/pred/final_pred/{llm}_out_post.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(extracted_query))