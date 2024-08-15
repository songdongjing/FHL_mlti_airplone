import yaml
import json
import math
import time

# 读取YAML文件
with open('output.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
    
       
# 初始化结果字典
result = {}
data_list = {}
database = {}

# 修改数据
for i in range(0, len(data)):
    name = "agent" + str(i)
    data_list[name] = []
    for var in data[name]:
        data_list[name].append(var)


# data_list['agent0'][0]['x']
swap = {}
shuChu = {}

shuChu["protocol_type:"] = 121
shuChu["platform_control:"] = []
cout = 10000
count = 0
for i_1 in data_list:
    swap[i_1] = []
    cout += 1
    # name = i
    for j in data_list[i_1]:
        swap[i_1].append([j['x']]+[j['y']])
    # 提取坐标数据
    coordinates = swap[i_1]

    # 计算每两个点之间的距离并存储在一个列表中
    thetas = []
    for i in range(1, len(coordinates)):
        x1, y1 = coordinates[i - 1]
        x2, y2 = coordinates[i]
        theta = math.degrees(math.atan2(y2 - y1, x2 - x1))
        thetas.append(theta)

    # 打印每两个点之间的方向
    for i, theta in enumerate(thetas):
        print(f"platform_rate: {theta}")
        count += 1

        database[count] = {
        "protocol_type": 121,
            "platform_control": {
                "platform_course": theta,
                "platform_pitch": 0.0,
                "platform_num": cout,
                "platform_rate": 30,
            },
            "task_name": "task_name_demo",
            "team_name": "team_name"
        }

        # 将结果写入JSON文件
        with open('output.json', 'w') as json_file:
            json.dump(database, json_file, indent=4)
        
