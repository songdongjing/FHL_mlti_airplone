import numpy as np
import math


def GetClockAngle(v1, v2):
    # 2个向量模的乘积
    TheNorm = np.linalg.norm(v1) * np.linalg.norm(v2)
    # 叉乘
    rho = np.rad2deg(np.arcsin(np.cross(v1, v2) / TheNorm))
    # 点乘
    theta = np.rad2deg(np.arccos(np.dot(v1, v2) / TheNorm))

    # print('theta = ', theta)
    if rho > 0:
        return 360 - theta
    else:
        return theta


def GetHeading(current_pos_m, goal_pos_m, sensor_num):
    heading_matrix = np.zeros((sensor_num, 1))

    for i in range(sensor_num):
        v2 = [goal_pos_m[i, 0] - current_pos_m[i, 0], goal_pos_m[i, 1] - current_pos_m[i, 1]]
        v1 = [0, 1]
        heading_matrix[i, 0] = GetClockAngle(v1, v2)
    return heading_matrix


def GetAFlyTime(p1, p2):
    vel = 30
    vel2 = 900
    distance2 = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
    t2 = distance2 / vel2
    # t = round(math.sqrt(t2))
    t = math.sqrt(t2)
    return t


def GetFlyTimes(current_pos_m, goal_pos_m, sensor_num):
    flytimes = np.zeros((sensor_num, 1))
    for i in range(sensor_num):
        p1 = [current_pos_m[i, 0], current_pos_m[i, 1]]
        p2 = [goal_pos_m[i, 0], goal_pos_m[i, 1]]
        flytimes[i, 0] = GetAFlyTime(p1, p2)
    return flytimes


# sensor_num1 = 20
# current_pos_m1 = np.random.randint(0, 2, size=(sensor_num1, 2))
# goal_pos_m1 = np.random.randint(0, 20001, size=(sensor_num1, 2))
# print('current_pos_m = \n', current_pos_m1)
# print('goal_pos_m = \n', goal_pos_m1)
#
# heading_matrix1 = GetHeading(current_pos_m1, goal_pos_m1, sensor_num1)
# print('heading_matrix = \n', heading_matrix1)
# print('goal_pos_m[19,0] - current_pos_m[19,0] = ', goal_pos_m1[19, 0] - current_pos_m1[19, 0])
# print('goal_pos_m[19,1] - current_pos_m[19,1] = ', goal_pos_m1[19, 1] - current_pos_m1[19, 1])
#
# print('------------------------------------------')
# flytimes1 = GetFlyTimes(current_pos_m1, goal_pos_m1, sensor_num1)
# print('flytimes1 = \n', flytimes1)
