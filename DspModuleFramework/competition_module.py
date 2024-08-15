import json
import xml.etree.ElementTree as ET
import answer3 as ans
import alg
import lat_lon_to_meter as trans
import time
#coding=utf-8

PT_INIT_SCENE = 106;			

PT_INIT_SCENE_RESPONSE = 107;

PT_PLATFORM_STATE_INFO = 120;	

PT_COLLABORATIVE_SHARE = 130;	

PT_COLLABORATIVE_SHARE_RESULT =131;

PT_PLATFORM_CONTROL = 121;		

PT_CONSENSUS_INFO = 140;		

PT_CONSENSUS_RESULT = 141;

team_name = "九洲测试团队"   #参赛队伍名称
MAIN_PLATFORM=10021#主节点为10001

t2=0
tt2=0
#通信数据定义（查询编码）
look_up_dict={"local_target_map":0,"platform_position":1,"task_pool":2,
             "platform_lat":0,"platform_lon":1,"dynamic":2,"state_config_info_num":3}
# 定义一个函数来将XML元素转换为字典
def xml_to_dict(element):
    data = {}
    for child in element:
        data[child.tag] = child.text
    return data


#平台移动决策模块  根据平台每个时间片发来的状态及探测信息（具体信息格式参见接口说明文档） 进行行动决策以及协同共享探测信息
class motion_imp(object):
    
    def __init__(self):
        print("create motionimp")
        self.m_share_state = 0  #协同状态  0无协同 1有目标协同 
        self.m_heading = 90;    #random.random()* 360.0;
        self.m_pitch=0
        self.m_changenum = 0;
        self.m_platform_id = 0;
        self.m_task_name = "";
        self.m_speed = 30.0;



        #*************************
        #**用户编写


        self.task_id=1

        self.task_area = []#任务区域
        self.ai_modules_num=46#无人机总数量
        
        self.m_position_lat = 0#本无人机平台位置
        self.m_position_lon=0

        self.height=100#无人机高度
        self.target_height=100#无人机避障高度

        #通信

        self.local_target_map= {}#本地目标地图{id:{"state_config_info_num":,"dynamic":}}
        self.local_platform_positon_map={}#无人机位置地图{id:{"platform_lat":,"platform_lon":}}
        self.task_pool= {}#任务池{id:{"platform_lat":,"platform_lon":}}
        self.task_pool_num=46#任务池中任务数量????todo

        #**********
        #搜索
        #**********
        self.target_num=14#目标数量
        #json_str = json.dumps(json_data,indent=4);
        #***************************
        #覆盖
        #*****************************
        self.my_task_position=[] #覆盖终点位置


        self.flag_final=True
        ####!!!!!!!!有问题就改
        self.flag_communicate=True
        self.theta=0
        self.step=0
        self.flag_send=True
        super().__init__();

    def __del__(self):
        print("delete motionimp")
    #初始化任务信息及传感器搭载信息
    def init(self,json_data):
        #106号消息
        # todo somethi


        self.m_speed = 30
        self.m_platform_id = json_data["platform_num"]
        self.m_task_name = json_data["task_name"]
        self.m_changenum = 0



        #*************************
        #**用户编写
        self.target_height=self.height + (self.m_platform_id - 10000) * 6

        self.ai_modules_num=json_data["ai_modules_num"]#无人机平台数量更新
        self.target_num=json_data["target_num"]#任务目标数更新
        self.task_area=json_data["task_area"]#任务区域更新

        self.ref_lat, self.ref_lon = self.task_area[3]["task_area_point_lat"], self.task_area[3][
            "task_area_point_lon"]  # 任务区域参考点
        #通信
        #调试代码
        #测试地图区域
        for i in range(4):
            print(f"任务区域为{self.task_area[i]['index']},{self.task_area[3-i]['task_area_point_lon'],self.task_area[i]['task_area_point_lat']}")
        print("转化为坐标系")
        ref_lon, ref_lat = self.task_area[3]['task_area_point_lon'], self.task_area[3]['task_area_point_lat']  # 任务区域参考点
        for i in range(4):
            y,x=trans.GPStoXY(self.task_area[i]['task_area_point_lat'],self.task_area[i]['task_area_point_lon'],ref_lat, ref_lon)
            print(f"{i}点坐标为{x, y}")
        #测试
        #**********
        #搜索
        #**********
        #json_str = json.dumps(json_data,indent=4);
        #***************************
        #覆盖
        #*****************************
        
        
        print("场景装载情况",json_data);
        
    #平台移动决策
    def share(self,json_data):
        # todo something 分析目标位置  平台做出协同共享决策
		# 输入信息 json_data 为120号消息 平台状态信息
		# 输入信息 task_name 任务名称
		# 输入信息 module_id  平台id 
        # print("感知消息为",json.dumps(json_data).encode('utf-8').decode('unicode-escape'))
        self.m_changenum += 1;



        msg = {"protocol_type": PT_COLLABORATIVE_SHARE,"custom_content": "用户自定义字段，可以是一段xml或者一段json或者其他自定义数据","platform_num": self.m_platform_id,
               "platform_alt": 2000.0,  "platform_lat": 22.234, "platform_lon": 102.2341,"recv_platforms_num": 1,"recv_platforms": [],
               "sensing_area": {"perception_angle": 90.0, "platform_course": 110.19999694824219, "range": 5000.0 },
               "target_infos_num":2,"target_infos": [{	 "platform_alt": 2000.0,"platform_lat": 22.234,"platform_lon": 102.2341 ,	"target_id": 1	},],
               "task_name": self.m_task_name, "team_name": team_name};
        msg["target_infos_num"] = json_data["targets_num"];
        msg["target_infos"] = json_data["targets"];

        #************************
        # 用户编写
        # if self.m_platform_id>=10022:
        #     # print(f"{self.m_platform_id}不行动")
        #     return msg#原始字段

        #本平台变量更新
        self.m_position_lat=json_data["platform_control"]["platform_lat"]
        self.m_position_lon=json_data["platform_control"]["platform_lon"]
        # ******************
        # 信息发送
        # ******************
        if self.flag_send:
            alg.communication_send(json_data,self)
        # print(f"所有的AI数{self.ai_modules_num}")
        for i in range(0, self.ai_modules_num):  # 发送给(通信范围内?)所有其他无人机 询问主办方是否做处理！！！！！！！
            id = 10001 + i
            if id != self.m_platform_id:
                msg["recv_platforms"].append(10001 + i)
        # print(msg["recv_platforms"])
        #xml 示例
        root = ET.Element('root');
        root.text = f"{self.custom_content}"
        xmlstr = ET.tostring(root,encoding='utf-8').decode('utf-8');
        msg["custom_content"] =  xmlstr; #xml转为string赋值 并且在DspModuleFramework中将本字段替换掉，参考DspModuleFramework 207-210 行代码修改
        #json_str = json.dumps(msg,indent=4);
        return msg; #输出信息 json_str 为130号消息 平台协同共享信息 json.dupms之后的字符串数据流

    #平台协同共享移动决策
    def motion(self,json_data):
        
        # todo something 根据协同目标位置  平台做出移动决策 
        # 输入信息 json_data 为131号消息 平台协同共享结果信息
		# 输入信息 task_name 任务名称
		# 输入信息 module_id  平台id
        #***********用户输入代码
        #*****************************
        #通信模块
        #*****************************
        if self.flag_communicate:
            alg.communication_recive(json_data, self)#每次都通信
        if self.task_id==1:#避障阶段
            #*****************************
            #避障
            #*****************************
            flag1=alg.avoid_object(self)  #避障
            if flag1:#如果避障成功
                self.task_id=2#切换到搜索阶段
                print(f"无人机{self.m_platform_id}避障结束，开始搜索")
        elif self.task_id==2:#搜索阶段
            #*****************************
            #搜索模块
            #*****************************
            targets_num=len(self.local_target_map)#本地地图中的目标数
            if targets_num!=self.target_num:#如果未搜索完搜索目标
                # print(f"目标数{targets_num}")
                # alg.search(self)
                alg.search_imporved(self)#搜索
            else:
                self.task_id=3#搜索完目标，切换到覆盖计算阶段
                print(f"无人机{self.m_platform_id}搜索结束，开始覆盖计算")
                print(f"目标地图{self.local_target_map}")
        elif self.task_id==3:#覆盖计算阶段
            # *****************************
            # 覆盖计算,任务分配
            # *****************************
            if self.m_platform_id == MAIN_PLATFORM:#如果式主节点
                print("位置地图数量",len(self.local_platform_positon_map))
                self.m_speed = 30
                # if len(self.local_platform_positon_map) == self.ai_modules_num:  #如果位置地图完整
                if len(self.local_platform_positon_map) == self.ai_modules_num:  # 如果位置地图完整
                    flag3 = alg.coverage(self)#计算无人机覆盖位置
                    self.flag_communicate=False#关闭接收通信#！！！！！！！！！！！！！！有问题就改#todo
                    print(f"主节点计算无人机覆盖位置成功，主节点为{MAIN_PLATFORM}")
                    self.m_speed = 30
                else:#如果不完整，主节点必须移动
                    flag3=False
                    self.m_speed = 30
                    # self.m_speed=0
            else:#不是主节点直接进入任务认领阶段
                flag3=True
            if flag3:
                self.task_id=4
                self.m_speed=0#本个时间步暂时停止
                print(f"无人机{self.m_platform_id}开始任务认领")

        elif self.task_id==4:
            # ****************
            # 任务认领
            # ****************
            flag4=alg.get_task(self)
            if flag4:#任务认领成功,进入任务执行阶段
                self.task_id=5
                self.m_speed=0
                print(f"{self.m_platform_id}进入任务执行阶段")
                self.flag_communicate = False#关闭接收通信
                print("接收通信关闭")
                self.step=0
            else:#任务认领失败，停止等待
                self.m_speed=0#
            self.m_speed = 0
        elif self.task_id==5:
            # *****************************
            # 任务执行
            # *****************************
            self.step+=1
            if self.step>=5:
                self.flag_send=False
            self.m_speed = 0  #先速度清零
            if self.my_task_position :  # 如果有自己的任务
                flag = alg.task_excute(self)
                self.flag_final=False
                if flag:#如果到达目标点
                    print(f"无人机{self.m_platform_id}到达目标点{self.my_task_position}")
                    print(f"{self.m_platform_id}所有任务结束")
                    self.task_id=6
                    self.speed=0
                else:#未到目标点,继续执行任务
                    pass
            else:
                raise Exception(f"{self.m_platform_id}未领取到任务就进入到执行阶段")
        elif self.task_id==6:
            #*******
            #任务结束，停止等待
            #*******
            self.m_speed = 0  # 停止等待
        else:
            raise Exception("任务超出范围")
        msg = {"protocol_type": PT_PLATFORM_CONTROL,
               "platform_control": {"platform_course": self.m_heading, "platform_pitch": self.m_pitch,"platform_num": self.m_platform_id,  "platform_rate": self.m_speed },
               "task_name": self.m_task_name, "team_name":team_name }
        #json_str = json.dumps(msg,indent=4);
        # print(f"控制消息为{msg}")
        return msg; #输出信息 json_str  为121号消息 平台机动控制信息 json.dupms之后的字符串数据流
    
#所有平台传感器设备搭载配置模块  根据场景初始化信息平台数量目标数量（具体信息格式参见接口说明文档） 分配各个平台搭载的传感器
class equipment_schedule_imp(object):
    def __init__(self):
        print("equipment_schedule_imp create");
    def __del__(self):
        print("equipment_schedule_imp delete");
    #传感器搭载配置计算
    def eq_schedule(self,json_data,init_num,scene_name):
        print("场景初始化接受消息为",json.dumps(json_data).encode('utf-8').decode('unicode-escape'))
        
        # todo something 分析传感器装载情况 并分配传感器配置
        # 输入信息 json_data 为106号消息 场景初始化信息
		# 输入信息 init_num 平台数量
		# 输入信息 task_name  任务名称
        


        msg = { "protocol_type": PT_INIT_SCENE_RESPONSE,"platform_init_num": init_num,"competition_type": 2,"task_name": scene_name, "team_name": team_name};
        loads = []
        #爪形和调试成功搜索策略
        # for i in range(0,3):#3架无人机装载传感器3
        #     loads.append({ "carry": True,"platform_num": 10001+i,"sensor_type": 3,"sensor_str_type": "sensor_3"})
        # for i in range(0,init_num-3):#剩余无人机采用传感器1
        #     loads.append({"carry": True, "platform_num": 10004+i, "sensor_type": 1, "sensor_str_type": "sensor_1"})
        print(init_num)
        for i in range(0,init_num):#剩余无人机采用传感器1
            loads.append({"carry": True, "platform_num": 10001+i, "sensor_type": 3, "sensor_str_type": "sensor_3"})


        msg["sensors"] = loads;

        #json_str = json.dumps(msg,indent=4);
        return msg #输出信息 json_str  为107号消息 传感器配置策略信息

#所有共识算法模块  根据场景最后目标及平台的探测信息（具体信息格式参见接口说明文档） 产生目标信息共识
class consensus_imp(object):
    def __init__(self):
        print("consensus_imp create");

    def __del__(self):
        print("consensus_imp delte");

    #目标共识计算
    def consensus(self,json_data,scene_name):
        t_consense=time.time()
        print("共识接受消息",json.dumps(json_data).encode('utf-8').decode('unicode-escape'))
        msg=ans.answer3(json_data)
        print(msg)
        t_consense2=time.time()
        print(f"共识阶段处理总耗时{t_consense2-t_consense}")
        # todo something 分析协同目标位置状态类型 进行共识计算 并达成各个目标类型、威胁度等信息的共识 
		# 输入信息 json_data 为140号消息 所有平台共识信息
		# 输入信息 task_name  任务名称
        # msg =   { "protocol_type": 141,	"consensus_results_num": 2,	 "consensus_results": [	{"platform_num": 2,"platform_alt": 2000.0,  "platform_lat": 22.234,"platform_lon": 102.2341,"results_num":2,"results": [	{"platform_alt": 2000.0,"platform_lat": 22.234,"platform_lon": 102.2341,	"target_id": 1,	"target_type": 2,		"target_type_confidence": 0.8,		"threat_level": 1	},{"platform_alt": 2000.0,"platform_lat": 22.23401,"platform_lon": 102.23411,"target_id": 1,  "target_type": 2,	"target_type_confidence": 0.7,	"threat_level": 2 }	]	}	] ,"task_name": scene_name, "team_name": team_name}
        #msg = {"consensus_result": {"results": [{"pos": {"platform_alt": 2000.0,"platform_lat": 23.814597839744415, "platform_lon": 120.39015769958496 },"target_id": 20000, "target_type": 12, "target_type_confidence": 0.8,"threat_level": 1},{"pos": { "platform_alt": 2000.0,"platform_lat": 23.814597839744415, "platform_lon": 120.39015769958496 },"target_id": 20001,"target_type": 12,"threat_level": 1}]}, "protocol_type": PT_CONSENSUS_RESULT,"task_name": scene_name,"team_name": team_name}
        #json_str = json.dumps(msg,indent=4);
        return msg #输出信息 json_str  为141号消息 所有目标共识结果信息  json.dupms之后的字符串数据流

