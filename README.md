
# Installation 

Set up the Python environment:
```
conda create -n SQLBench python=3.8 -y
conda activate SQLBench
pip install -r requirements.txt
```

# Running

Export your OpenAI API key:
```
export OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

Replace the VPN launch approach below with your own method, to gain access to OpenAI:
```
export https_proxy=http://127.0.0.1:15777 http_proxy=http://127.0.0.1:15777
```

Finally, simply run :laughing::
```
cd src
bash run.sh
```
this script automatically conducts all procedures: 1) text2sql, 2) evaluation. You can find the output SQL in `src/text2sql_results`.




