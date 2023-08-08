import gurobipy as gp
import csv

a_list = [200, 142.5, 380, 210, 307, 410, 50, 200, 600, 200, 143, 10]
with open('data/潮流缺额与剩余随时间变化数据.csv', 'r') as f:
    reader = csv.reader(f)
    b_list = list(reader)
    b_list = b_list[0]
    b_list = [float(i) for i in b_list]

def main():

    # 创建模型
    model = gp.Model("test2")

    # 创建变量
    for i in range(10):
        for j in range(96):
            globals()['x{}_{}'.format(i + 1, j + 1)] = model.addVar(lb=-a_list[i], ub=a_list[i], vtype=gp.GRB.INTEGER,
                                                                    name="x{}_{}".format(i + 1, j + 1))
            globals()['y{}_{}'.format(i + 1, j + 1)] = model.addVar(lb=0.4 * a_list[i], ub=1.6 * a_list[i],
                                                                    vtype=gp.GRB.INTEGER,
                                                                    name="y{}_{}".format(i + 1, j + 1))

    # 创建目标函数
    model.setObjective(gp.quicksum(eval(f"x{i+1}_{j+1}") for i in range(10) for j in range(96)), gp.GRB.MINIMIZE)

    # 创建约束条件
    for i in range(10):
        for j in range(96):
            model.addConstr(eval(f"x{i+1}_{j+1}") >= -a_list[i])
            model.addConstr(eval(f"x{i+1}_{j+1}") <= a_list[i])
            model.addConstr(gp.quicksum(eval(f"x{i+1}_{j+1}") for i in range(10)) <= 1.01 * b_list[j])
            model.addConstr(gp.quicksum(eval(f"x{i+1}_{j+1}") for i in range(10)) >= 0.99 * b_list[j])

            model.addConstr(gp.quicksum(eval(f"y{i+1}_{j+1}") for i in range(10)) <= 1.6 * a_list[i])
            model.addConstr(gp.quicksum(eval(f"y{i+1}_{j+1}") for i in range(10)) >= 0.4 * a_list[i])
            if j == 0:
                model.addConstr(eval(f"y{i+1}_{j+1}") == a_list[i])
            else:
                model.addConstr(eval(f"y{i+1}_{j+1}") == eval(f"y{i+1}_{j}") - 0.25 * eval(f"x{i+1}_{j+1}"))

    # 求解
    model.optimize()

    # 输出结果
    print("目标函数值为：", model.objVal)
    print("最优解为：")
    for i in range(10):
        for j in range(96):
            print("x{}{} = {}".format(i + 1, j + 1, eval(f"x{i+1}_{j+1}").x))
            print("y{}{} = {}".format(i + 1, j + 1, eval(f"y{i+1}_{j+1}").x))


if __name__ == '__main__':
    main()