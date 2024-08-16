
import re, os


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
        res = query
        if res.lower().startswith("SELECT".lower()) or res.lower().startswith(" SELECT".lower()) or res.lower().startswith("  SELECT".lower()):
            return res
        else:
            return "SELECT " + res

def extract_sql_from_text(text):
    sql_pattern = text.replace("\n", " ").split('~~')
    return sql_pattern


proj_dir = os.path.dirname(__file__)
with open(proj_dir + f'/pred_{llm}_parallel.txt', 'r', encoding='utf-8') as file:
    content = file.readlines()
    
extracted_query = [extract_sql(q, llm) for q in extract_sql_from_text("\n".join(content))]
with open(proj_dir + f'/{llm}_out_post.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(extracted_query))