import requests
import time


prompt_template ="""<s><|im_start|>system
You are an AI assistant whose name is InternLM (书生·浦语).
- InternLM (书生·浦语) is a conversational language model that is developed by Shanghai AI Laboratory (上海人工智能实验室). It is designed to be helpful, honest, and harmless.
- InternLM (书生·浦语) can understand and communicate fluently in the language chosen by the user such as English and 中文.<|im_end|>
<|im_start|>user
{text}<|im_end|>
<|im_start|>assistant"""


class Internlm2_Gauss_sft_notemplete:
    def __init__(self):
        pass

    def __call__(self,
                 prompt,
                 core_pod_ip='10.119.63.99',
                 temperature=0.001,
                 top_p=0.9,
                 max_new_tokens=256,
                 repetition_penalty=1.05,
                 stream=False,
                 *args, **kwargs):

        server = "http://101.230.144.204:8008/api/generate"
        headers = {"Content-Type": "application/json"}
        endpoint = f"http://{core_pod_ip}:2345/generate"  # cci tgi-gpu8

        # inputs = prompt_template.format_map({"text":prompt})
        inputs = prompt

        request_body = {
            "endpoint": endpoint,
            "inputs": inputs,
            "parameters": {
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": True,
                "max_new_tokens": max_new_tokens,
                "top_k": 1,
                "repetition_penalty": repetition_penalty,
                "stop": [
                #  "</s>",
                #  "User:",
                ]
            }
        }
        response = requests.post(server, headers=headers, json=request_body, stream=stream)
        # print(response)
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


if __name__=='__main__':
    prompt = """### 只通过sqlite SQL查询回答问题，不做任何解释。
### Sqlite SQL表及其属性：
#
# 积分报表信息(`工号`, `姓名`, `机构`, `部门`, `岗位`, `考核积分`);
# 员工点位信息(`工号`, `时间`, `经度`, `纬度`, `地址`, `备注`);
# 预警信息(`预警流水号`, `工号`, `员工姓名`, `状态`, `下发时间`, `逾期时间(含)`, `机构`, `预警时间`, `预警是否准确`, `部门`, `预警名称`, `预警级别`, `首次反馈时间`, `反馈时间`, `核查情况`, `是否超时`, `流程节点`, `是否存在问题`, `风险等级`, `回退次数`, `疑点类型`, `处置措施`);
# 离职人员名单(`工号`, `姓名`, `机构`, `部门`, `岗位`, `员工状态`, `离职日期`, `员工类别`);
# 访客记录(`上传人工号 `, `上传人姓名`, `组织机构`, `上传时间`, `员工位置`, `访客类型`, `备注信息`, `陪同人上传`, `直属上级名称`, `直属上级工号`, `是否被阅`, `被阅时间`, `是否T+1日内查阅`, `系统筛查结果`, `原因`, `手工筛查结果`, `备注`, `设备ID`, `客户类型`, `客户名称`, `营销产品`, `条线`, `渠道相关`, `陪同人`, `特殊类型`, `异常类型`, `异常原因`, `上传人工号`);
# 打卡记录(`工号`, `姓名`, `机构`, `部门`, `岗位`, `打卡日期`, `打卡时间`, `考勤机编号`, `打卡类型`, `补签卡`, `补签原因`, `上传时间`)
#
### 以下是有关数据库引用的一些示例数据信息。
#
# 积分报表信息(`工号`[000008,000008,000048], `姓名`[龚琛琛,龚琛琛,徐君], `机构`[三江支行,段塘支行,宁穿支行], `部门`[海曙支行三江支行个人银行部,海曙支行段塘支行个人银行部,鄞州中心区支行宁穿支行行长室], `岗位`[个人银行业务经理,贵宾理财经理,支行行长], `考核积分`[.2,.25,1]);
# 员工点位信息(`工号`[xxxxxx,xxxxxx,xxxxxx], `时间`[2024-02-22 09:14:27,2024-02-22 09:14:28,2024-02-22 09:14:29], `经度`[121.50728,121.50728,121.50727], `纬度`[31.24172,31.241716,31.24173], `地址`[上海市浦东新区银城中路8号靠近海银金融中心,上海市浦东新区银城中路9号靠近海银金融中心,上海市浦东新区银城中路10号靠近海银金融中心], `备注`[APP重启Wif定位结果:正常获取定位度:30.02G网络 当前网络正常使用,Wif定位结果:正常获联定位精度:3002G网络当前网络正常使用,Wi定位结果正常获取定位精度:30.02G网络当前网络正常使用]);
# 预警信息(`预警流水号`[20230629010000001611,20230629010000000793,20230628010000000034], `工号`[190582,225136,152946], \
`员工姓名`[王桢,李小雪,陈瑞娇], `状态`[待阅,待阅,待阅], `下发时间`[2023-06-30 00:00:00,2023-06-30 00:00:01,2023-06-29 00:00:02],\
 `逾期时间(含)`[,,], `机构`[上海张江支行,宁银消金,上海张江支行], `预警时间`[2023-06-30 00:00:00,2023-06-30 00:00:01,2023-06-29 00:00:02], `预警是否准确`[,,], `部门`[支行财富管理部,业务部-业务三部,支行公司业务二部], `预警名称`[访客对象为员工关系人,上传访客时间间隔过短,特殊时段访客], `预警级别`[黄,黄,黄], `首次反馈时间`[,,], `反馈时间`[,,], `核查情况`[,,], `是否超时`[否,否,否], `流程节点`[,,], `是否存在问题`[否,否,否], `风险等级`[无风险,无风险,无风险], `回退次数`[0,0,0], `疑点类型`[,,], `处置措施`[,,]);
# 离职人员名单(`工号`[182128,170687,183831], `姓名`[张鸿雁,沈佳晨,司慧], `机构`[上海分行,上海分行,上海分行], `部门`[上海分行风险管理部-回访部,上海分行个人银行总部-总经理室,上海分行财富管理部-投资顾问部], `岗位`[回访岗,个人银行总部副总经理,投资顾问尚], `员工状态`[离职,离职,离职], `离职日期`[2023-10-23 00:00:00,2023-09-08 00:00:00,2023-04-06 00:00:00], `员工类别`[正式工,正式工,正式工]);
# 访客记录(`上传人工号 `[None,None,None], `上传人姓名`[何佳凝,王扶摇,杨维诚], `组织机构`[普陀支行个人,信用卡中心-业务,普陀支行个人], \
`上传时间`[2023-03-31 21:18:05,2023-03-31 20:50:05,2023-03-31 20:48:56], `员工位置`[普陀区岚皋路567号,真如镇街道铜川路,川路68号弘基时尚], \
`访客类型`[新客户营销,其它,新客户营销], `备注信息`[,,], `陪同人上传`[否,否,否], `直属上级名称`[李珊珊,姚瑶,李姗姗], `直属上级工号`[180205,190969,180205], `是否被阅`[是,是,是], `被阅时间`[2023-03-31 21:18:05,2023-03-31 20:50:05,2023-03-31 20:48:56], `是否T+1日内查阅`[是,是,是], `系统筛查结果`[不匹配,不匹配,不匹配], `原因`[有记录无安排,有记录无安排,有记录无安排], `手工筛查结果`[未筛查,未筛查,未筛查], `备注`[,,], `设备ID`[8735b6ae8,41a7-a506,032359c2], `客户类型`[个人,,个人], `客户名称`[张女士,,张辉], `营销产品`[按揭,,按揭], `条线`[个人银行业务,信用卡业务,个人银行业务], `渠道相关`[,,], `陪同人`[,,], `特殊类型`[正常,正常,正常], `异常类型`[工作时间段访,工作时间段访,工作时间段访], `异常原因`[,,], `上传人工号`[225846,221841,226781]);
# 打卡记录(`工号`[160659,160659,050148], `姓名`[唐希龙,唐希龙,方圆], `机构`[上海分行,上海分行,上海分行], `部门`[行长室,行长室,行长室], `岗位`[分行副行长,分行副行长,分行副行长], `打卡日期`[2024年2月1日,2024年2月1日,2024年2月1日], `打卡时间`[08:04:50,18:48:49,08:02:48], `考勤机编号`[11.21.148.22,11.21.148.23,11.21.148.24], `打卡类型`[人脸考勤,人脸考勤,人脸考勤], `补签卡`[,,], `补签原因`[,,], `上传时间`[2024年2月1日8:04:50,2024年2月1日18:48:49,2024年2月1日8:02:48])
#
### 以下是生成SQL语句需要注意的地方：
#
# 注意，上下班时间可以通过查询打卡时间来确定；
# 注意，10:00在查询时需要用“10:00:00”表示；
# 注意，查询员工需要查询员工的姓名或者是上传人姓名；
# 注意，问题中出现比如“2021年5月份期间”，则需表示为“2021-05-01 00:00:00到2021-05-31 23:59:59”。
#
### 问题是: 查询下哪个员工下班时间最晚？
### SQL: """
    # prompt = "tell me a story, 尽量有意思一些，关于人工智能。"
    # prompt = "写一个快速排序算法，并生成简单测试用例测试结果"
    # prompt = "tell me a story with sql? 写一个sql查询语句，查询整个学校有多少人的年龄大于平均年龄。"
    prompt01 = """
    ### Answer the question by sqlite SQL query only and with no explanation.
    ### Sqlite SQL tables, with their properties:
    #
    # Basic_Info(Stk_Code, Stk_Name);
    # Balance_Sheet(Stk_Code, Cash_CB, IB_Deposits, Prec_Metals, Lending_Funds, Trad_FAs, Deriv_Assets, Buyback_FAs, Int_Receiv, Loans_Adv, Avail_Sale_FAs, Held_Mat_Invest, Recv_Invest, LT_Eq_Invest, Inv_Real_Estate, Fix_Assets, Intang_Assets, Def_IT_Assets, Oth_Assets, Tot_Assets, Bor_CB, IB_Dep_Oth_FIs, Bor_Funds_Oth_FIs, Trad_Fin_Liab, Deriv_Liab, Sell_Rep_FAs, Acc_Deposits, Emp_Comp_PAY, Tax_Pay, Int_Pay, Est_Liab, Bonds_PAY, Def_IT_Liab, Oth_Liab, Tot_Liab, Paid_Up_Cap, Cap_Reserves, Treas_Stock, Sur_Reserves, Gen_Risk_Res, Undist_Profits, Exch_Diff_Cash, Own_Eq_Attr_Parent, Minor_Int_Eq, Tot_Own_Eq, Tot_Liab_Own_Eq);
    # Income_Statement(Stk_Code, Oper_Rev, Net_Int_Inc, Int_Inc, Int_Exp, Fee_Com_Net_Inc, Fee_Com_Inc, Fee_Com_Exp, Inv_Inc, Inv_Inc_Assoc_JV, FV_Change_Inc, Exch_Gain_Inc, Oth_Biz_Inc, Oper_Exp, Tax_n_Surs, Gen_n_Admin_Exps, Assets_Imp_Loss, Oth_Biz_Costs, Oper_Profit, Non_Op_Rev, Non_Op_Exp, Loss_Disposal_Nonc_Assets, Tot_Profit, Income_Tax_Exp, Net_Profit, Attr_Parent_Net_Profit, Minor_Int_Inc_Loss, Basic_EPS, Diluted_EPS, Oth_Compre_Inc, Tot_Compre_Inc, Attr_Parent_Shareholders_Compre_Inc, Minor_Int_Shareholders_Compre_Inc);
    # Cash_Flow_Statement(Stk_Code, Net_Inc_Cust_Deposits_IB_Deposits, Net_Inc_Borrowings_CB, Net_Inc_IB_Borrowings, Cash_Int_Commission_Collected, Cash_Oth_Oper_Activities, Op_CF_Sub, Cust_Loans_Net_Inc, CenBank_Interbank_Net_Inc, Cash_Pay_Int_Fees_Com, Cash_Pay_Emp, Cash_Pay_Taxes, Cash_Pay_Op_Other, Op_CF_Out_Sub, Net_CF_Op, Recv_Investment, Investment_Income, Cash_Disposal_Assets, Recv_Other_Invest, Inv_CF_In_Sub, Cash_Pay_Invest, Cash_Pay_Assets, Cash_Pay_Inv_Other, Inv_CF_Out_Sub, Net_CF_Inv, Absorb_Investment, Subsidiary_Absorb_Minority, Issue_Bonds, Recv_Other_Fin, Fin_CF_In_Sub, Repay_Debt, Distribute_Dividends_Profits, Subsidiary_Pay_Minority, Cash_Pay_Fin_Other, Fin_CF_Out_Sub, Net_CF_Fin, FX_Rate_Change_Cash, Net_CF_Cash_Equiv, Initial_Cash_Equiv, Final_Cash_Equiv, CF_Stmt_Net_Income, Asset_Impairment_Dec, Fixed_Asset_Dep_Amort_Dec, Intangible_Asset_Amortization, Longterm_Amortization, Loss_Disposal_Fixed_Assets_Dec, Fixed_Asset_Scrap_Loss, Fair_Value_Change_Loss, CF_Stmt_Fin_Expenses, Investment_Loss, DIT_Asset_Reduction, DIT_Liability_Increase, Inventory_Decrease, Oper_Receivables_Decrease, Oper_Payables_Increase, Other, IM_NCF_Oper_Activities, Debt_Converted_Capital, Conv_Bonds_Maturing_Within_1Y, Fin_Lease_Additions_Fixed_Assets, Cash_End_Period, Cash_Begin_Period, Cash_Eq_End_Period, Cash_Eq_Begin_Period, IM_NCF_Cash_Eq)
    #
    ### Here are some data information about database references.
    #
    # Basic_Info(Stk_Code[600000.SH,600015.SH,600016.SH], Stk_Name[Shanghai Pudong Development Bank,Huaxia Bank,China Mingsheng Bank]);
    # Balance_Sheet(Stk_Code[600000.SH,600015.SH,600016.SH], Cash_CB[411019000000.0,176103000000.0,354899000000.0], IB_Deposits[147145000000.0,16293000000.0,114630000000.0], Prec_Metals[834000000.0,None,27993000000.0], Lending_Funds[393759000000.0,49776000000.0,188526000000.0], Trad_FAs[740222000000.0,425245000000.0,386582000000.0], Deriv_Assets[70837000000.0,9492000000.0,40635000000.0], Buyback_FAs[75358000000.0,31459000000.0,10025000000.0], Int_Receiv[None,None,None], Loans_Adv[4866904000000.0,2285717000000.0,4322267000000.0], Avail_Sale_FAs[None,None,None], Held_Mat_Invest[None,None,None], Recv_Invest[None,None,None], LT_Eq_Invest[2795000000.0,None,None], Inv_Real_Estate[None,None,None], Fix_Assets[42004000000.0,43055000000.0,50856000000.0], Intang_Assets[9958000000.0,1759000000.0,5739000000.0], Def_IT_Assets[64585000000.0,11907000000.0,56977000000.0], Oth_Assets[145910000000.0,31365000000.0,43087000000.0], Tot_Assets[8932519000000.0,4098550000000.0,7641451000000.0], Bor_CB[202042000000.0,137465000000.0,180971000000.0], IB_Dep_Oth_FIs[783188000000.0,586667000000.0,1426046000000.0], Bor_Funds_Oth_FIs[340630000000.0,183053000000.0,106646000000.0], Trad_Fin_Liab[14920000000.0,None,20506000000.0], Deriv_Liab[62341000000.0,9014000000.0,41844000000.0], Sell_Rep_FAs[373094000000.0,83045000000.0,131663000000.0], Acc_Deposits[5069529000000.0,2168881000000.0,4300243000000.0], Emp_Comp_PAY[7367000000.0,8047000000.0,11341000000.0], Tax_Pay[20503000000.0,3963000000.0,8161000000.0], Int_Pay[None,None,None], Est_Liab[6541000000.0,2035000000.0,2345000000.0], Bonds_PAY[1272371000000.0,581062000000.0,628199000000.0], Def_IT_Liab[641000000.0,None,242000000.0], Oth_Liab[50840000000.0,21950000000.0,38747000000.0], Tot_Liab[8211439000000.0,3790933000000.0,7014760000000.0], Paid_Up_Cap[29352000000.0,15915000000.0,43782000000.0], Cap_Reserves[81762000000.0,60737000000.0,58149000000.0], Treas_Stock[None,None,None], Sur_Reserves[188929000000.0,24119000000.0,55276000000.0], Gen_Risk_Res[101496000000.0,48747000000.0,90673000000.0], Undist_Profits[199479000000.0,115670000000.0,268624000000.0], Exch_Diff_Cash[None,None,None], Own_Eq_Attr_Parent[713100000000.0,304639000000.0,613419000000.0], Minor_Int_Eq[7980000000.0,2978000000.0,13272000000.0], Tot_Own_Eq[721080000000.0,307617000000.0,626691000000.0], Tot_Liab_Own_Eq[8932519000000.0,4098550000000.0,7641451000000.0]);
    # Income_Statement(Stk_Code[600000.SH,600015.SH,600016.SH], Oper_Rev[91230000000.0,47642000000.0,71539000000.0], Net_Int_Inc[60428000000.0,34151000000.0,51334000000.0], Int_Inc[150294000000.0,75794000000.0,133080000000.0], Int_Exp[89866000000.0,41643000000.0,81746000000.0], Fee_Com_Net_Inc[13962000000.0,3667000000.0,10836000000.0], Fee_Com_Inc[17520000000.0,6044000000.0,13441000000.0], Fee_Com_Exp[3558000000.0,2377000000.0,2605000000.0], Inv_Inc[13757000000.0,3656000000.0,8976000000.0], Inv_Inc_Assoc_JV[138000000.0,None,None], FV_Change_Inc[4319000000.0,4223000000.0,-2413000000.0], Exch_Gain_Inc[-3155000000.0,459000000.0,-106000000.0], Oth_Biz_Inc[1283000000.0,1376000000.0,2447000000.0], Oper_Exp[64652000000.0,31273000000.0,46748000000.0], Tax_n_Surs[1051000000.0,534000000.0,1043000000.0], Gen_n_Admin_Exps[24257000000.0,13287000000.0,21136000000.0], Assets_Imp_Loss[49000000.0,230000000.0,732000000.0], Oth_Biz_Costs[857000000.0,539000000.0,1627000000.0], Oper_Profit[26578000000.0,16369000000.0,24791000000.0], Non_Op_Rev[26000000.0,78000000.0,64000000.0], Non_Op_Exp[37000000.0,37000000.0,108000000.0], Loss_Disposal_Nonc_Assets[None,None,None], Tot_Profit[26567000000.0,16410000000.0,24747000000.0], Income_Tax_Exp[2952000000.0,4045000000.0,775000000.0], Net_Profit[23615000000.0,12365000000.0,23972000000.0], Attr_Parent_Net_Profit[23138000000.0,12114000000.0,23777000000.0], Minor_Int_Inc_Loss[477000000.0,251000000.0,195000000.0], Basic_EPS[0.76,0.58,0.46], Diluted_EPS[0.7,None,0.46], Oth_Compre_Inc[2258000000.0,1039000000.0,2721000000.0], Tot_Compre_Inc[25873000000.0,13404000000.0,26693000000.0], Attr_Parent_Shareholders_Compre_Inc[25343000000.0,13153000000.0,26302000000.0], Minor_Int_Shareholders_Compre_Inc[530000000.0,251000000.0,391000000.0]);
    # Cash_Flow_Statement(Stk_Code[600000.SH,600015.SH,600016.SH], Net_Inc_Cust_Deposits_IB_Deposits[185841000000.0,97042000000.0,289359000000.0], Net_Inc_Borrowings_CB[35502000000.0,35172000000.0,35776000000.0], Net_Inc_IB_Borrowings[None,None,None], Cash_Int_Commission_Collected[142928000000.0,66973000000.0,118670000000.0], Cash_Oth_Oper_Activities[8313000000.0,3824000000.0,28913000000.0], Op_CF_Sub[401985000000.0,246937000000.0,528276000000.0], Cust_Loans_Net_Inc[98383000000.0,82234000000.0,265774000000.0], CenBank_Interbank_Net_Inc[None,None,None], Cash_Pay_Int_Fees_Com[71825000000.0,36310000000.0,72398000000.0], Cash_Pay_Emp[19183000000.0,6951000000.0,16499000000.0], Cash_Pay_Taxes[19612000000.0,11776000000.0,10461000000.0], Cash_Pay_Op_Other[95779000000.0,9279000000.0,19680000000.0], Op_CF_Out_Sub[353499000000.0,172792000000.0,419645000000.0], Net_CF_Op[48486000000.0,74145000000.0,108631000000.0], Recv_Investment[842680000000.0,197103000000.0,797720000000.0], Investment_Income[50032000000.0,20864000000.0,35407000000.0], Cash_Disposal_Assets[None,13000000.0,920000000.0], Recv_Other_Invest[503000000.0,None,None], Inv_CF_In_Sub[893215000000.0,217980000000.0,834047000000.0], Cash_Pay_Invest[950682000000.0,316981000000.0,833348000000.0], Cash_Pay_Assets[4674000000.0,18750000000.0,3392000000.0], Cash_Pay_Inv_Other[None,None,None], Inv_CF_Out_Sub[955356000000.0,335731000000.0,836740000000.0], Net_CF_Inv[-62141000000.0,-117751000000.0,-2693000000.0], Absorb_Investment[None,None,None], Subsidiary_Absorb_Minority[None,None,None], Issue_Bonds[612774000000.0,70000000000.0,506253000000.0], Recv_Other_Fin[None,None,None], Fin_CF_In_Sub[612774000000.0,70000000000.0,506253000000.0], Repay_Debt[672761000000.0,10000000000.0,530375000000.0], Distribute_Dividends_Profits[16948000000.0,11854000000.0,15470000000.0], Subsidiary_Pay_Minority[None,None,None], Cash_Pay_Fin_Other[1646000000.0,None,1822000000.0], Fin_CF_Out_Sub[691355000000.0,42937000000.0,547670000000.0], Net_CF_Fin[-78581000000.0,27063000000.0,-41417000000.0], FX_Rate_Change_Cash[3958000000.0,610000000.0,1646000000.0], Net_CF_Cash_Equiv[-88278000000.0,-15933000000.0,66167000000.0], Initial_Cash_Equiv[372304000000.0,87707000000.0,128305000000.0], Final_Cash_Equiv[284026000000.0,71774000000.0,194472000000.0], CF_Stmt_Net_Income[23615000000.0,12365000000.0,23972000000.0], Asset_Impairment_Dec[49000000.0,230000000.0,732000000.0], Fixed_Asset_Dep_Amort_Dec[4399000000.0,1906000000.0,4137000000.0], Intangible_Asset_Amortization[None,21000000.0,None], Longterm_Amortization[None,632000000.0,None], Loss_Disposal_Fixed_Assets_Dec[-83000000.0,-6000000.0,28000000.0], Fixed_Asset_Scrap_Loss[None,None,None], Fair_Value_Change_Loss[-4319000000.0,None,2413000000.0], CF_Stmt_Fin_Expenses[None,None,None], Investment_Loss[-11281000000.0,None,-4910000000.0], DIT_Asset_Reduction[3334000000.0,None,-1957000000.0], DIT_Liability_Increase[None,None,None], Inventory_Decrease[None,None,None], Oper_Receivables_Decrease[-245794000000.0,-87024000000.0,-303177000000.0], Oper_Payables_Increase[252407000000.0,150890000000.0,386459000000.0], Other[None,None,None], IM_NCF_Oper_Activities[48486000000.0,74145000000.0,108631000000.0], Debt_Converted_Capital[None,None,None], Conv_Bonds_Maturing_Within_1Y[None,None,None], Fin_Lease_Additions_Fixed_Assets[None,None,None], Cash_End_Period[284026000000.0,71774000000.0,194472000000.0], Cash_Begin_Period[372304000000.0,87707000000.0,128305000000.0], Cash_Eq_End_Period[None,None,None], Cash_Eq_Begin_Period[None,None,None], IM_NCF_Cash_Eq[-88278000000.0,-15933000000.0,66167000000.0])
    #
    ### Foreign key information of Sqlite SQL tables, used for table joins: 
    #
    # Balance_Sheet(Stk_Code) references Basic_Info(Stk_Code);
    # Income_Statement(Stk_Code) references Basic_Info(Stk_Code);
    # Cash_Flow_Statement(Stk_Code) references Basic_Info(Stk_Code)
    #
    ### Question: 找出与运营中的其他活动有关的现金流入。
    ### SQL: 
    <|Bot|>:", parameters: GenerateParameters { best_of: None, temperature: Some(0.001), repetition_penalty: Some(1.05), frequency_penalty: None, presence_penalty: None, top_k: Some(1), top_p: Some(0.9), typical_p: None, do_sample: true, max_new_tokens: 256, return_full_text: None, stop: [], truncate: None, watermark: false, details: false, decoder_input_details: false, seed: None } }}:generate_stream{request=GenerateRequest { inputs: "<|User|>:### Answer the question by sqlite SQL query only and with no explanation.
    ### Sqlite SQL tables, with their properties:
    #
    # Basic_Info(Stk_Code, Stk_Name);
    # Balance_Sheet(Stk_Code, Cash_CB, IB_Deposits, Prec_Metals, Lending_Funds, Trad_FAs, Deriv_Assets, Buyback_FAs, Int_Receiv, Loans_Adv, Avail_Sale_FAs, Held_Mat_Invest, Recv_Invest, LT_Eq_Invest, Inv_Real_Estate, Fix_Assets, Intang_Assets, Def_IT_Assets, Oth_Assets, Tot_Assets, Bor_CB, IB_Dep_Oth_FIs, Bor_Funds_Oth_FIs, Trad_Fin_Liab, Deriv_Liab, Sell_Rep_FAs, Acc_Deposits, Emp_Comp_PAY, Tax_Pay, Int_Pay, Est_Liab, Bonds_PAY, Def_IT_Liab, Oth_Liab, Tot_Liab, Paid_Up_Cap, Cap_Reserves, Treas_Stock, Sur_Reserves, Gen_Risk_Res, Undist_Profits, Exch_Diff_Cash, Own_Eq_Attr_Parent, Minor_Int_Eq, Tot_Own_Eq, Tot_Liab_Own_Eq);
    # Income_Statement(Stk_Code, Oper_Rev, Net_Int_Inc, Int_Inc, Int_Exp, Fee_Com_Net_Inc, Fee_Com_Inc, Fee_Com_Exp, Inv_Inc, Inv_Inc_Assoc_JV, FV_Change_Inc, Exch_Gain_Inc, Oth_Biz_Inc, Oper_Exp, Tax_n_Surs, Gen_n_Admin_Exps, Assets_Imp_Loss, Oth_Biz_Costs, Oper_Profit, Non_Op_Rev, Non_Op_Exp, Loss_Disposal_Nonc_Assets, Tot_Profit, Income_Tax_Exp, Net_Profit, Attr_Parent_Net_Profit, Minor_Int_Inc_Loss, Basic_EPS, Diluted_EPS, Oth_Compre_Inc, Tot_Compre_Inc, Attr_Parent_Shareholders_Compre_Inc, Minor_Int_Shareholders_Compre_Inc);
    # Cash_Flow_Statement(Stk_Code, Net_Inc_Cust_Deposits_IB_Deposits, Net_Inc_Borrowings_CB, Net_Inc_IB_Borrowings, Cash_Int_Commission_Collected, Cash_Oth_Oper_Activities, Op_CF_Sub, Cust_Loans_Net_Inc, CenBank_Interbank_Net_Inc, Cash_Pay_Int_Fees_Com, Cash_Pay_Emp, Cash_Pay_Taxes, Cash_Pay_Op_Other, Op_CF_Out_Sub, Net_CF_Op, Recv_Investment, Investment_Income, Cash_Disposal_Assets, Recv_Other_Invest, Inv_CF_In_Sub, Cash_Pay_Invest, Cash_Pay_Assets, Cash_Pay_Inv_Other, Inv_CF_Out_Sub, Net_CF_Inv, Absorb_Investment, Subsidiary_Absorb_Minority, Issue_Bonds, Recv_Other_Fin, Fin_CF_In_Sub, Repay_Debt, Distribute_Dividends_Profits, Subsidiary_Pay_Minority, Cash_Pay_Fin_Other, Fin_CF_Out_Sub, Net_CF_Fin, FX_Rate_Change_Cash, Net_CF_Cash_Equiv, Initial_Cash_Equiv, Final_Cash_Equiv, CF_Stmt_Net_Income, Asset_Impairment_Dec, Fixed_Asset_Dep_Amort_Dec, Intangible_Asset_Amortization, Longterm_Amortization, Loss_Disposal_Fixed_Assets_Dec, Fixed_Asset_Scrap_Loss, Fair_Value_Change_Loss, CF_Stmt_Fin_Expenses, Investment_Loss, DIT_Asset_Reduction, DIT_Liability_Increase, Inventory_Decrease, Oper_Receivables_Decrease, Oper_Payables_Increase, Other, IM_NCF_Oper_Activities, Debt_Converted_Capital, Conv_Bonds_Maturing_Within_1Y, Fin_Lease_Additions_Fixed_Assets, Cash_End_Period, Cash_Begin_Period, Cash_Eq_End_Period, Cash_Eq_Begin_Period, IM_NCF_Cash_Eq)
    #
    ### Here are some data information about database references.
    #
    # Basic_Info(Stk_Code[600000.SH,600015.SH,600016.SH], Stk_Name[Shanghai Pudong Development Bank,Huaxia Bank,China Mingsheng Bank]);
    # Balance_Sheet(Stk_Code[600000.SH,600015.SH,600016.SH], Cash_CB[411019000000.0,176103000000.0,354899000000.0], IB_Deposits[147145000000.0,16293000000.0,114630000000.0], Prec_Metals[834000000.0,None,27993000000.0], Lending_Funds[393759000000.0,49776000000.0,188526000000.0], Trad_FAs[740222000000.0,425245000000.0,386582000000.0], Deriv_Assets[70837000000.0,9492000000.0,40635000000.0], Buyback_FAs[75358000000.0,31459000000.0,10025000000.0], Int_Receiv[None,None,None], Loans_Adv[4866904000000.0,2285717000000.0,4322267000000.0], Avail_Sale_FAs[None,None,None], Held_Mat_Invest[None,None,None], Recv_Invest[None,None,None], LT_Eq_Invest[2795000000.0,None,None], Inv_Real_Estate[None,None,None], Fix_Assets[42004000000.0,43055000000.0,50856000000.0], Intang_Assets[9958000000.0,1759000000.0,5739000000.0], Def_IT_Assets[64585000000.0,11907000000.0,56977000000.0], Oth_Assets[145910000000.0,31365000000.0,43087000000.0], Tot_Assets[8932519000000.0,4098550000000.0,7641451000000.0], Bor_CB[202042000000.0,137465000000.0,180971000000.0], IB_Dep_Oth_FIs[783188000000.0,586667000000.0,1426046000000.0], Bor_Funds_Oth_FIs[340630000000.0,183053000000.0,106646000000.0], Trad_Fin_Liab[14920000000.0,None,20506000000.0], Deriv_Liab[62341000000.0,9014000000.0,41844000000.0], Sell_Rep_FAs[373094000000.0,83045000000.0,131663000000.0], Acc_Deposits[5069529000000.0,2168881000000.0,4300243000000.0], Emp_Comp_PAY[7367000000.0,8047000000.0,11341000000.0], Tax_Pay[20503000000.0,3963000000.0,8161000000.0], Int_Pay[None,None,None], Est_Liab[6541000000.0,2035000000.0,2345000000.0], Bonds_PAY[1272371000000.0,581062000000.0,628199000000.0], Def_IT_Liab[641000000.0,None,242000000.0], Oth_Liab[50840000000.0,21950000000.0,38747000000.0], Tot_Liab[8211439000000.0,3790933000000.0,7014760000000.0], Paid_Up_Cap[29352000000.0,15915000000.0,43782000000.0], Cap_Reserves[81762000000.0,60737000000.0,58149000000.0], Treas_Stock[None,None,None], Sur_Reserves[188929000000.0,24119000000.0,55276000000.0], Gen_Risk_Res[101496000000.0,48747000000.0,90673000000.0], Undist_Profits[199479000000.0,115670000000.0,268624000000.0], Exch_Diff_Cash[None,None,None], Own_Eq_Attr_Parent[713100000000.0,304639000000.0,613419000000.0], Minor_Int_Eq[7980000000.0,2978000000.0,13272000000.0], Tot_Own_Eq[721080000000.0,307617000000.0,626691000000.0], Tot_Liab_Own_Eq[8932519000000.0,4098550000000.0,7641451000000.0]);
    # Income_Statement(Stk_Code[600000.SH,600015.SH,600016.SH], Oper_Rev[91230000000.0,47642000000.0,71539000000.0], Net_Int_Inc[60428000000.0,34151000000.0,51334000000.0], Int_Inc[150294000000.0,75794000000.0,133080000000.0], Int_Exp[89866000000.0,41643000000.0,81746000000.0], Fee_Com_Net_Inc[13962000000.0,3667000000.0,10836000000.0], Fee_Com_Inc[17520000000.0,6044000000.0,13441000000.0], Fee_Com_Exp[3558000000.0,2377000000.0,2605000000.0], Inv_Inc[13757000000.0,3656000000.0,8976000000.0], Inv_Inc_Assoc_JV[138000000.0,None,None], FV_Change_Inc[4319000000.0,4223000000.0,-2413000000.0], Exch_Gain_Inc[-3155000000.0,459000000.0,-106000000.0], Oth_Biz_Inc[1283000000.0,1376000000.0,2447000000.0], Oper_Exp[64652000000.0,31273000000.0,46748000000.0], Tax_n_Surs[1051000000.0,534000000.0,1043000000.0], Gen_n_Admin_Exps[24257000000.0,13287000000.0,21136000000.0], Assets_Imp_Loss[49000000.0,230000000.0,732000000.0], Oth_Biz_Costs[857000000.0,539000000.0,1627000000.0], Oper_Profit[26578000000.0,16369000000.0,24791000000.0], Non_Op_Rev[26000000.0,78000000.0,64000000.0], Non_Op_Exp[37000000.0,37000000.0,108000000.0], Loss_Disposal_Nonc_Assets[None,None,None], Tot_Profit[26567000000.0,16410000000.0,24747000000.0], Income_Tax_Exp[2952000000.0,4045000000.0,775000000.0], Net_Profit[23615000000.0,12365000000.0,23972000000.0], Attr_Parent_Net_Profit[23138000000.0,12114000000.0,23777000000.0], Minor_Int_Inc_Loss[477000000.0,251000000.0,195000000.0], Basic_EPS[0.76,0.58,0.46], Diluted_EPS[0.7,None,0.46], Oth_Compre_Inc[2258000000.0,1039000000.0,2721000000.0], Tot_Compre_Inc[25873000000.0,13404000000.0,26693000000.0], Attr_Parent_Shareholders_Compre_Inc[25343000000.0,13153000000.0,26302000000.0], Minor_Int_Shareholders_Compre_Inc[530000000.0,251000000.0,391000000.0]);
    # Cash_Flow_Statement(Stk_Code[600000.SH,600015.SH,600016.SH], Net_Inc_Cust_Deposits_IB_Deposits[185841000000.0,97042000000.0,289359000000.0], Net_Inc_Borrowings_CB[35502000000.0,35172000000.0,35776000000.0], Net_Inc_IB_Borrowings[None,None,None], Cash_Int_Commission_Collected[142928000000.0,66973000000.0,118670000000.0], Cash_Oth_Oper_Activities[8313000000.0,3824000000.0,28913000000.0], Op_CF_Sub[401985000000.0,246937000000.0,528276000000.0], Cust_Loans_Net_Inc[98383000000.0,82234000000.0,265774000000.0], CenBank_Interbank_Net_Inc[None,None,None], Cash_Pay_Int_Fees_Com[71825000000.0,36310000000.0,72398000000.0], Cash_Pay_Emp[19183000000.0,6951000000.0,16499000000.0], Cash_Pay_Taxes[19612000000.0,11776000000.0,10461000000.0], Cash_Pay_Op_Other[95779000000.0,9279000000.0,19680000000.0], Op_CF_Out_Sub[353499000000.0,172792000000.0,419645000000.0], Net_CF_Op[48486000000.0,74145000000.0,108631000000.0], Recv_Investment[842680000000.0,197103000000.0,797720000000.0], Investment_Income[50032000000.0,20864000000.0,35407000000.0], Cash_Disposal_Assets[None,13000000.0,920000000.0], Recv_Other_Invest[503000000.0,None,None], Inv_CF_In_Sub[893215000000.0,217980000000.0,834047000000.0], Cash_Pay_Invest[950682000000.0,316981000000.0,833348000000.0], Cash_Pay_Assets[4674000000.0,18750000000.0,3392000000.0], Cash_Pay_Inv_Other[None,None,None], Inv_CF_Out_Sub[955356000000.0,335731000000.0,836740000000.0], Net_CF_Inv[-62141000000.0,-117751000000.0,-2693000000.0], Absorb_Investment[None,None,None], Subsidiary_Absorb_Minority[None,None,None], Issue_Bonds[612774000000.0,70000000000.0,506253000000.0], Recv_Other_Fin[None,None,None], Fin_CF_In_Sub[612774000000.0,70000000000.0,506253000000.0], Repay_Debt[672761000000.0,10000000000.0,530375000000.0], Distribute_Dividends_Profits[16948000000.0,11854000000.0,15470000000.0], Subsidiary_Pay_Minority[None,None,None], Cash_Pay_Fin_Other[1646000000.0,None,1822000000.0], Fin_CF_Out_Sub[691355000000.0,42937000000.0,547670000000.0], Net_CF_Fin[-78581000000.0,27063000000.0,-41417000000.0], FX_Rate_Change_Cash[3958000000.0,610000000.0,1646000000.0], Net_CF_Cash_Equiv[-88278000000.0,-15933000000.0,66167000000.0], Initial_Cash_Equiv[372304000000.0,87707000000.0,128305000000.0], Final_Cash_Equiv[284026000000.0,71774000000.0,194472000000.0], CF_Stmt_Net_Income[23615000000.0,12365000000.0,23972000000.0], Asset_Impairment_Dec[49000000.0,230000000.0,732000000.0], Fixed_Asset_Dep_Amort_Dec[4399000000.0,1906000000.0,4137000000.0], Intangible_Asset_Amortization[None,21000000.0,None], Longterm_Amortization[None,632000000.0,None], Loss_Disposal_Fixed_Assets_Dec[-83000000.0,-6000000.0,28000000.0], Fixed_Asset_Scrap_Loss[None,None,None], Fair_Value_Change_Loss[-4319000000.0,None,2413000000.0], CF_Stmt_Fin_Expenses[None,None,None], Investment_Loss[-11281000000.0,None,-4910000000.0], DIT_Asset_Reduction[3334000000.0,None,-1957000000.0], DIT_Liability_Increase[None,None,None], Inventory_Decrease[None,None,None], Oper_Receivables_Decrease[-245794000000.0,-87024000000.0,-303177000000.0], Oper_Payables_Increase[252407000000.0,150890000000.0,386459000000.0], Other[None,None,None], IM_NCF_Oper_Activities[48486000000.0,74145000000.0,108631000000.0], Debt_Converted_Capital[None,None,None], Conv_Bonds_Maturing_Within_1Y[None,None,None], Fin_Lease_Additions_Fixed_Assets[None,None,None], Cash_End_Period[284026000000.0,71774000000.0,194472000000.0], Cash_Begin_Period[372304000000.0,87707000000.0,128305000000.0], Cash_Eq_End_Period[None,None,None], Cash_Eq_Begin_Period[None,None,None], IM_NCF_Cash_Eq[-88278000000.0,-15933000000.0,66167000000.0])
    #
    ### Foreign key information of Sqlite SQL tables, used for table joins: 
    #
    # Balance_Sheet(Stk_Code) references Basic_Info(Stk_Code);
    # Income_Statement(Stk_Code) references Basic_Info(Stk_Code);
    # Cash_Flow_Statement(Stk_Code) references Basic_Info(Stk_Code)
    #
    ### Question: 找出与运营中的其他活动有关的现金流入。
    ### SQL: """
    llm=Internlm2_Gauss_sft()
    print(llm(prompt01, max_new_tokens=512))
    print(llm('请用一句话解释万有引力', max_new_tokens=512))
    # from multiprocessing import Pool
    # import time
    #
    # stms = time.time()
    # pool = Pool(5)
    # # llm = Internlm2()
    # result = list(pool.map(llm, '请用一句话解释万有引力'))
    # print(len(result))
    # print(result)
