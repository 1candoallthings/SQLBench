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
        if '``` SELECT' in query:
            try:
                sql_out = re.findall(r"```(.*?)```", query.replace('\n', ' '))[0]
                return sql_out
            except:
                sql_out = re.findall(r"```(.*?)", query.replace('\n', ' '))[0]
                return sql_out
        elif "###" in query:
            return query.split('###')[0]
        else:
            return query.replace('\n', '')
    # elif llm == "codellama":
    #     if '```' in query:
    #         return re.findall(r"```(.*?)```", query.replace('\n', ' '))[0]
    #     elif "; ###" in query:
    #         return query.split('; ###')[0]
    #     else:
    #         return query.replace('\n', '')
    elif llm == "puyu" or llm == "codellama" or llm == "sqlcoder":
        res = query
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return res

def extract_sql_from_text(text):
    sql_pattern = text.replace("\n", " ").split('~~')
    return sql_pattern


proj_dir = os.path.dirname(__file__)
with open(proj_dir + f'/pred/pred_{llm}_parallel.txt', 'r', encoding='utf-8') as file:
    content = file.readlines()
    
extracted_query = [sqlparse.format(extract_sql(q, llm), reindent=False) for q in extract_sql_from_text("\n".join(content))]
with open(proj_dir + f'/pred/final_pred/{llm}_out_post.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(extracted_query))