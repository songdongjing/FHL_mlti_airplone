import random
import json
import numpy as np


# from data_generate import sensor_num, target_num

def read_data_sensor(file_path, sensor_num):
    # 从 JSON 文件中读取数据
    with open(file_path, 'r') as file:
        data = json.load(file)

    # 将数据存储到矩阵中
    matrix = np.zeros((sensor_num, 5), dtype=int)
    for i, item in enumerate(data):
        matrix[i] = [
            item['sensor_id'],
            item['sensor_type'],
            item['sensor_radius'],
            int(item['sensor_radius']) ** 2,
            item['sensor_angle']
        ]
    # print(matrix)
    return matrix


def read_data_target(file_path, target_num):
    # 在程序重新启动时读取JSON文件
    # with open('data.json', 'r') as f:
    with open(file_path, 'r') as f:
        loaded_data = json.load(f)

    # 将数据加载到一个矩阵中
    matrix = np.zeros((target_num, 3), dtype=int)
    for i, item in enumerate(loaded_data):
        matrix[i, 0] = item['id']
        matrix[i, 1] = item['x']
        matrix[i, 2] = item['y']

    # 打印矩阵
    # print("----read_data_target---------")
    # print(matrix)
    # print("matrix[1,1] = ", matrix[0, 0])

    return matrix
