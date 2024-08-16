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
        if "/*" in query:
            return "SELECT " + query.split('/*')[0]
        else:
            return "SELECT " + query.replace('\n', '')
    elif llm == "sqlcoder":
        res = query
        return "SELECT " + res
    elif llm == "codellama":
        res = query
        if "/*" in res:
            return "SELECT " + res.split("/*")[0]
        else:
            return "SELECT " + res
    elif llm == "puyu":
        res = query
        if "*/ " in res:
            res = res.split("*/ ")[len(res.split("*/ "))-1].replace("ി","")
            if "select" not in res.lower():
                res = "SELECT " + res
        elif "/* SELECT" in res:
            res = res.split("/* SELECT")[len(res.split("/* SELECT"))-1].replace("*/ി","")
            if "select" not in res.lower():
                res = "SELECT " + res
        if "select" not in res.lower().split(" ")[0]:
            res = "SELECT " + res
        return res.replace("ി","").replace("/*","").replace("*/","")

def extract_sql_from_text(text):
    sql_pattern = text.replace("\n", " ").split('~~')
    return sql_pattern


proj_dir = os.path.dirname(__file__)
with open(proj_dir + f'/pred/pred_{llm}_parallel.txt', 'r', encoding='utf-8') as file:
    content = file.readlines()
    
extracted_query = [sqlparse.format(extract_sql(q, llm), reindent=False) for q in extract_sql_from_text("\n".join(content))]
with open(proj_dir + f'/pred/final_pred/{llm}_out_post.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(extracted_query))