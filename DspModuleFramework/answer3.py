import json
import jsonpath

import numpy as np
from itertools import combinations


def answer3(obj):
    # # 提取140 json文件中的数据（给的）
    # # 输出141 json文件（创建）

    results = jsonpath.jsonpath(obj, '$..results')
    # print(results)

    # 平台总数量，消息数 现在为3
    Platform_Num = obj["consensus_infos_num"]
    # print(Platform_Num)
    # 每个平台的result数量 [3,3,4] ==> 0 1 2 
    Results_num = jsonpath.jsonpath(obj, '$..results_num')

    # print(Platform_num)
    # print(Results_num)
    # print(Target_id)

    ##############置信度融合的两个函数##################
    def fusion(a, b):
        m1 = np.array(a)
        m2 = np.array(b)
        k = 0
        for i in range(len(a)):
            for j in range(len(a)):
                k = k + m1[i] * m2[j]  # 计算冲突因子k

        res = 0
        for q in range(len(a)):
            res = res + m1[q] * m2[q]

        k = k - res

        list = []
        for s in range(len(a)):
            A = m1[s] * m2[s] / (1 - k)
            list.append(A)

        list2 = []
        for t in range(len(a)):
            P = list[t] / np.sum(list)
            list2.append(P)

        result = np.array(list2)

        return result

    def fusion2(element1, element2):
        # 要查找的两个元素
        # 用嵌套循环遍历每个数组，查找包含这两个元素的数组
        result_arrays = []
        P = []
        M = []
        O = [0.5, 0.5]
        for idex, arr in enumerate(arrays):
            if element1 in arr and element2 in arr:
                result_arrays.append(arr)
                P.append(idex)
        for idex, arr in enumerate(result_arrays):
            index1 = arr.index(element1)
            index2 = arr.index(element2)
            if index1 < index2:
                m = [array[P[idex]], 1 - array[P[idex]]]
            elif index1 > index2:
                m = [1 - array[P[idex]], array[P[idex]]]
            M.append(m)
        # print(M)
        # 使用len()函数获取数组中元素的数量
        element_count = len(M)

        for i in range(len(M)):
            O = fusion(O, M[i])
        if O[0] > O[1]:
            return [element1, element2]
        else:
            return [element2, element1]

    #########--------处理威胁度--------########################
    target_id = []
    threat_level = []
    threat_level_confidence = []
    # ###获取威胁度
    # Threat_level_confidence = jsonpath.jsonpath(obj, '$..threat_level_confidence')
    # Threat_Level_Confidence = list(set(Threat_level_confidence))

    ######1.获取target_id和threat_level#########
    ###输出：按文件顺序的id 和 威胁等级
    ###target_id[[1, 2, 3], [4, 2, 5], [1, 3, 4, 5]]
    ###threat_level:[[1, 2, 3], [1, 2, 3], [1, 2, 3, 4]]
    for i in range(0, Platform_Num):
        target_id.append([])
        threat_level.append([])
        threat_level_confidence.append([])
        for j in range(0, Results_num[i]):
            # print(output_msg["consensus_infos"][i]["results"][j]["target_id"])
            target_id[i].append(obj["consensus_infos"][i]["results"][j]["target_id"])
            threat_level[i].append(obj["consensus_infos"][i]["results"][j]["threat_level"])
            threat_level_confidence[i].append(obj["consensus_infos"][i]["results"][j]["threat_level_confidence"])

    first_threat_level_confidence = [lst[0] for lst in threat_level_confidence]
    # print(target_id)
    # print(threat_level)

    #########2.转换threat_level################################
    ##观测到的id arrays = [[1,2,3],[5,4,2],[5,1,4,3]]
    ##观测到的level = [[1,2,3],[3,1,2],[4,1,3,2]]
    ##转换为id new_arrays = [[1,2,3],[4,2,5],[1,3,4,5]]
    ##结果 1 3 4 2 3 5
    ###输出：按照威胁等级排序的id顺序
    def reorder_ids(arrays, levels):
        new_arrays = []
        for i in range(len(arrays)):
            new_array = [x for _, x in sorted(zip(levels[i], arrays[i]))]
            new_arrays.append(new_array)
        return new_arrays

    new_arrays = reorder_ids(target_id, threat_level)
    # print(new_arrays)

    ################3.计算威胁度排序###########################
    ###输出：new_threat_level_confidence：按照威胁等级排序的id排序
    # arrays = [[1, 2, 3], [4, 2, 5], [6, 7, 2], [5, 2, 3, 4],[3, 5, 2]]
    # array=[0.5,0.6,0.7,0.8,0.9]
    arrays = new_arrays
    array = first_threat_level_confidence
    new_threat_level_confidence = []

    for i in range(0, Platform_Num):
        ## 输出本平台的排序
        wx1 = arrays[i]
        # print(wx1)
        R = []
        p = []
        r = []
        element_count = {}
        # 生成数组的所有两两组合
        combinations_list = list(combinations(wx1, 2))

        for i in range(1):
            for ii in range(len(combinations_list)):
                R.append(fusion2(combinations_list[ii][0], combinations_list[ii][1]))

        for i in range(len(R)):
            p.append(R[i][0])
        for element in p:
            if element in element_count:
                element_count[element] += 1
            else:
                element_count[element] = 1

        new_sys1 = sorted(element_count.items(), key=lambda d: d[1], reverse=True)

        for key in new_sys1:
            r.append(key[0])
        set1 = set(wx1)
        set2 = set(r)

        # 使用集合的差集操作获取不包含在array2中的元素
        result = set1 - set2
        result_list = list(result)
        for i in range(0, len(result_list)):
            r.append(result_list[i])
        ##新的按顺序排序的id结果
        new_threat_level_confidence.append(r)

    ###############4.转换威胁度排序#################################
    ### [[2, 1, 3], [4, 2, 5], [1, 3, 4, 5]] 原始id顺序
    ### [[1, 2, 3], [4, 2, 5], [1, 3, 4, 5]] 排序后的id顺序
    #####应该输出对应的排序[[2,1,3],[1,2,3],[1,2,3,4]]
    ###输出：corresponding_order:按id顺序的level
    def get_corresponding_order(original_ids, sorted_ids):
        corresponding_order = []
        for i in range(len(sorted_ids)):
            order = []
            for j in range(len(sorted_ids[i])):
                index = original_ids[i].index(sorted_ids[i][j])
                order.append(index + 1)
            corresponding_order.append(order)
        return corresponding_order

    corresponding_order = get_corresponding_order(target_id, new_threat_level_confidence)
    ###level
    # print(corresponding_order)

    # ########反转######
    # for i in range(Platform_Num):
    #     max_th = max(corresponding_order[i])
    #     for j in range(len(corresponding_order[i])):
    #         corresponding_order[i][j] = max_th - corresponding_order[i][j] + 1


    ############--------处理类型和置信度--------#################

    Target_type_confidence = []
    Target_type = []

    ### 获取总的目标个数(一共有5-20个)
    Target_id = jsonpath.jsonpath(obj, '$..target_id')
    number_types = set(Target_id)
    total_id = list(number_types)
    Target_num = len(number_types)
    # print(Target_id)
    # print(total_id)
    # print(Target_num)
    # print(number_types)

    ###############1.处理类型和置信度#########################
    ###输入：result：结果字典，从中提取类型和置信度
    ###输出：Target_type：类型，Target_type_confidence：类型置信度 （按照id为顺序排列的[1,2,3,4,5.....]）
    ####输出样例
    ### 类型和置信度 [2,5,6,8,10],[0.9,0.7,0.7,0.7,0.7]

    for i1 in range(1, Target_num + 1):
        # print(i)
        extracted_data = []
        i2 = 0
        for item in results:

            for i3 in range(0, Results_num[i2]):
                if item[i3]['target_id'] == total_id[i1 - 1]:
                    target_types = item[i3]['target_types']
                    # print(target_types)

                    for target_type in target_types:
                        extracted_data.append([
                            target_type['target_type'],
                            target_type['target_type_confidence']
                        ])
            i2 = i2 + 1
        res = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
        k = []
        m = []
        for i4 in range(0, int(len(extracted_data) / 4)):
            k.append(extracted_data[(4 * i4):(4 + 4 * i4)])
            m.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            # print(k2)
        for i5 in range(0, int(len(extracted_data) / 4)):
            for i in range(4):
                for ii in range(10):
                    if ii == k[i5][i][0]:
                        m[i5][ii] = float(k[i5][i][1])
        for i in range(len(m)):
            res = fusion(res, m[i])
        # res = res.tolist()
        # print(res)

        if type(res) is np.ndarray:
            res = res.tolist()
        # print(type(res))
        # 类型和类型置信度 id从1开始
        Target_type_confidence.append(max(res))
        Target_type.append(res.index(max(res)))

    # print(Target_type_confidence)
    # print(Target_type)
    # print(target_id)

    ###############2.转换类型和置信度###########
    ###输入：target_id：原始id ，Target_type：类型， Target_type_confidence：类型置信度
    ###输出：type_sort：类型 ， confidence_sort：置信度 （按照按原始id顺序排列）

    ### [[2, 1, 3], [4, 2, 5], [1, 3, 4, 5]] 原始id顺序
    ####输出样例
    ### [[5,2,6],[8,5,10],[2,6,8,10]]  类型
    ### [[0.7, 0.9, 0.7], [0.7, 0.7, 0.9], [0.9, 0.7, 0.7, 0.7]]  置信度

    # def get_type_order(original_ids, type_order):
    #     type_sort = []
    #     for i in range(len(original_ids)):
    #         order = []
    #         for j in range(len(original_ids[i])):
    #             index = original_ids[i][j] - 1
    #             type_value = type_order[index]
    #             order.append(type_value)
    #         type_sort.append(order)
    #     return type_sort

    type_sort = []
    confidence_sort = []
    for ids in target_id:
        type_sort.append([Target_type[total_id.index(id)] for id in ids])
        confidence_sort.append([Target_type_confidence[total_id.index(id)] for id in ids])

    # original_ids = [[2, 1, 3], [4, 2, 1], [1, 3, 4, 5]]
    # type_order = [21, 5, 6, 8, 12]
    # confidence_oder = [0.9,0.7,0.7,0.7,0.7]

    # type_sort = get_type_order(target_id, Target_type)
    # confidence_sort = get_type_order(target_id, Target_type_confidence)

    # print(type_sort)
    # print(confidence_sort)

    ########------往result里写按顺序来的level、type、confidence--------##########

    ###修改输入数据键的名称

    obj["protocol_type"] = 141
    obj["consensus_results_num"] = obj.pop("consensus_infos_num")
    obj["consensus_results"] = obj.pop("consensus_infos")

    for i in range(0, Platform_Num):
        for j in range(Results_num[i]):
            obj["consensus_results"][i]["results"][j].pop("target_types")
            obj["consensus_results"][i]["results"][j].pop("target_types_num")
            obj["consensus_results"][i]["results"][j].pop("threat_level_confidence")
            obj["consensus_results"][i]["results"][j]["target_type"] = type_sort[i][j]
            obj["consensus_results"][i]["results"][j]["target_type_confidence"] = confidence_sort[i][j]
            obj["consensus_results"][i]["results"][j]["threat_level"] = corresponding_order[i][j]
    return obj

# obj = json.load(open('fff.json','r',encoding='utf-8'))

# print(answer3(obj))
