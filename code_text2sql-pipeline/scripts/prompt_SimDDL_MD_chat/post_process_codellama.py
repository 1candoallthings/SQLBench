import re, os
import sqlparse
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='codellama')
args = parser.parse_args()

llm = args.llm

def extract_sql(query, llm='sensenova'):
    if llm == "sensenova":
        if '```sql' in query:
            return re.findall(r"\`\`\`sql(.*?)\`\`\`", query.replace('\n', ' '))[0]
        else:
            return query.replace('\n', '')
    elif llm == 'llama2':
        if "### SQL:" in query:
            try:
                return re.findall(r"### SQL:(.*?)###", query.replace('\n', ' '))[0]
            except:
                return re.findall(r"### SQL:(.*?)", query.replace('\n', ' '))[0]
        elif "``` SELECT" in query:
            try:
                return re.findall(r"``` (.*?)```", query.replace('\n', ' '))[0]
            except:
                return re.findall(r"```(.*?)", query.replace('\n', ' '))[0]
        elif "###" in query:
            return query.split("###")[0]
        else:
            return query.replace('\n', '')
    elif llm == "sqlcoder":
        res = query
        return res
    elif llm == "codellama":
        sql_in = query
        if "<Answer>" in sql_in:
            sql_out = sql_in.split("<Answer>")[1].split("</Answer>")[0]
            return sql_out
        elif "Answer:" in sql_in:
            sql_out = sql_in.split("Answer:")[1].split(";")[0]
            return sql_out
        else:
            return query.replace('\n', ';')
    elif llm == "puyu":
        # res = query
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