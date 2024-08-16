# coding: utf-8

import random
import requests
import json
import time
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from settings import SECRETKEYS


class SQLCoder:

    def __init__(self, keys=None):
        self._key=None

    def __call__(self,
                 prompt,
                 core_pod_ip='10.119.28.126', 
                 temperature=0.001,
                 top_p=0.9,
                 max_new_tokens=256,
                 repetition_penalty=1.05,
                 stream=True,
                 *args, **kwargs):
        #替换敏感词
        prompt_desen=prompt.replace('Master', 'Bachelor')
        # print('-*-S'*20)
        # print(f"Puyu Prompt:\n{prompt_desen}")
        # print('--' * 30+' Fin Prompt ')

        url = 'http://cluster-proxy.sh.sensetime.com:19939/generate'  
        # context = "<|User|>:"+prompt+"\n<|Bot|>:"
        data = {
            "inputs": prompt,
            "parameters": {
                "do_sample": False,
                "temperature": temperature,
                "top_k": 1,
                "max_new_tokens": max_new_tokens,
                "repetition_penalty": repetition_penalty,
            }
        }
        response = requests.post(url, json=data)
        # print(response)
        time.sleep(0.1)
        if response.status_code == 200:
            try:
                res = response.json()
            except:
                raise Exception('Response can not be parsed !')
            return res["generated_text"][0].rstrip("</s>")
        else:
            # print('No response returned by SQLCoder !')
            return 'No response returned by SQLCoder !'
            # raise Exception('No response returned by SQLCoder !')


if __name__=='__main__':
    llm=SQLCoder()
    print(llm("""Figure out corresponding SQLite SQL Query of Question according to database.
<Database>
CREATE TABLE stadium (stadium_id NUMBER PRIMARY KEY, location TEXT, name TEXT, capacity NUMBER, highest NUMBER, lowest NUMBER, average NUMBER); CREATE TABLE singer (singer_id NUMBER PRIMARY KEY, name TEXT, country TEXT, song_name TEXT, song_release_year TEXT, age NUMBER, is_male OTHERS); CREATE TABLE concert (concert_id NUMBER PRIMARY KEY, concert_name TEXT, theme TEXT, stadium_id TEXT, year TEXT, FOREIGN KEY (stadium_id) REFERENCES stadium(stadium_id)); CREATE TABLE singer_in_concert (concert_id NUMBER PRIMARY KEY, singer_id TEXT, FOREIGN KEY (concert_id) REFERENCES concert(concert_id), FOREIGN KEY (singer_id) REFERENCES singer(singer_id));
</Database>
<Question>How many singers do we have?</Question>"""))
    # from multiprocessing import Pool 
    # pool = Pool(3)
    # print(list(pool.map(parallel_call, zip([['请用一句话解释万有引力'], ['请用2句话解释万有引力'], ['请用3句话解释万有引力']], SECRETKEYS['llama2']))))
#     prompt='''Complete sqlite SQL query only and with no explanation.

# DATABASE:
# Table enterprise_finance_report_month, columns = [*, company_name, accounting_year_month, index_name, this_year, last_year, this_year_budget, this_month, completion_rate, change_last_year, year_on_year, this_year_start, compared_beginning_year, year_to_date, last_month, compared_last_year, change_rate_last1M_this_year]
# Table ha02_cmft_person_info_wide, columns = [*, year, belong_day, company, leader_name, emplid, aes_emplid, name, sex, phone, birthdate, age, age_type, level_1, level_1_name, level_2, level_2_name, level_2_managername, level_3, level_3_name, level_3_managername, action, action_dt_start, eff_status, last_entry_dt, cmpny_seniority_dt, start_entry_dt, birthcountry, birthplace, school_descr, education, age_cmp, age_job, natiion, recruit_mode, jobcode, company_selft_jobdescr, supv_lvl_id, c_sta_supv_lvl, c_grp_supv_lvl, position_sequence_code, position_sequence_name, position_sequence_code_sub, position_sequence_name_sub, DW_Etl_Dt, DW_Etl_Tm, DW_Ins_Dt, DW_Ins_Tm]
# Table ha02_cmft_people_org_relation, columns = [*, id, org_id, org_name, parent_org_id, virtual_parent_org_id, company_id, level]
# Table ha02_cmft_personnel_performance, columns = [*, year, emplid, name, level_1, level_1_name, level_2, level_2_name, level_3, level_3_name, score]
# Table ads_index_wall, columns = [*, sum_month, index_name, index_value, unit_value, org_name, budget_complete, year_over_year, ing_ratio, kpi_rate]

# 金科员工的平均年龄是多少?
# SELECT'''
#     print(llm(prompt=prompt))
