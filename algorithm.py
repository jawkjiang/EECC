# -*- coding: utf-8 -*-

import csv
import numpy
import matlab.engine
import cnn_lstm_stock.cnnlstm_stock as cnnlstm
from sko.GA import GA, GA_TSP
from sko.DE import DE
from sko.PSO import PSO
from sko.ACA import ACA_TSP
from sko.tools import set_run_mode


def loss_read():
    with open('data/潮流缺额与剩余随时间变化数据.csv', 'r') as f:
        reader = csv.reader(f)
        loss_list = list(reader)
        loss_list = loss_list[0]
        loss_list = [float(i) for i in loss_list]
    return loss_list


def station_read():
    with open('data/电站数据.csv', 'r') as f:
        reader = csv.reader(f)
        # 电站数据为n*4的矩阵，第一列为电站名称，第二列为电站类型str，第三列为电站最大出力float，第四列为备注
        station_list = list(reader)
        # 取第二列和第三列的数据，保留数据类型
        station_list = [[i[1], float(i[2])] for i in station_list]

    return station_list


def linear_planning():
    pass


def AI_planing(loss_list, station_list):
    # 分别对三种电站存储最大出力序列
    H2_power = []
    ele_power = []
    water_power = []

    # 读取电站数据
    for i in station_list:
        if i[0] == 'H2':
            H2_power.append(i[1])
        elif i[0] == 'ele':
            ele_power.append(i[1])
        elif i[0] == 'water':
            water_power.append(i[1])

    # 目标函数建模
    def obj_func(x):

        for i in range(len(H2_power)):
            for j in range(96):
                # 氢能源出力序列
                globals()[f'x_{i}_{j}'] = x[i * 96 + j]
                # 氢能源容量序列
                globals()[f'x_{i + len(H2_power)}_{j}'] = x[96 * len(H2_power) + i * 96 + j]

        for i in range(len(ele_power)):
            for j in range(96):
                # 电化学出力序列
                globals()[f'y_{i}_{j}'] = x[96 * 2 * len(H2_power) + i * 96 + j]
                # 电化学容量序列
                globals()[f'y_{i + len(ele_power)}_{j}'] = x[96 * 2 * len(H2_power) + 96 * len(ele_power) + i * 96 + j]

        for i in range(len(water_power)):
            for j in range(96):
                # 抽水蓄能开关序列
                globals()[f'z_{i}_{j}'] = x[96 * 2 * len(H2_power) + 96 * 2 * len(ele_power) + i * 96 + j]
                # 抽水蓄能容量序列
                globals()[f'z_{i + len(water_power)}_{j}'] = x[96 * 2 * len(H2_power) + 96 * 2 * len(ele_power) +
                                                               96 * len(water_power) + i * 96 + j]

        return \
                sum(eval(f"max(1.89 * x_{i}_{j}, -1.3 * x_{i}_{j})") for i in range(len(H2_power)) for j in range(96)) + \
 \
                2.94 * sum([eval(f"abs(y{i}_{j})") for i in range(len(ele_power)) for j in range(96)]) \
                + 102e4 * sum([(3e-4 - 0.009 * (eval(f"y{i + len(ele_power)}_{j}") / 60 / ele_power[i]
                                                - (1 - 1 / 3000) ** (1 / 2.66) * ele_power[i] / 60 / 15)) * ele_power[
                                   i] / 365 / 96 / 1e3
                               for i in range(len(ele_power)) for j in range(96)]) + \
 \
                sum([loss_list[i] * globals()[f'z_{i}'] for i in range(len(water_power))])

    # 约束条件建模
    # 等式约束建模
    constraint_eq = ()
    # 氢能源容量与出力关系
    for i in range(len(H2_power)):
        for j in range(96):
            if j == 0:
                constraint_eq += (lambda x: eval(f"x{i + len(H2_power)}_{j}") - 500,)
            else:
                constraint_eq += (lambda x: eval(f"x{i + len(H2_power)}_{j}") - eval(f"x{i + len(H2_power)}_{j - 1}") +
                                            max(eval(f"x{i}_{j - 1}") * 15 * 60 / 2 / 96485.33289 / 0.55 / 150 * 1e3,
                                                eval(f"x{i}_{j - 1}") * 15 * 0.75 * 60 / 15 * 1e-3),)
    # 电化学容量与出力关系
    for i in range(len(ele_power)):
        for j in range(96):
            if j == 0:
                constraint_eq += (lambda x: eval(f"y{i + len(ele_power)}_{j}") - ele_power[i],)
            else:
                constraint_eq += (lambda x: eval(f"y{i + len(ele_power)}_{j}") - eval(f"y{i + len(ele_power)}_{j - 1}") +
                                            eval(f"max(x{i}_{j}, 0.9 * x{i}_{j})") * 0.25,)
    # 抽水蓄能容量与开关状态关系


    # 不等式约束建模
    constraint_ueq = ()
    # 氢能源容量约束
    for i in range(len(H2_power)):
        for j in range(96):
            constraint_ueq += (lambda x: -eval(f"x{i + len(H2_power)}_{j}"))
            constraint_ueq += (lambda x: eval(f"x{i + len(H2_power)}_{j}") * 8.314 * 300 / 1000 - 14700000,)
    # 电化学容量约束
    for i in range(len(ele_power)):
        for j in range(96):
            constraint_ueq += (lambda x: eval(f"y{i + len(ele_power)}_{j}") - 1.6 * ele_power[i],)
            constraint_ueq += (lambda x: -eval(f"y{i + len(ele_power)}_{j}") + 0.4 * ele_power[i],)

    def GA_planning():
        pass

    def PSO_planning():
        pass

    def DE_planning():
        pass

    def ACA_planning():
        pass

    def GA_TSP_planning():
        pass


def main():
    pass


if __name__ == '__main__':
    main()
