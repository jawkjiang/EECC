import pulp
import csv
import matplotlib.pyplot as plt

a_list = [200, 142.5, 380, 210, 307, 410, 50, 200, 600, 200, 143, 10]
with open('data/潮流缺额与剩余随时间变化数据.csv', 'r') as f:
    reader = csv.reader(f)
    b_list = list(reader)
    b_list = b_list[0]
    b_list = [float(i) for i in b_list]


def main():
    # 问题初始化
    prob = pulp.LpProblem("test1", pulp.LpMinimize)

    # 定义变量
    for i in range(10):
        for j in range(96):
            globals()['x{}_{}'.format(i + 1, j + 1)] = pulp.LpVariable("x{}_{}".format(i + 1, j + 1),
                                                                       lowBound=-a_list[i], upBound=a_list[i],
                                                                       cat=pulp.LpInteger)
            globals()['y{}_{}'.format(i + 1, j + 1)] = pulp.LpVariable("y{}_{}".format(i + 1, j + 1),
                                                                       lowBound=0.4 * a_list[i],
                                                                       upBound=1.6 * a_list[i],
                                                                       cat=pulp.LpInteger)

    # 定义目标函数
    prob += pulp.lpSum([globals()['x{}_{}'.format(i + 1, j + 1)] for i in range(10) for j in range(96)])

    # 定义约束条件
    for i in range(10):
        for j in range(96):
            prob += globals()['x{}_{}'.format(i + 1, j + 1)] >= -a_list[i]
            prob += globals()['x{}_{}'.format(i + 1, j + 1)] <= a_list[i]
            prob += pulp.lpSum([globals()['x{}_{}'.format(i + 1, j + 1)] for i in range(10)]) <= 1.01 * b_list[j]
            prob += pulp.lpSum([globals()['x{}_{}'.format(i + 1, j + 1)] for i in range(10)]) >= 0.99 * b_list[j]

            prob += pulp.lpSum([globals()['y{}_{}'.format(i + 1, j + 1)] for i in range(10)]) <= 1.6 * a_list[i]
            prob += pulp.lpSum([globals()['y{}_{}'.format(i + 1, j + 1)] for i in range(10)]) >= 0.4 * a_list[i]
            if j == 0:
                prob += globals()['y{}_{}'.format(i + 1, j + 1)] == a_list[i]
            else:
                prob += globals()['y{}_{}'.format(i + 1, j + 1)] == globals()['y{}_{}'.format(i + 1, j)] - 0.25 * \
                        globals()['x{}_{}'.format(i + 1, j)]

    # 求解
    prob.solve()

    '''
    # 测试是否满足约束条件
    for i in range(10):
        for j in range(96):
            assert -a_list[i] <= globals()['x{}_{}'.format(i + 1, j + 1)].varValue <= a_list[i]
            assert pulp.value(pulp.lpSum([globals()['x{}_{}'.format(i + 1, j + 1)] for i in range(10)])) == b_list[j]
            assert -8 * a_list[i] <= pulp.value(
                pulp.lpSum([globals()['x{}_{}'.format(i + 1, j + 1)] for j in range(96)])) <= 8 * a_list[i]
    '''

    # 输出结果
    print("Status:", pulp.LpStatus[prob.status])
    for v in prob.variables():
        print(v.name, "=", v.varValue)

    print("目标函数值 = {}".format(pulp.value(prob.objective)))

    # 画图
    x = [i for i in range(0, 96)]
    y = [globals()['x{}_{}'.format(2, j + 1)].varValue for j in range(96)]
    plt.plot(x, y, label='x{}_{}'.format(2, j + 1))
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
