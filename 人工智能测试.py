from sko.GA import GA, GA_TSP
from sko.DE import DE
from sko.PSO import PSO
from sko.ACA import ACA_TSP
from sko.tools import set_run_mode
import torch
import numpy as np
import csv

a_list = [200, 142.5, 380, 210, 307, 410, 50, 200, 600, 200, 143, 10]
# 读取数据
with open('data/潮流缺额与剩余随时间变化数据.csv', 'r') as f:
    reader = csv.reader(f)
    b_list = list(reader)
    b_list = b_list[0]
    b_list = [float(i) for i in b_list]


def target_func(x):
    global j
    for i in range(10):
        for j in range(96):
            # x0_0, x1_1, ... = x
            globals()['x{}_{}'.format(i, j)] = x[i * 96 + j]
            globals()['x{}_{}'.format(i+10, j)] = x[i * 96 + j + 960]
    # 定义目标函数，将下面的sum改为目标函数
    return 2.94 * sum([eval(f"abs(x{i}_{j})") for i in range(10) for j in range(96)]) + 102e4 * sum([(
            3e-4 - 0.009 * (eval(f"x{i+10}_{j}") / 60 / a_list[i] - (1 - 1 / 3000) ** (1 / 2.66)
                            * a_list[i] / 60 / 15)) * a_list[i] / 365 / 96 / 1e3 for i in range(10) for j in range(96)])


lb = []
ub = []
for i in range(10):
    for j in range(96):
        lb.append(-a_list[i])
        ub.append(a_list[i])
for i in range(10):
    for j in range(96):
        lb.append(0.4 * a_list[i])
        ub.append(1.6 * a_list[i])
constraint_eq = ()
for j in range(96):
    constraint_eq += (lambda x: sum([eval(f"max(x{i}_{j}, 0.9 * x{i}_{j})") for i in range(10)]) - b_list[j],)
for i in range(10):
    for j in range(96):
        constraint_eq += (lambda x: eval(f"x{i+10}_{j}") - eval(f"max(x{i}_{j}, 0.9 * x{i}_{j})") * 0.25,)
constraint_ueq = ()
for i in range(10):
    for j in range(96):
        constraint_ueq += (lambda x: eval(f"x{i+10}_{j}") - 1.6 * a_list[i],)
        constraint_ueq += (lambda x: -eval(f"x{i+10}_{j}") + 0.4 * a_list[i],)

ga = GA(func=target_func, n_dim=1920, size_pop=50, max_iter=80, lb=lb, ub=ub, constraint_eq=constraint_eq, precision=1e-7)
# de = DE(func=target_func, n_dim=1920, size_pop=50, max_iter=80, lb=lb, ub=ub, constraint_eq=constraint_eq)
# ga = PSO(func=target_func, dim=1920, pop=50, max_iter=80, lb=lb, ub=ub, constraint_eq=constraint_eq)
# ga = ACA_TSP(func=target_func, n_dim=1920, size_pop=50, max_iter=80, lb=lb, ub=ub, constraint_eq=constraint_eq)
set_run_mode(ga, "vectorization")
set_run_mode(ga, "cached")
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(torch.version.cuda)
best_x, best_y = ga.run()
print(len(best_x))
best_x = np.array(best_x)
best_x = best_x.reshape(20, 96)
best_y = np.array(best_y)
best_y = best_y.reshape(1, 1)

best_x = best_x.tolist()
best_y = best_y.tolist()
with open('data/最优解GA.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(best_x)
    writer.writerows(best_y)
print('best_x:', best_x, '\n', 'best_y:', best_y)
