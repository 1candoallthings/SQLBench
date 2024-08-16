import requests
import ast
import time
import jsonlines
import requests
import json
import time


class PuyuNew:
    def __init__(self):
        pass

    def __call__(self,
                 prompt,
                 # model= "nova-ptc-xl-v1", # "nova-ptc-xl-v2-1-0-8k-internal",
                 temperature=0.001,
                 top_p=0.9,
                 max_new_tokens=256,
                 repetition_penalty=1.05,
                 stream=False,
                 *args, **kwargs):
        #替换敏感词
        prompt_desen=prompt.replace('Master', 'Bachelor')
        # print('-*-S'*20)
        # print(f"Puyu Prompt:\n{prompt_desen}")
        # print('--' * 30+' Fin Prompt ')

        url = 'http://cluster-proxy.sh.sensetime.com:20055/generate'
        # context = "<|User|>:"+prompt+"\n<|Bot|>:"
        data = {
            "inputs": prompt,
            "parameters": {
                "do_sample": True,
                "temperature": temperature,
                "top_p": top_p,
                "max_new_tokens": max_new_tokens,
                "repetition_penalty": repetition_penalty,
            }
        }
        response = requests.post(url, json=data)

        time.sleep(0.1)
        if response.status_code == 200:
            try:
                res = response.json()
            except:
                raise Exception('Response can not be parsed !')

            return res["generated_text"][0].rstrip("</s>")
        else:
            raise Exception('No response returned by SenseNova !')
        # if ans.text:
        #     try:
        #         ans_text=json.loads(ans.text)

        #     except:
        #         raise Exception('Response can not be parsed !')

        #     if 'data' in ans_text:
        #         if 'choices' in ans_text['data']:
        #             prompt_out=ans_text['data']['choices'][0]['message']
        #             print(f"SenseNova Answer:\n{prompt_out}")
        #             print('-*-E' * 20)
        #             return prompt_out
        #         else:
        #             raise Exception(ans_text)
        #     else:
        #         raise Exception(ans_text)
        # else:
        #     raise Exception('No response returned by SenseNova !')


if __name__=='__main__':
    llm=PuyuNew()
    print(llm('请用一句话解释万有引力', max_new_tokens=512))
    # from multiprocessing import Pool 
    # pool = Pool(1)
    # print(list(pool.map(llm, ['写python快排函数'])))
#     prompt='''Complete sqlite SQL query only and with no explanation.

# DATABASE:
# Table enterprise_finance_report_month, columns = [*, company_name, accounting_year_month, index_name, this_year, last_year, this_year_budget, this_month, completion_rate, change_last_year, year_on_year, this_year_start, compared_beginning_year, year_to_date, last_month, compared_last_year, change_rate_last1M_this_year]
# Table ha02_cmft_person_info_wide, columns = [*, year, belong_day, company, leader_name, emplid, aes_emplid, name, sex, phone, birthdate, age, age_type, level_1, level_1_name, level_2, level_2_name, level_2_managername, level_3, level_3_name, level_3_managername, action, action_dt_start, eff_status, last_entry_dt, cmpny_seniority_dt, start_entry_dt, birthcountry, birthplace, school_descr, education, age_cmp, age_job, natiion, recruit_mode, jobcode, company_selft_jobdescr, supv_lvl_id, c_sta_supv_lvl, c_grp_supv_lvl, position_sequence_code, position_sequence_name, position_sequence_code_sub, position_sequence_name_sub, DW_Etl_Dt, DW_Etl_Tm, DW_Ins_Dt, DW_Ins_Tm]
# Table ha02_cmft_people_org_relation, columns = [*, id, org_id, org_name, parent_org_id, virtual_parent_org_id, company_id, level]
# Table ha02_cmft_personnel_performance, columns = [*, year, emplid, name, level_1, level_1_name, level_2, level_2_name, level_3, level_3_name, score]
# Table ads_index_wall, columns = [*, sum_month, index_name, index_value, unit_value, org_name, budget_complete, year_over_year, ing_ratio, kpi_rate]

# 金科员工的平均年龄是多少?
# SELECT'''
#     print(llm(prompt=prompt,max_new_tokens=256))



# idx= 0


# headers = {
#     'Content-Type': 'application/json'
#     }
# item = {}
# item["instruction"] = ''
# context = "<|User|>:"+item["instruction"]+"\n<|Bot|>:"

# data = {
#             "inputs": context,
#             "parameters": {
#                 "do_sample": False,
#                 "max_new_tokens": 1024
#             }
#         } 

 

