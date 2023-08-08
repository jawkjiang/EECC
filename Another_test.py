import cvxpy as cp
import csv
import sympy as sp
import gurobipy as gp

a_list = [200, 142.5, 380, 210, 307, 410, 50, 200, 600, 200, 143, 10]
with open('data/潮流缺额与剩余随时间变化数据.csv', 'r') as f:
    reader = csv.reader(f)
    b_list = list(reader)
    b_list = b_list[0]
    b_list = [float(i) for i in b_list]
print(b_list)


def main():
    # x是一个10*96的矩阵，每一行代表一个电站的出力，每一列代表一个时刻的出力
    x = cp.Variable((10, 96), integer=True)
    # y是一个10*96的矩阵，每一行代表一个电站的电量，每一列代表一个时刻的电量
    y = cp.Variable((10, 96), integer=True)
    # z是一个10*96的矩阵，每一行代表一个电站的等效放电次数，每一列代表一个时刻的等效放电次数
    z = cp.Variable((10, 96), integer=True)
    constraints = []

    for i in range(10):
        for j in range(96):
            # 约束条件
            # 电站出力的约束
            constraints.append(x[i, j] >= -a_list[i])
            constraints.append(x[i, j] <= a_list[i])
            constraints.append(cp.sum(x[:, j]) == b_list[j])

            # 电站电量的约束
            # 电量和出力的关系
            if j == 0:
                constraints.append(y[i, j] == a_list[i])
            else:
                constraints.append(y[i, j] == y[i, j - 1] - 0.25 * x[i, j - 1])
            # 电量自身的约束
            constraints.append(y[i, j] >= 0.4 * a_list[i])
            constraints.append(y[i, j] <= 1.6 * a_list[i])

            # 电池等效放电次数的约束
            # 电池等效放电次数和出力的关系
            constraints.append(z[i, j] == (3e-4 - 0.009 * (y[i, j] / 60 / a_list[i] - (1 - 1 / 3000) ** (1 / 2.66)
                                                           * a_list[i] / 60 / 15)) * a_list[i])

    obj = cp.Minimize(2.94 * cp.sum(x) + 0.1 * cp.sum(z))

    prob = cp.Problem(obj, constraints)
    prob.solve()
    print("Status:", prob.status)
    print("目标函数值 = {}".format(prob.value))
    print("最优解为：")
    print(x.value)


if __name__ == '__main__':
    main()
