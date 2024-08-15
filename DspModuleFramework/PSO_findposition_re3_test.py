import numpy as np
import time
import json
from datetime import datetime
from data_generate import data_generate
from get_fitness import get_fitness, get_only_fitness

import matplotlib.pyplot as plt
import matplotlib
from test_chart import test_chart, plot_map
from read_data import read_data_sensor, read_data_target
from save_result import save_result

# 记录程序开始时间
start_time = time.time()

# 生成数据
# target_num = 7
# sensor_num = 5
# data_generate(sensor_num, target_num)

target_num = 20
sensor_num = 20
data_generate(sensor_num, target_num)

# 初始化种群，群体规模，每个粒子的速度和规模
N = 500  # 种群数目
T = 40  # 最大迭代次数
# 算法运行次数 numofcy
numofcy = 10

N = 500
T = 80
numofcy = 10

N = 500
T = 50
numofcy = 10

# 这组参数不错
N = 200
T = 50
numofcy = 10

# N = 100
# T = 50
# numofcy = 1

# 要求单个目标被几架无人机覆盖
target_be_covered_num = 2

D = 2 * sensor_num  # 维度,2*sensor_num，每个传感器都有xy坐标
c1 = c2 = 1.5  # 个体学习因子与群体学习因子
w_max = 0.8  # 权重系数最大值
w_min = 0.4  # 权重系数最小值

# x_max = 4  # 每个维度最大取值范围，如果每个维度不一样，那么可以写一个数组，下面代码依次需要改变
# x_min = -4  # 同上
x_max = 20000
x_min = 0

# v_max = 1  # 每个维度粒子的最大速度
# v_min = -1  # 每个维度粒子的最小速度
v_max = 1000
v_min = -1000

print("----read_data_target---------")
target_matrix = read_data_target('target_data.json', target_num)
sensor_matrix = read_data_sensor('sensor_data.json', sensor_num)
# print('target_matrix = \n', target_matrix)
# print('sensor_matrix = \n', sensor_matrix)

target_num = int(target_matrix[-1, 0])
print('target_num = ', target_num)

sensor_num = int(sensor_matrix[-1, 0])
# sensor_num = 16
print('sensor_num = ', sensor_num)
# print(sensor_matrix)
print("----read_data_target end---------")

# 设置字体和设置负号
matplotlib.rc("font", family="KaiTi")
matplotlib.rcParams["axes.unicode_minus"] = False

ccn_sum_matrix = np.zeros((numofcy), dtype=int)
x_bestx_record = np.zeros((sensor_num, numofcy))
x_besty_record = np.zeros((sensor_num, numofcy))
idcn_numofcycle_matrix = np.zeros((target_num, numofcy), dtype=int)
uavcn_numofcycle_matrix = np.zeros((sensor_num, numofcy), dtype=int)

for numofcycle in range(numofcy):
    print(f"*******************算法第{numofcycle + 1}组************************")

    start_time_temp = time.time()
    # 初始化种群个体
    # x = np.random.rand(N, D) * (x_max - x_min) + x_min  # 初始化每个粒子的位置
    x = np.random.randint(low=0, high=20000, size=(N, D))

    # v = np.random.rand(N, D) * (v_max - v_min) + v_min  # 初始化每个粒子的速度
    v = np.random.randint(low=v_min, high=v_max, size=(N, D))

    # print('x.shape = ', x.shape)
    # print('v.shape = ', v.shape)
    #
    # print('x = ', x)
    # print('v = ', v)

    # 初始化个体最优位置和最优值
    p = x  # 用来存储每一个粒子的历史最优位置
    p_best = np.ones((N, 1))  # 每行存储的是最优值
    for i in range(N):  # 初始化每个粒子的最优值，此时就是把位置带进去，把适应度值计算出来
        # p_best[i] = func(x[i, :])
        # x_one = x[i, :]
        # print('x_one.shape = ', x_one.shape)
        # x_one = x_one.flatten()
        # p_best[i] = get_fitness(x_one, sensor_matrix, target_matrix, sensor_num, target_num)
        # scid, idcn, ccn, cn, fitness = get_fitness(x[i, :], sensor_matrix, target_matrix, sensor_num, target_num)
        p_best[i] = get_only_fitness(x[i, :], sensor_matrix, target_matrix, sensor_num, target_num)

    # 初始化全局最优位置和全局最优值
    g_best = -10000  # 设置真的全局最优值
    gb = np.zeros(T)  # 用于记录每一次迭代的全局最优值
    x_best = np.zeros(D)  # 用于存储最优粒子的取值

    # 按照公式依次迭代直到满足精度或者迭代次数
    for i in range(T):
        for j in range(N):
            # 个更新个体最优值和全局最优值
            fitness_temp = get_only_fitness(x[j, :], sensor_matrix, target_matrix, sensor_num, target_num)
            if p_best[j] < fitness_temp:
                p_best[j] = fitness_temp
                p[j, :] = x[j, :].copy()
            # p_best[j] = func(x[j,:]) if func(x[j,:]) < p_best[j] else p_best[j]
            # 更新全局最优值
            if g_best < p_best[j]:
                g_best = p_best[j]
                x_best = x[j, :].copy()  # 一定要加copy，否则后面x[j,:]更新也会将x_best更新
            # 计算动态惯性权重
            w = w_max - (w_max - w_min) * i / T
            # 更新位置和速度
            v[j, :] = w * v[j, :] + c1 * np.random.rand(1) * (p[j, :] - x[j, :]) + c2 * np.random.rand(1) * (
                    x_best - x[j, :])
            x[j, :] = x[j, :] + v[j, :]
            # 边界条件处理
            for ii in range(D):
                if (v[j, ii] > v_max) or (v[j, ii] < v_min):
                    v[j, ii] = v_min + np.random.rand(1) * (v_max - v_min)
                if (x[j, ii] > x_max) or (x[j, ii] < x_min):
                    x[j, ii] = x_min + np.random.rand(1) * (x_max - x_min)
        # 记录历代全局最优值
        gb[i] = g_best
    print("最优值为", gb[T - 1])
    # print("最优位置为\n", x_best)

    scid, idcn, uavcn, ccn, cn, fitness = get_fitness(x_best, sensor_matrix, target_matrix, sensor_num, target_num)

    idcn_numofcycle_matrix[:, numofcycle] = idcn
    uavcn_numofcycle_matrix[:, numofcycle] = uavcn

    ccn_sum = ccn.sum()

    ccn_sum_matrix[numofcycle] = ccn_sum

    for ir in range(sensor_num):
        # print('ir = ', ir)
        # print('numofcycle = ', numofcycle)
        # 数据按列分组，第一列是第一个循环的所有数，第二列是第二个循环的所有数字
        x_bestx_record[ir, numofcycle] = x_best[2 * ir]
        x_besty_record[ir, numofcycle] = x_best[2 * ir + 1]

    end_time_temp = time.time()
    run_time_temp = end_time_temp - start_time_temp
    save_result(x_best, idcn, uavcn, ccn, target_num, sensor_num, ccn_sum, cn, fitness, run_time_temp, numofcycle, N, T)
    # print('------------------------------------------------------------------')
    # print('scid = \n', scid)
    print('numofcycle = ', numofcycle)
    print('idcn = ', idcn)
    print('ccn = ', ccn)
    print('uavcn = ', uavcn)
    print('ccn_sum = ', ccn_sum)
    print('cn = ', cn)
    print('fitness = ', fitness)
    print(f"第{numofcycle + 1}组算法耗时{end_time_temp - start_time_temp}")

print("----------------------------所有组计算完成，开始选优--------------------------------------")

# idcn_numofcycle_matrix = np.zeros((target_num, numofcy), dtype=int)
useindex_k = -1
# useindex = np.zeros((numofcy), dtype=int)
useindex = np.full((numofcy), -1)
for i in range(numofcy):
    # print('i = ', i)
    if np.all(idcn_numofcycle_matrix[:, i] >= target_be_covered_num):
        print('进入矩阵')
        useindex_k += 1
        useindex[useindex_k] = i

# 如果找不到一组 每个目标被覆盖的次数都大于 target_be_covered_num 的话,将target_be_covered_num-1再试
print('useindex = ', useindex_k)

if useindex_k == -1:
    target_be_covered_num -= 1
    for i in range(numofcy):
        # print('i = ', i)
        if np.all(idcn_numofcycle_matrix[:, i] >= target_be_covered_num):
            print('进入矩阵')
            useindex_k += 1
            useindex[useindex_k] = i
print('useindex = ', useindex)

# 把useindex中后半部分带0元素所在列删掉
useindex_k2 = 0
for item in useindex:
    if item != -1:
        useindex_k2 += 1

print('useindex_k2 = ', useindex_k2)
useindex = useindex[0:useindex_k2]


print(f"所有目标被覆盖了{target_be_covered_num}次以上的组别列表：useindex = \n{useindex}")

ccn_sum_max_i = 0
ccn_sum_max = 0

for item in useindex:
    if ccn_sum_matrix[item] >= ccn_sum_max:
        ccn_sum_max = ccn_sum_matrix[item]
        ccn_sum_max_i = item

print(f"----------------------------在{numofcy}次中-----------------------------------")
print('ccn_sum_max_i = ', ccn_sum_max_i)
print('ccn_sum_max = ', ccn_sum_max)
print('idcn_numofcycle_matrix[] = ', idcn_numofcycle_matrix[:, ccn_sum_max_i])
print(f"uavcn_numofcycle_matrix[] = {uavcn_numofcycle_matrix[:, ccn_sum_max_i]}")

x_bestx = np.zeros((sensor_num), dtype=int)
x_besty = np.zeros((sensor_num), dtype=int)
x_bestx = x_bestx_record[:, ccn_sum_max_i]
x_besty = x_besty_record[:, ccn_sum_max_i]
print('x_bestx = ', x_bestx)
print('x_besty = ', x_besty)

# 记录程序结束时间
end_time = time.time()
# 计算程序运行时间
run_time = end_time - start_time
print("程序运行时间：", run_time, "秒")

# plt.plot(range(T), gb)
# plt.xlabel("迭代次数")
# plt.ylabel("适应度值")
# plt.title("适应度进化曲线")
# plt.show()

test_chart(idcn_numofcycle_matrix[:, ccn_sum_max_i], uavcn_numofcycle_matrix[:, ccn_sum_max_i], sensor_num, target_num)

#
# # 定义圆心坐标和半径
# centers = np.random.randint(low=0, high=20000, size=(sensor_num, 2))
#
# radius = np.array(range(sensor_num))
#
# print('centers.shape = ', centers.shape)
#
# print('radius.shape = ', radius.shape)
#
# for i in range(sensor_num):
#     # centers[i, 0] = x_best[i * 2]
#     # centers[i, 1] = x_best[i * 2 + 1]
#     centers[i, 0] = x_bestx[i]
#     centers[i, 1] = x_besty[i]
#     radius[i] = sensor_matrix[i, 2]
#
# # print('centers = \n', centers)
# # print('radius = \n', radius)
#
# # 定义散点坐标
# points = np.random.randint(low=0, high=20000, size=(target_num, 2))
# for i in range(target_num):
#     points[i, 0] = target_matrix[i, 1]
#     points[i, 1] = target_matrix[i, 2]
#
# # 创建一个新的图形窗口
# fig, ax = plt.subplots()
#
# rect = plt.Rectangle((0, 0), 20000, 20000, linewidth=1, edgecolor='red', facecolor='none')
# ax.add_patch(rect)
#
# # 绘制圆
# for center, r in zip(centers.tolist(), radius.tolist()):
#     circle = plt.Circle(center, r, color='blue', fill=False)
#     ax.add_artist(circle)
#
# # 绘制散点图
# x = points[:, 0]
# y = points[:, 1]
# ax.scatter(x, y, s=50, c='red', marker='.', alpha=0.8)
#
# # 设置坐标轴范围
# plt.xlim(-5000, 25000)
# plt.ylim(-5000, 25000)
# # 显示图形
# plt.show()
plot_map(x_bestx, x_besty, sensor_num, target_num)
