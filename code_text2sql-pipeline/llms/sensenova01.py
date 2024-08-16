# coding: utf-8

import random
import requests
import json
import time
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from settings import SECRETKEYS


class SenseNova01:
    '''
    Manual: https://platform.sensenova.cn/#/doc?path=/chat/ChatCompletions/ChatCompletions.md
    '''
    def __init__(self, keys=SECRETKEYS['sensenova']):
        self._key="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyWVo5RUdQTjVmbXNCN1pQNUhMUEw2NWE3ekwiLCJleHAiOjE3MTg3MjI3MjQsIm5iZiI6MTcwMDcyMjcxOX0.KpCb8vB_DLCa0aNZuTyOUywhsszPmOpedppEYm0sFF8"

    def __call__(self,
                 prompt,
                 model= "nova-ptc-xl-v1", # "nova-ptc-xl-v2-1-0-8k-internal",
                 temperature=0.1,
                 top_p=0.9,
                 max_new_tokens=256,
                 repetition_penalty=1.05,
                 stream=False,
                 *args, **kwargs):
        #替换敏感词
        prompt_desen=prompt.replace('Master', 'Bachelor')
        # print('-*-S'*20)
        # print(f"SenseNova Prompt:\n{prompt_desen}")
        # print('--' * 30+' Fin Prompt ')

        url = 'https://api.sensenova.cn/v1/llm/chat-completions'
        data = {
            "model":model,
            "messages": [{"role": "user", "content": prompt_desen}],
            "temperature": temperature,
            "top_p": top_p,
            "max_new_tokens": max_new_tokens,
            "repetition_penalty": repetition_penalty,
            "stream": stream
        }
        time.sleep(4)
        ans = requests.post(url, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._key},
                            json=data)
        if ans.text:
            try:
                ans_text=json.loads(ans.text)

            except:
                raise Exception('Response can not be parsed !')

            if 'data' in ans_text:
                if 'choices' in ans_text['data']:
                    prompt_out=ans_text['data']['choices'][0]['message']
                    # print(f"SenseNova Answer:\n{prompt_out}")
                    # print('-*-E' * 20)
                    return prompt_out
                else:
                    raise Exception(ans_text)
            else:
                raise Exception(ans_text)
        else:
            raise Exception('No response returned by SenseNova !')


if __name__=='__main__':
    llm=SenseNova()
    # print(llm('请用一句话解释万有引力',model='nova-ptc-xl-v1',max_new_tokens=512))

    prompt='''Complete sqlite SQL query only and with no explanation.

DATABASE:
Table enterprise_finance_report_month, columns = [*, company_name, accounting_year_month, index_name, this_year, last_year, this_year_budget, this_month, completion_rate, change_last_year, year_on_year, this_year_start, compared_beginning_year, year_to_date, last_month, compared_last_year, change_rate_last1M_this_year]
Table ha02_cmft_person_info_wide, columns = [*, year, belong_day, company, leader_name, emplid, aes_emplid, name, sex, phone, birthdate, age, age_type, level_1, level_1_name, level_2, level_2_name, level_2_managername, level_3, level_3_name, level_3_managername, action, action_dt_start, eff_status, last_entry_dt, cmpny_seniority_dt, start_entry_dt, birthcountry, birthplace, school_descr, education, age_cmp, age_job, natiion, recruit_mode, jobcode, company_selft_jobdescr, supv_lvl_id, c_sta_supv_lvl, c_grp_supv_lvl, position_sequence_code, position_sequence_name, position_sequence_code_sub, position_sequence_name_sub, DW_Etl_Dt, DW_Etl_Tm, DW_Ins_Dt, DW_Ins_Tm]
Table ha02_cmft_people_org_relation, columns = [*, id, org_id, org_name, parent_org_id, virtual_parent_org_id, company_id, level]
Table ha02_cmft_personnel_performance, columns = [*, year, emplid, name, level_1, level_1_name, level_2, level_2_name, level_3, level_3_name, score]
Table ads_index_wall, columns = [*, sum_month, index_name, index_value, unit_value, org_name, budget_complete, year_over_year, ing_ratio, kpi_rate]

金科员工的平均年龄是多少?
SELECT'''
    print(llm(prompt=prompt,max_new_tokens=256))
