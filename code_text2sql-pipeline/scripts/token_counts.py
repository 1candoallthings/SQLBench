import tiktoken

def num_tokens_from_string(string: str, encoding_name: str="cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


import os, json, tqdm
proj_dir = os.path.dirname(os.path.dirname(__file__))
input_file = proj_dir + "/data/ppl_test.json"
with open(input_file) as f:
    input_data = json.load(f)
sqls = []
for sample in tqdm.tqdm(input_data):
    sqls.append(sample["gold_sql"])


longest_string = max(sqls, key=num_tokens_from_string)

print(num_tokens_from_string(longest_string))