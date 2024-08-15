import numpy as np


# from math import comb


# fitness(x[i, :], sensor_matrix, target_matrix, sensor_num, target_num)
# 输入x[i,:]是一维的行向量 有 sensor_num*2 列
def get_fitness(x_one, sensor_matrix, target_matrix, sensor_num, target_num):
    # scid : sensor cover id 代表每个传感器覆盖的目标id 维度为 sensor_num * target_num
    scid = np.zeros((sensor_num, target_num), dtype=int)

    # idcn : id covered num 代表每个目标id 被覆盖的次数, 这里示例计算传感器0 种群0 的计算方式，是计算它与 其2、3、4号等等传感器的所有种群的 重复覆盖每个目标的重复个数
    # idcn = np.zeros((1, target_num), dtype=int)

    # uavcn,每架无人机覆盖的目标数目

    # ccn : Cross coverage num 代表交叉覆盖的数量, 计算方式同一个目标被8个传感器覆盖，则为comb(8,2)
    ccn = np.zeros(target_num, dtype=int)

    # cn cover num 总覆盖目标数，数量为 0 - target_num
    cn = int(0)

    # print('ccn.shape = ', ccn.shape)
    # print('x_one.shape = ', x_one.shape)

    for i in range(sensor_num):
        x = x_one[2 * i]
        y = x_one[2 * i + 1]
        for j in range(target_num):
            if (x - target_matrix[j, 1]) ** 2 + (y - target_matrix[j, 2]) ** 2 <= sensor_matrix[i, 3] - 360000:
                scid[i, j] = 1
        # 按行求和
    idcn = np.sum(scid, axis=0)
    uavcn = np.sum(scid, axis=1)

    # print('type(idcn) = ', type(idcn))
    # print('type(scid) = ', type(scid))
    #
    # print('idcn = \n', idcn)
    # print('idcn.shape = ', idcn.shape)
    #
    # print('target_num = ', target_num)
    # print('ccn.shape = ', ccn.shape)

    for k in range(target_num):
        # print('k = ', k)
        # ccn[i] = comb(2, idcn[i])
        # ccn[k] = 0
        # print('idcn[k] = ', idcn[k])
        if idcn[k] != 0:
            cn += 1
            if idcn[k] == 1:
                ccn[k] = 0
            else:
                # ccn[k] = comb(idcn[k], 2)
                ccn[k] = idcn[k] * (idcn[k] - 1) / 2

    # print('ccn = \n', ccn)
    # print('覆盖了 cn = ', cn, '个目标')

    idcn_sum = idcn.sum()
    ccn_sum = ccn.sum()
    maxof2 = max(idcn_sum, ccn_sum)

    # 第1种目标函数策略：
    # fitness = maxof2 * cn / target_num * 2 + idcn_sum + ccn_sum
    #
    # for g in idcn:
    #     if g == 0:
    #         fitness = int(fitness/2)
    #
    # for g2 in ccn:
    #     if g2 == 0:
    #         fitness = int(fitness/2)

    # 第2种目标函数策略：
    # fitness = 0
    # for g in idcn:
    #     if g >= 4:
    #         fitness += 16
    #     if g == 3:
    #         fitness += 8
    #     if g == 2:
    #         fitness -= 4
    #     if g == 1:
    #         fitness -= 8
    #     if g == 0:
    #         fitness -= 32
    #
    #
    # for g in uavcn:
    #     if g >= 4:
    #         fitness += 16
    #     if g == 3:
    #         fitness += 6
    #     if g == 2:
    #         fitness += 4
    #     if g == 1:
    #         fitness -= 4
    #     if g == 0:
    #         fitness -= 16

    # 第3种目标函数策略：
    fitness1 = 0
    for g in idcn:
        if g >= 4:
            fitness1 += 32
        if g == 3:
            fitness1 += 24
        if g == 2:
            fitness1 += 16
        if g == 1:
            fitness1 -= 128
        if g == 0:
            fitness1 -= 128

    fitness2 = 0
    for g in uavcn:
        if g >= 4:
            fitness2 += 32
        if g == 3:
            fitness2 += 32
        if g == 2:
            fitness2 += 16
        if g == 1:
            fitness2 += 8
        if g == 0:
            fitness2 -= 128

    # fitness = fitness1 * target_num / (target_num + sensor_num) + fitness2 * sensor_num / (target_num + sensor_num)
    fitness = fitness1 + fitness2

    # 第4种覆盖策略
    # idcn_average = idcn_sum / sensor_num
    # fitness = 1000
    # if idcn_sum < target_num * 2:
    #     fitness = 0
    # else:
    #     for g in idcn:
    #         fitness -= abs(g - idcn_average)
    #
    # for g in uavcn:
    #     if g == 0:
    #         fitness -= 1

    # print('maxof2 * cn / target_num = ', maxof2 * cn / target_num)
    # print('idcn_sum = ', idcn_sum)
    # print('ccn_sum = ', ccn_sum)
    # print('fitness = ', fitness)

    return scid, idcn, uavcn, ccn, cn, fitness


def get_only_fitness(x_one, sensor_matrix, target_matrix, sensor_num, target_num):
    scid, idcn, uavcn, ccn, cn, fitness = get_fitness(x_one, sensor_matrix, target_matrix, sensor_num, target_num)
    return fitness
