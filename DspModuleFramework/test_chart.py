import random
import numpy as np
import matplotlib.pyplot as plt
from read_data import read_data_sensor, read_data_target


def test_chart(idcn, uavcn, sensor_num, target_num):
    # 第一幅图
    # x_data = ["第{}年".format(i) for i in range(16, 36)]
    # target_num = len(idcn)
    x_data = ["{}".format(i + 1) for i in range(target_num)]
    y_data = [i for i in idcn]
    plt.rcParams["font.sans-serif"] = ['SimHei']
    plt.rcParams["axes.unicode_minus"] = False

    # 创建第一个图形
    plt.figure(1)
    for i in range(len(x_data)):
        plt.bar(x_data[i], y_data[i])
        plt.text(x_data[i], y_data[i] + 0.1, str(y_data[i]), ha='center')

    plt.title("单个目标被无人机覆盖次数")
    plt.xlabel("目标id")
    plt.ylabel("覆盖次数")

    # 第二副图

    x_data2 = ["{}".format(i + 1) for i in range(sensor_num)]
    y_data2 = [i for i in uavcn]
    plt.rcParams["font.sans-serif"] = ['SimHei']
    plt.rcParams["axes.unicode_minus"] = False
    # 创建第一个图形
    plt.figure(2)
    for i in range(len(x_data2)):
        plt.bar(x_data2[i], y_data2[i])
        plt.text(x_data2[i], y_data2[i] + 0.1, str(y_data2[i]), ha='center')

    plt.title("单架无人机覆盖目标数量")
    plt.xlabel("无人机id")
    plt.ylabel("覆盖目标数量")
    plt.show()


def plot_map(x_bestx, x_besty, sensor_num, target_num,target_matrix,sensor_matrix):
    # target_matrix = read_data_target('target_data.json', target_num)
    # sensor_matrix = read_data_sensor('sensor_data.json', sensor_num)

    # 定义圆心坐标和半径
    centers = np.random.randint(low=0, high=20000, size=(sensor_num, 2))

    radius = np.array(range(sensor_num))
    #
    # print('centers.shape = ', centers.shape)
    # print('radius.shape = ', radius.shape)

    for i in range(sensor_num):
        # centers[i, 0] = x_best[i * 2]
        # centers[i, 1] = x_best[i * 2 + 1]
        centers[i, 0] = x_bestx[i]
        centers[i, 1] = x_besty[i]
        radius[i] = sensor_matrix[i, 2]

    # print('centers = \n', centers)
    # print('radius = \n', radius)

    # 定义散点坐标
    points = np.random.randint(low=0, high=20000, size=(target_num, 2))
    for i in range(target_num):
        points[i, 0] = target_matrix[i, 1]
        points[i, 1] = target_matrix[i, 2]

    # 创建一个新的图形窗口


    fig, ax = plt.subplots()

    rect = plt.Rectangle((0, 0), 20000, 20000, linewidth=1, edgecolor='red', facecolor='none')
    ax.add_patch(rect)

    # 绘制圆
    for center, r in zip(centers.tolist(), radius.tolist()):
        circle = plt.Circle(center, r, color='blue', fill=False)
        ax.add_artist(circle)

    # 绘制散点图
    x = points[:, 0]
    y = points[:, 1]
    ax.scatter(x, y, s=50, c='red', marker='.', alpha=0.8)

    # 设置坐标轴范围
    plt.xlim(-5000, 25000)
    plt.ylim(-5000, 25000)
    # 显示图形
    plt.show()
