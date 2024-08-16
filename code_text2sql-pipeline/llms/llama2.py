# coding: utf-8

import random
import requests
import json
import time
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from settings import SECRETKEYS


class Llama2:

    def __init__(self, keys=None):
        self._key=None

    def __call__(self,
                 prompt,
                 core_pod_ip='10.119.25.63',
                 temperature=0.1,
                 top_p=0.9,
                 max_new_tokens=256,
                 repetition_penalty=1.05,
                 stream=False,
                 *args, **kwargs):
        #替换敏感词
        # prompt_desen=prompt.replace('Master', 'Bachelor')
        # print('-*-S'*20)
        # print(f"Llama2 Prompt:\n{prompt}")
        # print('--' * 30+' Fin Prompt ')

        server = "http://103.177.28.206:8000/api/generate"
        headers = {"Content-Type": "application/json"}
        endpoint = f"http://{core_pod_ip}:2345/generate"  # cci tgi-gpu8
        
        request_body = {
            "endpoint": endpoint,
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": True,
                "max_new_tokens": max_new_tokens,
                "top_k": 4,
                "repetition_penalty": repetition_penalty,
                "stop": [
                #  "</s>",
                #  "User:",
                ]
            }
        }
        response = requests.post(server, headers=headers, json=request_body, stream=stream)

        time.sleep(0.1)
        if response.status_code == 200:
            try:
                res = response.json()
            except:
                raise Exception('Response can not be parsed !')
            try:
                return res["generated_text"]
            except:
                return "generated_text"
        else:
            raise Exception('No response returned by SenseNova !')

def parallel_call(inps):
    querys, api = inps[0], inps[1]
    llm=Llama2()
    res = []
    for q in querys:
        out = llm(q, core_pod_ip=api)
        res.append(out)
    return res    

if __name__=='__main__':
    llm=Llama2()
    print(llm('请用一句话解释万有引力'))
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