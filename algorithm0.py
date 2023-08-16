# -*- coding: utf-8 -*-

import csv
import numpy as np
import matlab
from sko.GA import GA
from sko.PSO import PSO
from sko.DE import DE
from sko.SA import SA
from sko.AFSA import AFSA
from sko.tools import set_run_mode


def loss_read(path):
    with open(path, 'r') as f:
        reader = csv.reader(f)
        loss_list = list(reader)
        loss_list = loss_list[0]
        loss_list = [float(i) for i in loss_list]
    return loss_list


def station_read(path):
    with open(path, 'r') as f:
        reader = csv.reader(f)
        # 电站数据为n*4的矩阵，第一列为电站名称，第二列为电站类型str，第三列为电站最大出力float，第四列为备注
        station_list = list(reader)
        # 取第二列和第三列的数据，保留数据类型
        station_list = [[i[1], float(i[2])] for i in station_list]

    return station_list


def linear_planning():
    pass


class AI_planing:

    def __init__(self, loss_list, station_list):
        self.loss_list = loss_list
        self.station_list = station_list
        # 分别对三种电站存储最大出力序列
        self.H2_power = []
        self.ele_power = []
        self.water_power = []

        # 读取电站数据
        for i in self.station_list:
            if i[0] == '氢储能':
                self.H2_power.append(i[1])
            elif i[0] == '电化学':
                self.ele_power.append(i[1])
            elif i[0] == '抽水蓄能':
                self.water_power.append(i[1])

        # 目标函数建模
        def obj_func(x):

            for i in range(len(self.H2_power)):
                for j in range(96):
                    # 氢能源出力序列
                    globals()[f'x{i}_{j}'] = x[i * 96 + j]
                    # 氢能源容量序列

            for i in range(len(self.ele_power)):
                for j in range(96):
                    # 电化学出力序列
                    globals()[f'y{i}_{j}'] = x[96 * len(self.H2_power) + i * 96 + j]
                    # 电化学容量序列

            for i in range(len(self.water_power)):
                for j in range(96):
                    # 抽水蓄能出力序列
                    globals()[f'z{i}_{j}'] = x[96 * len(self.H2_power) + 96 * len(self.ele_power) + i * 96 + j]
                    # 抽水蓄能容量序列

            return \
                    sum(eval(f"max(1.89 * x{i}_{j}, -1.3 * x{i}_{j})") for i in range(len(self.H2_power)) for j in
                        range(96)) + \
\
 \
                    2.94 * sum([eval(f"abs(y{i}_{j})") for i in range(len(self.ele_power)) for j in range(96)]) \
\
                    + 102e4 * sum([(
                                           3e-4 - 0.009 * (self.ele_power[i] / 60 / self.ele_power[i]
                                                            - (1 - 1 / 3000) ** (1 / 2.66) * self.ele_power[i] / 60 / 15))
                                   * self.ele_power[i] / 365 / 96 / 1e3 for i in range(len(self.ele_power))]) \
 \
                    + 102e4 * sum([(
                                           3e-4 - 0.009 * ((self.ele_power[i]
                                                           - 0.25 * sum(eval(f"max(y{i}_{l}, 0.9 * y{i}_{l})") for l in range(j)))
                                                            / 60 / self.ele_power[i]
                                            - (1 - 1 / 3000) ** (1 / 2.66) * self.ele_power[i] / 60 / 15))
                                   * self.ele_power[i] / 365 / 96 / 1e3
                                   for i in range(len(self.ele_power)) for j in range(1, 96)]) + \
 \
\
                    100 * sum(eval(f"abs(z{i}_{j})") for i in range(len(self.water_power)) for j in range(96))

        self.obj_func = obj_func
        self.n_dim = 96 * (len(self.H2_power) + len(self.ele_power) + len(self.water_power))

        # 约束条件建模
        # 上下限约束建模
        self.ub = []
        self.lb = []
        for i in range(len(self.H2_power)):
            for j in range(96):
                self.ub.append(self.H2_power[i])
                self.lb.append(-self.H2_power[i])
        for i in range(len(self.ele_power)):
            for j in range(96):
                self.ub.append(self.ele_power[i])
                self.lb.append(-self.ele_power[i])
        for i in range(len(self.water_power)):
            for j in range(96):
                self.ub.append(self.water_power[i])
                self.lb.append(-self.water_power[i])

        '''
        # 等式约束建模
        self.constraint_eq = ()
        # 氢能源容量与出力关系
        for i in range(len(self.H2_power)):
            for j in range(96):
                if j == 0:
                    self.constraint_eq += (lambda x: eval(f"x{i + len(self.H2_power)}_{j}") - 500,)
                else:
                    self.constraint_eq += (
                        lambda x: eval(f"x{i + len(self.H2_power)}_{j}") - eval(f"x{i + len(self.H2_power)}_{j - 1}") +
                                  eval(f"max(x{i}_{j - 1} * 15 * 60 / 2 / 96485.33289 / 0.55 / 150 * 1e3,"
                                       f" x{i}_{j - 1} * 15 * 0.75 * 60 / 15 * 1e-3)"),)
        for i in range(len(self.ele_power)):
            for j in range(96):
                # if j == 0, y{i + len(self.ele_power)}_{j} = self.ele_power[i]
                # if j != 0, y{i + len(self.ele_power)}_{j} = y{i + len(self.ele_power)}_{j - 1}
                # - eval(f"max(x{i}_{j - 1}, 0.9 * x{i}_{j - 1})") * 0.25,)
                # that means we can delete the volume constraint
                # if j != 0, y{i + len(self.ele_power)}_{j} = self.ele_power[i]
                # - sum(max(x{i}_{j - 1}, 0.9 * x{i}_{j - 1}) for i in range(len(self.ele_power)) for j in range(1, 96)) * 0.25
                if j == 0:
                    self.constraint_eq += (lambda x: eval(f"y{i + len(self.ele_power)}_{j}") - self.ele_power[i],)
                else:
                    self.constraint_eq += (
                        lambda x: eval(f"y{i + len(self.ele_power)}_{j}") - eval(
                            f"y{i + len(self.ele_power)}_{j - 1}") +
                                  eval(f"max(x{i}_{j - 1}, 0.9 * x{i}_{j - 1})") * 0.25,)
        # 抽水蓄能容量与出力关系
        for i in range(len(self.water_power)):
            for j in range(96):
                if j == 0:
                    self.constraint_eq += (lambda x: eval(f"z{i + len(self.water_power)}_{j}") - 1146.5 * 1e4 / 2,)
                else:
                    self.constraint_eq += (
                        lambda x: eval(f"z{i + len(self.water_power)}_{j}") - eval(
                            f"z{i + len(self.water_power)}_{j - 1}") +
                                  eval(f"max(x{i}_{j - 1}, 0.75 * x{i}_{j - 1})") * 0.25 * 15 * 60 / 2000 / 9.8 / 1000 * 1e6,)
        # 潮流缺额约束
        for j in range(96):
            self.constraint_eq += (
                lambda x: sum(eval(f"min(x{i}_{j}, 0.55 * x{i}_{j})") for i in range(len(self.H2_power))) +
                          sum(eval(f"min(y{i}_{j}, 0.9 * y{i}_{j})") for i in range(len(self.ele_power))) +
                          sum(eval(f"min(z{i}_{j}, 0.75 * z{i}_{j})") for i in range(len(self.water_power))) -
                          self.loss_list[j],)
        '''

        # 不等式约束建模
        self.constraint_ueq = ()
        # 氢能源容量约束
        for i in range(len(self.H2_power)):
            for j in range(1, 96):

                self.constraint_ueq += (lambda x: -500 + sum(eval(
                    f"max(x{i}_{l} * 15 * 60 / 2 / 96485.33289 / 0.55 / 150 * 1e3, x{i}_{l} * 15 * 0.75 * 60 / 15 * 1e-3)")
                    for l in range(j)),)

                self.constraint_ueq += (lambda x: (500 - sum(eval(
                    f"max(x{i}_{l} * 15 * 60 / 2 / 96485.33289 / 0.55 / 150 * 1e3, x{i}_{l} * 15 * 0.75 * 60 / 15 * 1e-3)")
                    for l in range(j))) * 8.314 * 300 / 1000
                                             - 14700000,)

        # 电化学容量约束
        for i in range(len(self.ele_power)):
            for j in range(1, 96):

                self.constraint_ueq += (lambda x: self.ele_power[i] - 0.25 * sum(eval(f"max(y{i}_{l}, 0.9 * y{i}_{l})") for l in range(j))
                                             - 1.6 * self.ele_power[i],)

                self.constraint_ueq += (lambda x: -self.ele_power[i] + 0.25 * sum(eval(f"max(y{i}_{l}, 0.9 * y{i}_{l})") for l in range(j))
                                             + 0.4 * self.ele_power[i],)

        # 抽水蓄能容量约束
        for i in range(len(self.water_power)):
            for j in range(1, 96):

                self.constraint_ueq += (lambda x: self.ele_power[i] - 0.25 * 15 * 60 / 2000 / 9.8 / 1000 * 1e6 * sum(eval(f"max(z{i}_{l}, 0.75 * z{i}_{l})") for l in range(j))
                                             - 1146.5 * 1e4,)

                self.constraint_ueq += (lambda x: -self.ele_power[i] + 0.25 * 15 * 60 / 2000 / 9.8 / 1000 * 1e6 * sum(
                    eval(f"max(z{i}_{l}, 0.75 * z{i}_{l})") for l in range(j)),)


        # 潮流缺额约束
        for j in range(96):
            self.constraint_ueq += (
                lambda x: sum(eval(f"min(x{i}_{j}, 0.55 * x{i}_{j})") for i in range(len(self.H2_power))) +
                          sum(eval(f"min(y{i}_{j}, 0.9 * y{i}_{j})") for i in range(len(self.ele_power))) +
                          sum(eval(f"min(z{i}_{j}, 0.75 * z{i}_{j})") for i in range(len(self.water_power)))
                          - 1.1 * self.loss_list[j],)
            self.constraint_ueq += (
                lambda x: -sum(eval(f"min(x{i}_{j}, 0.55 * x{i}_{j})") for i in range(len(self.H2_power))) -
                          sum(eval(f"min(y{i}_{j}, 0.9 * y{i}_{j})") for i in range(len(self.ele_power))) -
                          sum(eval(f"min(z{i}_{j}, 0.75 * z{i}_{j})") for i in range(len(self.water_power)))
                          + 0.9 * self.loss_list[j],)


        self.best_x = None
        self.best_y = None
        self.best_H2_power = None
        self.best_ele_power = None
        self.best_water_power = None

    def GA_planning(self, size_pop, max_iter, prob_mut, precision):
        result = GA(func=self.obj_func, n_dim=self.n_dim, size_pop=size_pop, max_iter=max_iter, prob_mut=prob_mut,
                    lb=self.lb, ub=self.ub, constraint_ueq=self.constraint_ueq, precision=precision)
        return result

    def PSO_planning(self, size_pop, max_iter, w, c1, c2):
        result = PSO(func=self.obj_func, n_dim=self.n_dim, pop=size_pop, max_iter=max_iter,
                     lb=self.lb, ub=self.ub, w=w, c1=c1, c2=c2, constraint_ueq=self.constraint_ueq)
        return result

    def DE_planning(self, size_pop, max_iter, prob_mut, F):
        result = DE(func=self.obj_func, n_dim=self.n_dim, size_pop=size_pop, max_iter=max_iter, prob_mut=prob_mut, F=F,
                    lb=self.lb, ub=self.ub, constraint_ueq=self.constraint_ueq)
        return result

    def SA_planning(self, T_max, T_min, L, max_stay_counter):
        ga = AI_planing.GA_planning(self, 50, 1, 0.001, 1e-7)
        ga.run()
        x0 = ga.best_x
        result = SA(func=self.obj_func, n_dim=self.n_dim, x0=x0, T_max=T_max, T_min=T_min, L=L,
                    max_stay_counter=max_stay_counter)
        return result

    def AFSA_planning(self, size_pop, max_iter, max_try_num, step, visual, q, delta):
        result = AFSA(func=self.obj_func, n_dim=self.n_dim, size_pop=size_pop, max_iter=max_iter,
                      max_try_num=max_try_num, step=step, visual=visual, q=q, delta=delta)
        return result

    def calculate(self, method, times, **kargs):
        result = method(**kargs)
        set_run_mode(result, "vectorization")
        if method == self.SA_planning:
            best_x, best_y = result.run()
        else:
            best_x, best_y = result.run(times)
        best_x = np.array(best_x)
        best_x = best_x.reshape(int(self.n_dim / 96), 96)
        if method == self.AFSA_planning:
            best_x = 1000 * best_x
            best_y = 1000 * best_y
        best_x = best_x.tolist()
        best_y = np.array(best_y)
        best_y = best_y.reshape(1, 1)
        best_y = best_y.tolist()
        # 将best_x中的出力数据筛选出来
        best_x = best_x[0: len(self.H2_power)] + \
                 best_x[len(self.H2_power): len(self.H2_power) + len(self.ele_power)] + \
                 best_x[len(self.H2_power) + len(self.ele_power): len(self.H2_power) + len(
                     self.ele_power) + len(self.water_power)]
        # 筛选氢储能出力数据
        for i in range(len(self.H2_power)):
            for j in range(96):
                best_x[i][j] = best_x[i][j] * 0.55
        self.best_H2_power = best_x[0: len(self.H2_power)]
        # 筛选电化学储能出力数据
        for i in range(len(self.ele_power)):
            for j in range(96):
                best_x[i + len(self.H2_power)][j] = best_x[i + len(self.H2_power)][j] * 0.9
        self.best_ele_power = best_x[len(self.H2_power): len(self.H2_power) + len(self.ele_power)]
        # 筛选抽水蓄能出力数据
        for i in range(len(self.water_power)):
            for j in range(96):
                best_x[i + len(self.H2_power) + len(self.ele_power)][j] = \
                    best_x[i + len(self.H2_power) + len(self.ele_power)][j] * 0.75
        self.best_water_power = best_x[len(self.H2_power) + len(self.ele_power): len(self.H2_power) + len(
            self.ele_power) + len(self.water_power)]
        self.best_x = best_x
        self.best_y = best_y


def main():
    loss_list = loss_read("data/湖南_loss.csv")
    station_list = station_read("data/湖南_station.csv")
    ai_planing = AI_planing(loss_list, station_list)
    ai_planing.calculate(ai_planing.GA_planning, 1, size_pop=50, max_iter=1, prob_mut=0.001, precision=1e-7)
    best_x = ai_planing.best_x
    best_y = ai_planing.best_y
    with open('data/最优解GA1.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(best_x)
        writer.writerows(best_y)
    print('best_x:', best_x, '\n', 'best_y:', best_y)


if __name__ == '__main__':
    main()
