python ./scripts/post_process.py --llm $*
python utils/test-suite-sql-eval-master/evaluation.py --gold data/gold_test.txt --pred $*_out_post.txt --db utils/database-spider/database-dev --etype exec

python utils/test-suite-sql-eval-master/evaluation.py --gold data/gold_test.txt --pred /root/lizhishuai/text2sql/scripts/prompt_html_chat/puyu_out_post.txt --db utils/database-spider/database-dev --etype exec