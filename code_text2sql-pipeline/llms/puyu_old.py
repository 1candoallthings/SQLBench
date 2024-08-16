import requests
import ast
import time
import jsonlines
import requests
import json
import time


class Puyu:
    def __init__(self):
        pass

    def __call__(self,
                 prompt,
                 model="nova-ptc-xl-v1",  # "nova-ptc-xl-v2-1-0-8k-internal",
                 temperature=0.1,
                 top_p=0.9,
                 max_new_tokens=256,
                 repetition_penalty=1.05,
                 stream=False,
                 *args, **kwargs):
        # 替换敏感词
        prompt_desen = prompt.replace('Master', 'Bachelor')
        # print('-*-S'*20)
        # print(f"Puyu Prompt:\n{prompt_desen}")
        # print('--' * 30+' Fin Prompt ')

        url = 'http://euclid-70b.mtc.sensetime.com/'
        context = "<|User|>:" + prompt + "\n<|Bot|>:"
        data = {
            "inputs": context,
            "parameters": {
                "do_sample": False,
                "temperature": temperature,
                "top_p": top_p,
                "max_new_tokens": max_new_tokens,
                "repetition_penalty": repetition_penalty,
            }
        }
        Flag = 1
        headers = {
            'Content-Type': 'application/json'
        }
        while Flag:
            time.sleep(0.3)
            response = requests.post(url, headers=headers, json=data)
            tmp = ast.literal_eval(response.text)
            if 'generated_text' in response.text:
                item = tmp[0]['generated_text']
                Flag = 0
        return item
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


if __name__ == '__main__':
    llm = Puyu()
    print("你是什么语言模型?")
    print(llm("""你是一个策略专家，擅长把复杂问题尽可能的拆分为多个简单的子问题。
我会给你一个问题，你需要充分理解问题的内容，并结合背景信息把问题尽可能的拆分为多个子问题，注意保持前后的逻辑关系。
     
下面是参考案例：
question:参考上海市落户人口总量数据，去年上海市通过落户政策落户了多少人？并分析下这种趋势。
child_01:上海市2022年落户人口的总量是多少？
child_02:上海市2022年人才类落户数量是多少？
child_03:上海市2022年刚性政策类数量是多少？
child_04:上海市2022年人才落户数量占总落户数量的百分比是多少？
child_04:根据上述数据，分析下落户政策的趋势。

question:分析下北京市落户的变化趋势。
child_01:查询下北京2022年落户人口的数据是多少？
child_02:查询下北京2021年落户人口的数据是多少？
child_03:查询下北京2022年落户人口的数据比2021年差值是多少？
child_04:根据以上数据，分析下北京市落户人口的变化趋势。
     
注意：
1.上海市的落户渠道分为人才类落户和刚性政策类落户两种；其中人才类落户的渠道包含居转户及家属随迁、直接引进及家属随迁、留学回国及家属随迁、非沪籍应届毕业落户。 
2.今年是2023年，过去五年分别是2022年、2021年、2020年、2019年和2018年，关于增长类的数据一般是对比今年比去年的数据增长了多少。
3.关于趋势分析类的问题需要计算数据的差值并进行对比，比如今年的数据需要跟去年的数据作对比。

下面正式开始，问题是：参考上海市落户人口总量数据，去年上海市通过落户政策落户了多少人？"""))
    # from multiprocessing import Pool
    #
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



