import xml.etree.ElementTree as ET
import math
import numpy as np
import PSO_findposition_re3 as pso
import lat_lon_to_meter as trans
import getHeading
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
#通信数据定义（查询编码）
look_up_dict={"local_target_map":0,"platform_position":1,"task_pool":2,
             "platform_lat":0,"platform_lon":1,"dynamic":2,"state_config_info_num":3}

#功能：接收其他无人机传输数据修改本地内存 ①更新目标地图②更新位置地图（只在探测到所有目标时进行）③更新任务池（只在任务发布之后进行）
#输入：①131号消息 平台协同共享结果信息②无人机对象
#输出：无
def communication_recive(json_data,drone_motion):
    modules = json_data["modules"]
    for module in modules:
        # XML字符串转为xml格式
        root = ET.fromstring(module["custom_content"])
        # 将XML根元素转换为字典
        custom_content = eval(root.text)
        # 根据其他无人机信息更新共享数据
        # ******************
        ##更新目标地图
        # *******************
        local_target_map = custom_content[look_up_dict["local_target_map"]]
        if local_target_map:#如果本地目标地图中有数据
            if len(local_target_map) == 1:#如果只有一个数据
                targets_id = list(local_target_map.keys())[0]
                if targets_id in drone_motion.local_target_map.keys():# 如果本地地图有此目标
                    drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = \
                        local_target_map[targets_id][look_up_dict["platform_lat"]]  # 经纬度
                    drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = \
                        local_target_map[targets_id][look_up_dict["platform_lon"]]
                    drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = local_target_map[targets_id][
                        look_up_dict["dynamic"]]  # 静态目标
                    # dynamic=drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]]
                    # if dynamic:#如果已经标记为动态目标了
                    #     pass
                        # if  local_target_map[targets_id][look_up_dict["state_config_info_num"]]>drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]]:   #如果步长大于本地存储的步长
                        #     drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]] = local_target_map[targets_id][look_up_dict["state_config_info_num"]]
                        #     drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = local_target_map[look_up_dict["platform_lat"]]
                        #     drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = local_target_map[look_up_dict["platform_lon"]]
                        # else:#如果自己的步长更大，就忽略
                        #     pass
                    # elif local_target_map[targets_id][look_up_dict["platform_lat"]] != \
                    # drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] or \
                    # local_target_map[targets_id][look_up_dict["platform_lon"]] != \
                    # drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]]:#如果是动态目标但是未标记
                    #     pass
                    #     drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = True#标记为动态
                    #     drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]] = local_target_map[targets_id][look_up_dict["state_config_info_num"]]#标记步长
                    #     drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = local_target_map[look_up_dict["platform_lat"]]
                    #     drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = local_target_map[look_up_dict["platform_lon"]]
                    # else:#如果是静态目标,忽略
                    #     # drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = False
                    #     pass
                else:  # 共享地图中没有此目标，就直接添加
                    drone_motion.local_target_map[targets_id] = {}
                    drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = \
                        local_target_map[targets_id][look_up_dict["platform_lat"]]#经纬度
                    drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = \
                        local_target_map[targets_id][look_up_dict["platform_lon"]]
                    drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = local_target_map[targets_id][look_up_dict["dynamic"]]#静态目标
                    # if drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]]:#如果为动态
                    #     drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]] = \
                    #         local_target_map[targets_id][look_up_dict["state_config_info_num"]]#标记步长

            else:#有多个数据
                for targets_id in local_target_map:
                    if targets_id in drone_motion.local_target_map.keys():# 如果本地地图有此目标
                        drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = \
                            local_target_map[targets_id][look_up_dict["platform_lat"]]  # 经纬度
                        drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = \
                            local_target_map[targets_id][look_up_dict["platform_lon"]]
                        drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = \
                        local_target_map[targets_id][look_up_dict["dynamic"]]  # 静态目标
                        # dynamic=drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]]
                        # if dynamic:#如果已经标记为动态目标？
                        #     pass
                            # try:
                            #     if local_target_map[targets_id][look_up_dict["state_config_info_num"]] >= drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]]:  # 如果步长大于本地存储的步长
                            #         drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]] = \
                            #             local_target_map[targets_id][look_up_dict["state_config_info_num"]]
                            #         drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = \
                            #         local_target_map[look_up_dict["platform_lat"]]
                            #         drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = \
                            #         local_target_map[look_up_dict["platform_lon"]]
                            # except:
                            #     # drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]] = \
                            #     #     local_target_map[targets_id][look_up_dict["state_config_info_num"]]
                            #     # drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = \
                            #     #     local_target_map[look_up_dict["platform_lat"]]
                            #     # drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = \
                            #     #     local_target_map[look_up_dict["platform_lon"]]
                            #     pass
                            # # else:  # 如果自己的步长更大，就忽略
                            # #     pass
                        # elif local_target_map[targets_id][look_up_dict["platform_lat"]] != \
                        # drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] or \
                        # local_target_map[targets_id][look_up_dict["platform_lon"]] != \
                        # drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]]:#为动态目标但是未标记？
                        #     pass
                                # drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = True#标记
                                # drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]] = local_target_map[targets_id][look_up_dict["state_config_info_num"]]#标记步长
                                # drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = local_target_map[targets_id][look_up_dict["platform_lat"]]
                                # drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = local_target_map[targets_id][look_up_dict["platform_lon"]]
                        # else:#为静态目标
                        #     # drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = False
                        #     pass
                    else:  # 共享地图中没有此目标，就直接添加
                        drone_motion.local_target_map[targets_id] = {}
                        drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = \
                        local_target_map[targets_id][look_up_dict["platform_lat"]]
                        drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = \
                        local_target_map[targets_id][look_up_dict["platform_lon"]]
                        drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = local_target_map[targets_id][look_up_dict["dynamic"]]
                        # if drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]]:#如果为动态
                        #     drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]] = \
                        #     local_target_map[targets_id][look_up_dict["state_config_info_num"]]#标记步长
                        # else:#不是动态的，就忽略
                        #     pass
        # ******************
        ##无人机位置地图更新
        # *******************
        # print(f"位置地图为{drone_motion.local_platform_positon_map}")
        if len(drone_motion.local_target_map) == drone_motion.target_num :#如果目标地图更新完所有目标!!!!!有问题就改#todo
            local_platform_position_map=custom_content[look_up_dict["platform_position"]]
            if local_platform_position_map:#如果无人机位置地图有数据
                if len(local_platform_position_map) == 1:  # 如果只有一个数据,直接更新
                    platform_id = list(local_platform_position_map.keys())[0]
                    drone_motion.local_platform_positon_map[platform_id] = {}
                    drone_motion.local_platform_positon_map[platform_id][look_up_dict["platform_lat"]] = \
                    local_platform_position_map[platform_id][look_up_dict["platform_lat"]]
                    drone_motion.local_platform_positon_map[platform_id][look_up_dict["platform_lon"]] = \
                    local_platform_position_map[platform_id][look_up_dict["platform_lon"]]
                else:#有多个数据
                    for platform_id in local_platform_position_map:
                        if platform_id in drone_motion.local_platform_positon_map:#如果地图中有
                            pass
                        else:#地图中没有,就更新
                            drone_motion.local_platform_positon_map[platform_id] = {}
                            drone_motion.local_platform_positon_map[platform_id][look_up_dict["platform_lat"]] = \
                            local_platform_position_map[platform_id][look_up_dict["platform_lat"]]
                            drone_motion.local_platform_positon_map[platform_id][look_up_dict["platform_lon"]] = \
                            local_platform_position_map[platform_id][look_up_dict["platform_lon"]]
            else:#没有数据,忽略
                pass
        else:#没有更新完,忽略
            pass
        # print(f"更新后的位置地图为{drone_motion.local_platform_positon_map}")
        # ******************
        # 任务池更新
        # ******************
        # 将接收的任务池中最少任务量的池子作为自己的任务池

        task_pool = custom_content[look_up_dict["task_pool"]]
        task_pool_num = len(task_pool)
        # print(f"共享任务池为{task_pool}")
        if task_pool_num != 0:#任务池中有任务
            # print("任务池更新成功")
            # print(f"ID{drone_motion.m_platform_id},任务池{drone_motion.task_pool}")
            # drone_motion.task_pool_num=task_pool_num
            drone_motion.task_pool = task_pool#直接更新
        else:#否则忽略
            pass
#功能：通信发布 ①根据探测数据更新目标地图②更新己方无人机位置地图
#输入：①120号消息 平台状态信息②无人机对象
#输出：无
def communication_send(json_data,drone_motion):
    # 根据自己感知的信息更新共享数据
    # drone_motion.target_num = json_data["targets_num"]#更新所有目标数，初始化的时候已经做过了
    # 本地目标地图更新
    targets_list = json_data["targets"]
    if targets_list:#如果感知结果中有数据
        if len(targets_list)==1:#如果数据只有一个
            targets_dict=targets_list[0]
            targets_id = targets_dict["target_id"]
            if targets_id in drone_motion.local_target_map.keys():#如果本地地图中已经有此目标
                drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = targets_dict["platform_lat"]
                drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = targets_dict["platform_lon"]
                drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = False
                # dynamic=drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]]
                # if dynamic or targets_dict["platform_lat"] != drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] or targets_dict["platform_lon"] != drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]]: # 是动态目标？
                #     drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = True
                #     try:
                #         drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]] = json_data["state_config_info_num"]#记录感知步长
                #     except:
                #          raise Exception(f"加入步长信息出错，错误数据{json_data},本地数据{drone_motion.local_target_map}")
                #     drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = targets_dict[
                #         "platform_lat"]
                #     drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = targets_dict[
                #         "platform_lon"]
                # else:#静态目标，标记
                #     drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = False
            else:#新增目标?
                drone_motion.local_target_map[targets_id] = {}
                drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = targets_dict["platform_lat"]
                drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = targets_dict["platform_lon"]
                drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = False
        else:#多个数据
            for targets_dict in targets_list:
                targets_id = targets_dict["target_id"]  # 目标ID
                # 如果本地地图有此目标
                if targets_id in drone_motion.local_target_map.keys():
                    drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = targets_dict[
                        "platform_lat"]
                    drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = targets_dict[
                        "platform_lon"]
                    drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = False
                    # 检查是否为动态目标
                    # if targets_dict["platform_lat"] != drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] or \
                    #         targets_dict["platform_lon"] != drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]]:
                    #     drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = True
                    #     try:
                    #         drone_motion.local_target_map[targets_id][look_up_dict["state_config_info_num"]] = json_data[
                    #             "state_config_info_num"]
                    #     except:
                    #         raise Exception(f"加入步长信息出错，错误数据{json_data},本地数据{drone_motion.local_target_map}")
                    #     drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = targets_dict["platform_lat"]
                    #     drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = targets_dict["platform_lon"]
                    # else:
                    #     drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = False
                else:  # 新增目标
                    drone_motion.local_target_map[targets_id] = {}
                    drone_motion.local_target_map[targets_id][look_up_dict["platform_lat"]] = targets_dict["platform_lat"]
                    drone_motion.local_target_map[targets_id][look_up_dict["platform_lon"]] = targets_dict["platform_lon"]
                    drone_motion.local_target_map[targets_id][look_up_dict["dynamic"]] = False
    else:#感知结果没有目标，跳过
        pass
    # 无人机位置地图更新
    if not drone_motion.m_platform_id in drone_motion.local_platform_positon_map:#如果自己的位置没有加入本地位置地图
        drone_motion.local_platform_positon_map[drone_motion.m_platform_id] = {}
    drone_motion.local_platform_positon_map[drone_motion.m_platform_id][look_up_dict["platform_lat"]] = drone_motion.m_position_lat
    drone_motion.local_platform_positon_map[drone_motion.m_platform_id][look_up_dict["platform_lon"]] = drone_motion.m_position_lon
    # 任务池任务在接收时认领和更新!!!!

    # 用户信息合并
    drone_motion.custom_content = {look_up_dict["local_target_map"]: drone_motion.local_target_map,
                           look_up_dict["platform_position"]: drone_motion.local_platform_positon_map,
                           look_up_dict["task_pool"]: drone_motion.task_pool}
#功能：避障（飞成一个竖条）  根据本无人机编号，计算本平台速度和俯仰角
#输入：无人机对象
#输出：无
def avoid_object(drone_motion):
    height_delta=drone_motion.target_height-drone_motion.height#计算高度差
    if drone_motion.height==drone_motion.target_height:#如果达到目标高度，任务结束
        return True
    if height_delta>30:#如果高度差大于30m，则直着飞
        drone_motion.m_speed=30
        drone_motion.m_pitch=90
        drone_motion.height+=30
    else:#如果小于30m，则直接飞到期望高度
        drone_motion.m_speed=30
        drone_motion.m_pitch=math.asin(height_delta / 30.0)
        drone_motion.height=drone_motion.target_height
    return False# 避障未结束
# 功能：搜索（按照规则指定无人机飞行） ！！！！！未完成  todo
# 输入：无人机对象
# 输出：无
def search(drone_motion):
    add = 0
    drone_motion.m_speed = 30  # 先假设所有无人机都在运动
    if drone_motion.m_platform_id == 10001:
        drone_motion.m_heading = 135 + add
    elif drone_motion.m_platform_id == 10002:
        drone_motion.m_heading = 110 + add
    elif drone_motion.m_platform_id == 10003:
        drone_motion.m_heading = 160 + add
    elif drone_motion.m_platform_id == 10015:
        drone_motion.m_heading = 90
    elif drone_motion.m_platform_id == 10016:
        drone_motion.m_heading = 80
    elif drone_motion.m_platform_id == 10017:
        drone_motion.m_heading = 70
    elif drone_motion.m_platform_id == 10018:
        drone_motion.m_heading = 100
    elif drone_motion.m_platform_id == 10019:
        drone_motion.m_heading = 120
    elif drone_motion.m_platform_id == 10020:
        drone_motion.m_heading = 130
    elif drone_motion.m_platform_id == 10021:
        drone_motion.m_heading = 135
    elif drone_motion.m_platform_id == 10022:
        drone_motion.m_heading = 140
    elif drone_motion.m_platform_id == 10023:
        drone_motion.m_heading = 145
    elif drone_motion.m_platform_id == 10024:
        drone_motion.m_heading = 137
    else:
        drone_motion.m_speed = 30
        drone_motion.m_heading = 90

    if drone_motion.m_changenum % 4 != 0:  # 走三步停一步
        if drone_motion.m_platform_id == 10004:
            drone_motion.m_speed = 30
            drone_motion.m_heading = 122 + add
        if drone_motion.m_platform_id == 10005:
            drone_motion.m_heading = 147 + add
    if drone_motion.m_changenum % 2 != 0:  # 走一步停一步
        if drone_motion.m_platform_id == 10006:
            drone_motion.m_speed = 30
            drone_motion.m_heading = 122 + add
        if drone_motion.m_platform_id == 10007:
            drone_motion.m_speed = 30
            drone_motion.m_heading = 147 + add
    if drone_motion.m_changenum % 4 == 0:  # 走一步停三步
        if drone_motion.m_platform_id == 10008:
            drone_motion.m_speed = 30
            drone_motion.m_heading = 122 + add
        if drone_motion.m_platform_id == 10009:
            drone_motion.m_speed = 30
            drone_motion.m_heading = 147 + add
# 功能：覆盖  搜索到所有目标后，采用粒子群算法(调用pso)计算所有目标位置，采用KM算法(调用position_allocate()函数)进行任务分配
# 输入：无人机对象
# 输出：bool（是否覆盖和目标分配成功）
def coverage(drone_motion):

    print("覆盖模块开始")
    # 覆盖无人机位置点计算
    sensor_num = len(drone_motion.local_platform_positon_map)
    print(f"传感器数量{sensor_num}")
    target_num = len(drone_motion.local_target_map)
    print(f"目标数量{target_num}")
    target_matrix = np.zeros((target_num, 3), dtype=int)
    # 参考点
    ref_lat, ref_lon = drone_motion.task_area[3]["task_area_point_lat"], drone_motion.task_area[3]["task_area_point_lon"]
    for i in range(target_num):  # 目标矩阵数据输入
        target_matrix[i][0] = i + 1
        # 经纬度转化
        y, x = trans.GPStoXY(drone_motion.local_target_map[i + 1][look_up_dict["platform_lat"]],
                             drone_motion.local_target_map[i + 1][look_up_dict["platform_lon"]], ref_lat, ref_lon)
        target_matrix[i][1] = x
        target_matrix[i][2] = y
    print(f"目标矩阵{target_matrix}")
    sensor_matrix = np.zeros((sensor_num, 5), dtype=int)
    for i in range(sensor_num):  # 无人机矩阵输入
        sensor_matrix[i][0] = 1 + i
        if i < 3:
            sensor_matrix[i][1] = 3
            sensor_matrix[i][2] = 8000
            sensor_matrix[i][3] = 8000 ** 2
        else:
            sensor_matrix[i][1] = 1
            sensor_matrix[i][2] = 5000
            sensor_matrix[i][3] = 5000 ** 2
    print(f"传感器矩阵{target_matrix}")
    print("target_matrix矩阵",target_matrix)
    print("sensor_matrix矩阵",sensor_matrix)
    best_position_x, best_position_y = pso.pso_findposition(target_matrix, sensor_matrix)  # sensor_num向量
    print(f"最优位置{best_position_x, best_position_y}")
    # 无人机位置分配(基于KM算法目标分配)

    ref_lat, ref_lon = drone_motion.task_area[3]["task_area_point_lat"], drone_motion.task_area[3]["task_area_point_lon"]
    target_position=np.stack([best_position_x,best_position_y],1).tolist()#目标位置的列表[[x1,y1],[x2,y2]]
    drone_position,drone_id=drone_trans(drone_motion.local_platform_positon_map,ref_lat, ref_lon)#无人机位置列表，ID列表
    print(drone_id)
    match_list=position_allocate(drone_position,target_position)#返回匹配表[无人机索引，目标索引]
    # 任务池任务发布
    for i in range(sensor_num):
        drone_motion.task_pool[drone_id[i]] = {}
        drone_motion.task_pool[drone_id[i]][look_up_dict["platform_lat"]] = best_position_x[match_list[i][1]]#无人机索引第i个匹配match_list中第i个索引中的值代表的索引
        drone_motion.task_pool[drone_id[i]][look_up_dict["platform_lon"]] = best_position_y[match_list[i][1]]#注意！！！任务池中的坐标为x,y不是经纬度！！！！！需要检查
    # for i in range(sensor_num):
    #     drone_motion.task_pool[10001 + i] = {}
    #     drone_motion.task_pool[10001 + i][look_up_dict["platform_lat"]] = best_position_x[i]
    #     drone_motion.task_pool[10001 + i][look_up_dict["platform_lon"]] = best_position_y[i]
    print(f"任务池为{drone_motion.task_pool}")
    return True
# 功能：任务认领  任务分配后，通信模块共享任务池，当本地任务池中有本无人机平台时，获取目标位置
# 输入：无人机对象
# 输出：无
def get_task(drone_motion):
    # ****************
    # 任务认领
    # ****************
    if drone_motion.task_pool:#如果任务池中有任务
        print("任务认领")
        if len(drone_motion.task_pool) == 1:#任务池中任务只有一个
            platform_id = list(drone_motion.task_pool.keys())
            if platform_id[0] == drone_motion.m_platform_id:#如果任务池中唯一的ID是自己的ID
                # drone_motion.my_task_position=drone_motion.task_pool.pop(drone_motion.m_platform_id)
                drone_motion.my_task_position = drone_motion.task_pool[drone_motion.m_platform_id]
                return True
        else:
            for platform_id in drone_motion.task_pool:
                # 本平台任务池更新
                # 任务池任务认领
                # 如果任务池中有自己的任务，则认领任务并删除
                if platform_id == drone_motion.m_platform_id:#如果ID是自己的ID
                    drone_motion.my_task_position = drone_motion.task_pool[drone_motion.m_platform_id]
                    # drone_motion.my_task_position = drone_motion.task_pool.pop(drone_motion.m_platform_id)# 将认领的任务在任务池中删除
                    # print(f"任务认领成功,任务为{drone_motion.my_task_position}")
                    print(f"{drone_motion.m_platform_id}领取任务为{drone_motion.my_task_position}")
                    return True
    else:#任务池中没有任务，认领失败
        return False

# 功能：任务执行  获得任务目标点后，计算本无人机平台的速度和航向角 (未完成 ！！！！！)  todo
# 输入：无人机对象
# 输出：无
def task_excute(drone_motion):
    my_task_position_lat = drone_motion.my_task_position[1]
    my_task_position_lon = drone_motion.my_task_position[0]
    task_position_y, task_position_x = my_task_position_lat, my_task_position_lon#任务领取的就是直角坐标，只是变量名字有问题
    y, x = trans.GPStoXY(drone_motion.m_position_lat, drone_motion.m_position_lon,drone_motion.ref_lat,drone_motion.ref_lon)
    distance_2=abs(task_position_y-y)+abs(task_position_x-x)#曼哈顿距离
    if distance_2<30:#如果距离小于30米，任务结束
        print(f"任务结束,{drone_motion.m_platform_id}为{x,y}")
        return True#任务成功完成
    if drone_motion.flag_final:
        print("计算角度")
        drone_motion.theta = getHeading.GetClockAngle([0, 1], [task_position_x - x, task_position_y - y])  # 获得航向角
    drone_motion.m_heading = drone_motion.theta
    drone_motion.m_speed = 30
    return False#任务未完成
# 功能：任务分配  获得任务目标点后，计算本无人机平台的速度和航向角
# 输入：无人机位置和目标位置列表[[x1,y1],[x2,y2]]
# 输出：匹配列表[drone_index,target_index]无人机和目标的索引
def position_allocate(drone_position,target_position):
    match_list=[]
    try:
        distance_matrix = cdist(drone_position, target_position, 'euclidean')#计算欧几里得距离
    except:
        raise Exception(f"计算距离矩阵出错，输入数据为:无人机位置向量{drone_position},目标位置向量{target_position}，期望输入格式np.array")
    try:
        drone_index, target_index = linear_sum_assignment(distance_matrix)#计算最小权值匹配
    except:
        raise Exception(f"计算最小权值匹配时出错误，输入的距离矩阵为{distance_matrix}")
    for i, j in zip(drone_index, target_index):
        print(f"无人机 {i+10001} 匹配到目标 {j+1}，距离为 {distance_matrix[i][j]}")
        match_list.append([i,j])
    return match_list
# 功能：无人机位置经纬度转化
# 输入：无人机位置地图，参考点
# 输出：无人机位置列表[[x1,y1],[x2,y2]],无人机ID列表(与位置列表一一对应)
def drone_trans(local_platform_positon_map,ref_lat, ref_lon):#输入无人机本地位置地图，输出无人机位置列表[[x1,y1],[x2,y2]
    drones_position=[]
    drones_id=[]
    for ID in local_platform_positon_map:#从本地无人机位置地图中获取所有无人机位置
        lat=local_platform_positon_map[ID][look_up_dict["platform_lat"]]
        lon=local_platform_positon_map[ID][look_up_dict["platform_lon"]]
        y,x=trans.GPStoXY(lat,lon,ref_lat, ref_lon)
        drones_position.append([x,y])
        drones_id.append(ID)
    return drones_position,drones_id

###############################################
#功能：转圈搜索
#输入：无人机对象
#输出：无
def search_imporved(drone_motion):
    if 10001<=drone_motion.m_platform_id<=10016:
        return_data=search_circle(drone_motion)
        if return_data:#未到达目标点
            theta,task_positon_x,task_positon_y=return_data
            speed=30
        else:#到达目标点
        #转圈???暂时不动  todo
            theta = 0
            speed = 0
    elif 10017<=drone_motion.m_platform_id<=10021:
        return_data=search_communication(drone_motion)
        if return_data:
            theta,task_positon_x,task_positon_y=return_data
            speed = 30
        else:
            #不动
            theta=0
            speed = 0
    elif drone_motion.m_platform_id>=10022:
        return_data=run_others(drone_motion)
        if return_data:
            theta,task_positon_x,task_positon_y=return_data
            speed = 30
        else:
            #不动
            theta=0
            speed = 0
    else:
        theta=0
        speed=0
    drone_motion.m_heading=theta
    drone_motion.m_speed=speed
    # return True#表示任务未结束
#功能：通过无人机转圈的方式实现圆形搜索，从而将问题转化为无人机布置
#输入：无人机对象
#输出:无人机运动角度 目标位置
def search_circle(drone_motion):
    drone_x,drone_y=localization(drone_motion)#定位无人机位置
    target_coord=[]#目标位置
    for coord_x in [2500,7500,12500,17500]:
        for coord_y in [2500,7500,12500,17500]:
            target_coord.append((coord_x,coord_y))
    drone_index=drone_motion.m_platform_id-10000#无人机序号
    if drone_index<=16:
        task_positon_x,task_positon_y=target_coord[drone_index-1]#任务分配
    else:
        pass
    if drone_index<=16:
        if ((task_positon_x-drone_x)**2+(task_positon_y-drone_y)**2)<900:#如果距离目标点小于30m
            return False#任务结束
        else:
            theta = getHeading.GetClockAngle([0, 1], [task_positon_x - drone_x, task_positon_y - drone_y])#计算航向角
            return (theta,task_positon_x,task_positon_y)
# 功能：维持无人机通信
# 输入：无人机对象
# 输出:无人机运动角度 目标位置
def search_communication(drone_motion):
    drone_x,drone_y=localization(drone_motion)#定位无人机位置
    target_coord=[(5000,5000),(5000,15000),(15000,5000),(15000,15000),(10000,10000)]#目标位置
    drone_index=drone_motion.m_platform_id-10016#无人机序号
    if 1<=drone_index<=5:
        task_positon_x,task_positon_y=target_coord[drone_index-1]#任务分配
    else:
        pass
    if 1<=drone_index<=5:
        if ((task_positon_x - drone_x) ** 2 + (task_positon_y - drone_y) ** 2) < 900:  # 如果距离目标点小于30m
            return False
        else:
            theta = getHeading.GetClockAngle([0, 1], [task_positon_x - drone_x, task_positon_y - drone_y])#计算航向角
            return (theta,task_positon_x,task_positon_y)
def run_others(drone_motion):
    # target_coord = (10000,10000)  # 目标位置
    drone_x, drone_y = localization(drone_motion)#本平台位置
    if drone_x<=100:#左边
        if drone_y<=100: #左下角
            target_coord=(0,0)
        elif 100<drone_y<=19900:#左边
            target_coord=(0,drone_y)
        elif drone_y>19900:#左上角
            target_coord=(0,20000)
    elif 100<drone_x<=19900:#x轴中间
        if drone_y<=100:#下边
            target_coord=(drone_x,0)
        elif drone_y>19900:#上边
            target_coord=(drone_x,20000)
        else:
            target_coord=(15000,15000)
            print("初始点在中间去了")
    elif drone_x>19900:#右边
        if drone_y<=100:#右下角
            target_coord=(20000,0)
        elif 100<drone_y<=19900:#右边
            target_coord=(20000,drone_y)
        elif drone_y>19900:#右上角
            target_coord=(20000,20000)
    else:
        raise Exception("初始点超出范围")


    if drone_motion.m_platform_id>=10022:
        task_positon_x, task_positon_y = target_coord  # 任务分配
    else:
        pass
    if drone_motion.m_platform_id>=10022:
        if ((task_positon_x - drone_x) ** 2 + (task_positon_y - drone_y) ** 2) < 900:  # 如果距离目标点小于30m
            return False
        else:
            theta = getHeading.GetClockAngle([0, 1], [task_positon_x - drone_x, task_positon_y - drone_y])#计算航向角
            return (theta,task_positon_x,task_positon_y)


#功能：建立地图坐标，定位无人机位置
#输入：无人机对象
#输出：本平台无人机直角坐标系坐标
def localization(drone_motion):
    m_lat = drone_motion.m_position_lat
    m_lon = drone_motion.m_position_lon#无人机经纬度
    y, x = trans.GPStoXY(m_lat, m_lon, drone_motion.ref_lat, drone_motion.ref_lon)#直角坐标系位置
    return x,y



