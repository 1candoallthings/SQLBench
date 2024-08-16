pip install -r requirements.txt
python nltk_downloader.py
python scripts/evaluation.py --gold exams/official_demo/gold_example.txt --pred examps/official_demo/pred_example.txt --etype all --db spider/database-dev --table examples/official_demo/data/tables.json > examp/official_demo/eval_results.txt

