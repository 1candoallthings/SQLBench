# SQLBench TEXT2SQL


```python
from utils.sensenova import SenseNova
llm=SenseNova()
prompt='''Complete sqlite SQL query only and with no explanation.

DATABASE:
Table enterprise_finance_report_month, columns = [*, company_name, accounting_year_month, index_name, this_year, last_year, this_year_budget, this_month, completion_rate, change_last_year, year_on_year, this_year_start, compared_beginning_year, year_to_date, last_month, compared_last_year, change_rate_last1M_this_year]
Table ha02_cmft_person_info_wide, columns = [*, year, belong_day, company, leader_name, emplid, aes_emplid, name, sex, phone, birthdate, age, age_type, level_1, level_1_name, level_2, level_2_name, level_2_managername, level_3, level_3_name, level_3_managername, action, action_dt_start, eff_status, last_entry_dt, cmpny_seniority_dt, start_entry_dt, birthcountry, birthplace, school_descr, education, age_cmp, age_job, natiion, recruit_mode, jobcode, company_selft_jobdescr, supv_lvl_id, c_sta_supv_lvl, c_grp_supv_lvl, position_sequence_code, position_sequence_name, position_sequence_code_sub, position_sequence_name_sub, DW_Etl_Dt, DW_Etl_Tm, DW_Ins_Dt, DW_Ins_Tm]
Table ha02_cmft_people_org_relation, columns = [*, id, org_id, org_name, parent_org_id, virtual_parent_org_id, company_id, level]
Table ha02_cmft_personnel_performance, columns = [*, year, emplid, name, level_1, level_1_name, level_2, level_2_name, level_3, level_3_name, score]
Table ads_index_wall, columns = [*, sum_month, index_name, index_value, unit_value, org_name, budget_complete, year_over_year, ing_ratio, kpi_rate]

金科员工的平均年龄是多少?
SELECT'''
ans=llm(prompt=prompt, model='nova-ptc-xl-v1',max_new_tokens=512)
print(ans)
```

## SQLexec
```python
from utils.sql_exec import query_db
ans=query_db('activity_1', 'SELECT * from Student')
print(ans)
```

## Text2SQL Planning
```python
from models.flexsql2 import run_text2sql

test_sample_path = "cache/unit_ppl_test.json"
output_file="cache/unit_ppl_test_filled.json"

run_text2sql(test_sample_path,output_file)
# see output file
```


## Text2SQL Eval
+ target_name is the name of key/column  
```python
from utils.auto_eval import eval_text2sql_once,eval_text2sql_step_by_step

# 不关注每道题的对错，得到整体统计指标
# 结果在output_dir的scores_once.log中
eval_text2sql_once("./cache/unit_ppl_test_filled_example.json",target_name='init_sql',output_dir="./cache")

# 关注每道题的对错，除了整体统计指标还有单题正确错误信息，速度较慢
# 结果在output_dir的scores.log和scores.csv中
eval_text2sql_step_by_step("./cache/unit_ppl_test_filled_example.json",target_name='init_sql',output_dir="./cache")

```