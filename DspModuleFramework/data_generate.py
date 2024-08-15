import json
import random
import numpy as np


def data_generate(sensor_num, target_num):
    # 生成20个随机目标数据
    data = []
    for _ in range(target_num):
        x = random.randint(0, 20000)
        y = random.randint(0, 20000)
        data.append({"id": len(data) + 1, "x": x, "y": y})

    # 打印数据
    for item in data:
        print(item)

    # 将数据保存到JSON文件中
    with open('target_data.json', 'w') as f:
        json.dump(data, f, indent=3)

    # 生成传感器的随机数据
    data = []
    for i in range(1, sensor_num + 1):
        sensor_id = i
        sensor_type = random.randint(1, 4)
        sensor_type = 2
        sensor_radius = [5000, 4000, 8000, 6000][sensor_type - 1]
        sensor_angle = [180, 180, 120, 360][sensor_type - 1]
        sensor_data = {
            'sensor_id': sensor_id,
            'sensor_type': sensor_type,
            'sensor_radius': sensor_radius,
            'sensor_angle': sensor_angle
        }
        data.append(sensor_data)

    # 将数据保存为 JSON 文件
    with open('sensor_data.json', 'w') as file:
        json.dump(data, file, indent=4)

    print("数据已保存为 sensor_data.json 文件")
