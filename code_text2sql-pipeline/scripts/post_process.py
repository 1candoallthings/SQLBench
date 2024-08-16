
import re, os


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--llm", default='sensenova')
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
            return res[:-2]
        else:
            return "SELECT " + res[:-2]

def extract_sql_from_text(text):
    sql_pattern = r'\bSELECT\b.*?\bFROM\b.*?ി'
    sql_matches = re.findall(sql_pattern, text, re.DOTALL)
    sql_statements = [sql.strip() for sql in sql_matches]
    return sql_statements


proj_dir = os.path.dirname(os.path.dirname(__file__))
with open(f'pred_{llm}_dailpmpt.txt', 'r', encoding='utf-8') as file:
    content = file.readlines()
    
extracted_query = [extract_sql_from_text(c, llm=llm) for c in content]
with open(f'{llm}_out_post.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(extracted_query))