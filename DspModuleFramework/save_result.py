import json
import numpy as np
from datetime import datetime


# 生成要保存的矩阵数据和其他变量

# idcn = np.array([4, 3, 4, 7, 8, 7, 3, 5, 4, 4, 2, 6, 6, 4, 4, 7, 2, 4, 5, 4, 6])
# ccn = np.array([[6, 3, 6, 21, 28, 21, 3, 10, 6, 6, 1, 15, 15, 6, 6, 21, 1, 6, 10, 6, 15]])
# target_num = 21
# sensor_num = 16
# ccn_sum = 212
# cn = 21
# fitness = 99


def save_result(x_best, idcn, uavcn, ccn, target_num, sensor_num, ccn_sum, cn, fitness, run_time, numofcycle, N, T):
    target_num = int(target_num)
    sensor_num = int(sensor_num)
    ccn_sum = int(ccn_sum)
    cn = int(cn)
    fitness = int(fitness)
    run_time = float(run_time)

    # print('x_best.shape = ', x_best.shape)
    x_bestx = np.zeros((sensor_num,))
    x_besty = np.zeros((sensor_num,))

    for i in range(sensor_num):
        # print('i = ', i)
        x_bestx[i] = x_best[2 * i]
        x_besty[i] = x_best[2 * i + 1]

    # 创建一个包含所有数据的字典
    data2 = {
        'timestamp': datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        'population: N = ': N,
        'iterations: T = ': T,
        'target_num': target_num,
        'sensor_num': sensor_num,
        'ccn_sum': ccn_sum,
        'cn': cn,
        'fitness': fitness,
        'runtime': run_time,
        'uavcn ': uavcn.astype(int).tolist(),
        'idcn': idcn.astype(int).tolist(),
        'ccn': ccn.astype(int).tolist(),
        'x_bestx': x_bestx.astype(int).tolist(),
        'x_besty': x_besty.astype(int).tolist()
    }

    # 将数据保存为JSON文件
    filename = data2['timestamp'] + '第' + str(numofcycle) + '次' + '.json'
    with open(filename, 'w') as file:
        json.dump(data2, file, indent=4)

    print(f"数据已保存到 {filename} 文件中。")
