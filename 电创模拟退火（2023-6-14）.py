# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 11:01:47 2023

@author: 29190
"""

import csv
import pulp
import math
import random

# 模型数据初始化
# 基本设置
T = 15  # 仿真步长
UB = 230  # 线路电压等级
# 抽蓄数据
Pump_power_each = 300  # 每台机组最大出力:MW
Pump_power_max = 900  # 抽水蓄能最大出力:MW
Pump_volume_max = 1146.5 * 1e4  # 水库允许的最大体积:m3
Pump_peak_cost_each = 100  # 抽水蓄能单位调峰成本:元/MW
Pump_run_cost_each = 300  # 抽水蓄能运行成本:元/MW
Pump_switch_cost_each = 3000  # 启停机单位成本:元
Pump_efficiency = 0.75  # 抽/发效率
Pump_number = 1  # 抽水蓄能站数量
g = 9.8  # 重力加速度
Pump_height = 2000  # 水库高度
water_density = 1000  # 水密度

# 电池储能数据
# 电源出力上限：MW
Battery_power_max_list = [200, 142.5, 380, 210, 307, 410, 50, 200, 600, 200, 143, 10]
Battery_volume_max = 1800  # 定义蓄电池最大容量和最小容量MWh
Battery_build_cost_each: float = 102e4  # 单位年建设成本
Battery_run_cost_each = 2.94  # 单位运维成本
Battery_efficiency = 0.9  # 电池充放电效率
N0 = 1e3  # 固有放电次数
kp = 2.66  # 与电池固定参数
Battery_number = 12  # 电池储能站数量

# 氢能数据
H2_power_max = 100  # 氢能最大出力
H2_tank_volumn = 1000  # 氢储能罐体积
H2_fuelcell_run_cost = 1.89  # 燃料电池出力运维单位成本
H2_elecell_run_cost = 1.3  # 电解池出力运维单位成本
H2_fuelcell_efficiency = 0.55  # 燃料电池效率
H2_elecell_efficiency = 0.75  # 电解槽效率
H2_number = 2  # 氢能站数量
H2_pressure_max = 14700000  # 储罐最大压力
Fara = 96485.33289  # 法拉第常数
Uref = 150  # 氢燃料电池电堆电压
kH2 = 15  # 电解制氢系数
R = 8.314  # 理想气体常数
H2_T = 300  # 储罐开氏温度

# 读取潮流缺额数据
Flow_shortfall_csv = csv.reader(open("data/潮流缺额与剩余随时间变化数据.csv"))
Flow_shortfall_list = [row for row in Flow_shortfall_csv]

# 读取湖南电网数据
Hunan_csv = csv.reader("")


# 抽水蓄能模型
class PumpUnit:

    # 水站单元模型初始化方法
    def __init__(self, turnbin_number, volumn0):
        self.turnbin_number = turnbin_number  # 水站拥有的水轮机数目
        self.volumn = volumn0  # 初始水容量
        self.volumn0 = volumn0  # 同样为初始水容量，但不作修改，仅在约束条件中作比较时用
        self.turnbin_list = []  # 水轮机序列

    # 水轮机模型
    class turnbin:

        # 水轮机模型初始化方法
        def __init__(self, power0, switch0):
            self.power = power0  # 初始化水轮机装机容量
            self.switch = switch0  # 初始水轮机开关状态
            self.switch_list = [switch0, switch0]  # 存储前态和现态的开关状态表

        # 水轮机开关状态切换方法
        def change_switch(self, switch):
            self.switch_list[0] = self.switch  # 存储前态开关状态
            self.switch_list[1] = switch  # 存储现态开关状态
            self.switch = switch  # 更新开关状态为现态

    # 为水站添加水轮机的方法
    def init_turnbin(self, turnbin):
        self.turnbin_list.append(turnbin)

    # 水位访问方法
    def get_volumn(self):
        return self.volumn

    # 水位变化函数
    def volumn_change(self):
        for i in range(len(self.turnbin_list)):
            self.volumn += self.turnbin_list[i].switch * self.turnbin_list[i] \
                .power_change * T * Pump_efficiency / (water_density * g * Pump_height)
        return self.volumn

    # 单位成本函数
    def get_each_cost(self):
        each_run_cost = 0
        each_switch_cost = 0
        # 对每个水轮机循环相加，得到总的水站单位成本
        for i in range(len(self.turnbin_list)):
            # 单位水轮机运行成本
            each_run_cost += -self.turnbin_list[i].switch * \
                             self.turnbin_list[i].power_change * Pump_run_cost_each
            # 单位水轮机开关切换成本
            each_switch_cost += abs(self.turnbin_list[i].switch_list[1] -
                                    self.turnbin_list[i].switch_list[0]) * Pump_switch_cost_each
        # 总成本
        self.each_cost = each_run_cost + each_switch_cost
        self.constraint()
        return self.each_cost

    # 约束条件罚函数
    def constraint(self):
        if self.volumn > Pump_volume_max or self.volumn < 0:
            self.each_cost = float("inf")


# 电化学模型
class Battery_unit:

    # 电化学单元模型初始化方法
    def __init__(self, power0, volumn0, power_max):
        self.power = power0  # 电池充放电功率
        self.volumn = volumn0  # 初始功率电量
        self.volumn0 = volumn0
        self.power_max = power_max  # 电池最大出力
        self.charge_discharge_change = 0  # 充放电切换次数

    # 充放电功率变化方法
    def power_change(self, power):
        if self.power * power < 0:
            self.charge_discharge_change += 1
        self.power = power

    # 容量访问方法
    def get_volumn(self):
        return self.volumn

    # 电池容量变化函数
    def volumn_change(self):
        self.volumn -= self.power * T * Battery_efficiency / 60

    # 电池等效放电次数
    def get_equal_discharge_frequency(self):
        self.equal_discharge_frequency = 3e-4 - 0.009 * (self.volumn / 60 / \
                                                         Battery_volumn_max - (1 - 1 / 3000) ** (
                                                                 1 / kp) * Battery_volumn_max / 60 / T)
        return self.equal_discharge_frequency

    # 单位成本函数
    def get_each_cost(self):
        each_bulid_cost = self.get_equal_discharge_frequency() * \
                          Battery_build_cost_each * Battery_volumn_max / 365 / N0
        each_run_cost = Battery_run_cost_each * self.power
        self.each_cost = each_bulid_cost + each_run_cost
        self.constraint()
        return self.each_cost

    # 约束条件罚函数
    def constraint(self):
        if abs(self.power) > self.power_max \
                or self.volumn < Battery_volumn_max * 0.2 \
                or self.volumn > Battery_volumn_max * 0.8 \
                or self.charge_discharge_change > 1:
            self.each_cost = float("inf")


# 氢储能模型
class H2_unit():

    # 氢储能模型初始化方法
    def __init__(self, power0, amount0):
        self.power = power0  # 燃料电池放电功率/电解池充电功率
        self.amount = amount0  # 氢储罐存储氢气的物质的量
        self.amount0 = amount0
        self.pressure = self.amount * R * H2_T / H2_tank_volumn  # 氢储罐压力

    # 出力功率变化方法
    def power_change(self, power):
        self.power = power

    # 储罐氢气物质的量访问方法
    def get_ammount(self):
        return self.amount

    # 储罐氢气物质的量变化函数
    def ammount_change(self):
        if self.power >= 0:
            self.amount -= self.power * T * 60 / 2 / Fara / H2_fuelcell_efficiency / Uref * 1e3
        else:
            self.amount -= self.power * kH2 * H2_elecell_efficiency * 60 / T * 1e-3

    # 储罐压力变化函数
    def pressure_change(self):
        self.pressure = self.amount * R * H2_T / H2_tank_volumn

    # 单位成本函数
    def get_each_cost(self):
        if self.power >= 0:
            self.each_cost = self.power * H2_fuelcell_run_cost
        else:
            self.each_cost = -self.power * H2_elecell_run_cost
        self.constraint()
        return self.each_cost

    # 约束条件罚函数
    def constraint(self):
        if self.pressure > H2_pressure_max \
                or self.volumn < 0 \
                or abs(self.power) > H2_power_max:
            self.each_cost = float("inf")


# 目标函数
# 输入的是每个时刻的抽蓄水轮机开关状态表、每个电池的出力状态表和每个氢储能站的出力状态表
def min_cost(pump_solution, battery_solution, H2_solution,
             Turnbin_list, Pump_unit_list, Battery_unit_list, H2_unit_list):
    # 初始化各储能方式总成本
    pump_cost = 0
    battery_cost = 0
    H2_cost = 0

    # 抽蓄总成本计算
    for i in range(int(24 * 60 / T)):
        # 特别地，抽蓄需要更新每个水轮机的开关状态，这里两次change
        # 是用来建立前态和现态的开关状态序列
        for j in range(len(Turnbin_list)):
            Turnbin_list[j].change_switch(pump_solution[i - 1][j])
            Turnbin_list[j].change_switch(pump_solution[i][j])

        for j in range(Pump_number):
            # 更新当前解下的水位
            Pump_unit_list[j].volumn_change()
            # 抽蓄总成本计算
            pump_cost += Pump_unit_list[j].get_each_cost()

        for j in range(Battery_number):
            # 更新当前解下的电池容量
            Battery_unit_list[j].volumn_change()
            # 电化学总成本计算
            battery_cost += Battery_unit_list[j].get_each_cost()

        for j in range(H2_number):
            # 更新当前解下储罐氢气的物质的量
            H2_unit_list[j].ammount_change()
            # 氢储能总成本计算
            H2_cost += H2_unit_list[j].get_each_cost()

    total_cost = pump_cost + battery_cost + H2_cost

    # 负载功率平衡约束条件
    for i in range(int(24 * 60 / T)):

        pump_power = 0
        for j in range(len(Turnbin_list)):
            pump_power += pump_solution[i][j] * Turnbin_list[j].power_change
        battery_power = sum(battery_solution[i])
        H2_power = sum(H2_solution[i])

        if pump_power + battery_power + H2_power < float(Flow_shortfall_list[0][i]) - 1000 \
                or pump_power + battery_power + H2_power > float(Flow_shortfall_list[0][i]) + 1000:
            total_cost = float("inf")

    return total_cost


def linear_planning(Turnbin_list, Pump_unit_list, Battery_unit_list, H2_unit_list):
    # 创建pulp问题对象
    min_cost_problem = pulp.LpProblem("min_cost", sense=pulp.LpMinimize)

    # 创建pulp决策变量对象矩阵
    for i in range(int(24 * 60 / T)):

        for j in range(len(Turnbin_list)):
            # 创建水轮机开关变量
            exec("turnbin_switch_{0}_{1} = pulp.LpVariable('turnbin_switch_{0}_{1}',\
                 lowBound=-1, upBound=1, cat='Integer')".format(i, j))
            # 创建水轮机开关切换中间变量，在后面加约束以线性化绝对值
            exec("turnbin_switch_change_{0}_{1} = pulp.LpVariable(              \
                'turnbin_switch_change_{0}_{1}', lowBound=0, upBound=2,         \
                cat='Integer')".format(i, j))

        for j in range(Battery_number):
            # 创建电池出力变量
            exec("battery_power_{0}_{1} = pulp.LpVariable('battery_power_{0}_{1}',\
                 lowBound=-{2}, upBound={2}, cat='Continuous')" \
                 .format(i, j, Battery_power_max_list[j]))

        for j in range(H2_number):
            # 创建氢储能出力变量，包括w1、w2、z1、z2用以线性化分段函数，power = 
            # -H2_power_max * w1 + H2_power_max * w2，z1、z2用于限定w1、w2
            exec("H2_power_w1_{0}_{1} = pulp.LpVariable('H2_power_w1_{0}_{1}',  \
                 lowBound=0, upBound=1, cat='Continuous')" \
                 .format(i, j))
            exec("H2_power_w2_{0}_{1} = pulp.LpVariable('H2_power_w2_{0}_{1}',  \
                 lowBound=0, upBound=1, cat='Continuous')" \
                 .format(i, j))
            exec("H2_power_z1_{0}_{1} = pulp.LpVariable('H2_power_w1_{0}_{1}',  \
                 lowBound=0, upBound=1, cat='Binary')" \
                 .format(i, j))
            exec("H2_power_z2_{0}_{1} = pulp.LpVariable('H2_power_w2_{0}_{1}',  \
                 lowBound=0, upBound=1, cat='Binary')" \
                 .format(i, j))

    # 创建pulp目标函数对象
    min_cost_string = "min_cost_problem +="
    for i in range(int(24 * 60 / T)):

        # 创建抽蓄目标函数
        for j in range(len(Turnbin_list)):
            min_cost_string += "+ turnbin_switch_{0}_{1} * {2} + turnbin_switch_change_{0}_{1}\
            * {3} ".format(i, j, Pump_run_cost_each, Pump_switch_cost_each)

        # 创建电化学目标函数
        for j in range(Battery_number):
            # 创建消耗容量表达式
            run_volumn_string = ""
            for k in range(i):
                run_volumn_string += "+ battery_power_{0}_{1} ".format(k, j)
            run_volumn_string = run_volumn_string[1:]

            min_cost_string += "+ battery_power_{0}_{1} * {2} + 3e-4 - 0.009 *  \
            (({3}-({4})*{5}*{6}/60)/60/{7} - (1-1/3000)**(1/{8}) * {7}/60/{5}) " \
                .format(i, j, Battery_run_cost_each, Battery_unit_list[j].get_volumn(),
                        run_volumn_string, T, Battery_efficiency, Battery_volumn_max, kp)

        # 创建氢储能目标函数
        for j in range(H2_number):
            min_cost_string += "+ H2_power_w1_{0}_{1} * {2} * {3} +             \
            H2_power_w2_{0}_{1} * {4} * {3}" \
                .format(i, j, H2_elecell_run_cost, H2_power_max, H2_fuelcell_run_cost)

    min_cost_string = min_cost_string[:19] + min_cost_string[21:]
    print(min_cost_string)
    exec(min_cost_string)

    # 添加约束
    for i in range(int(24 * 60 / T)):

        # 抽蓄约束
        for j in range(len(Turnbin_list)):
            # 水轮机开关切换中间变量约束
            min_cost_string = "(min_cost_problem +="
            min_cost_string += "turnbin_switch_change_{0}_{1} >= turnbin_switch_{0}_{1})" \
                .format(i, j)
            exec(min_cost_string)

            min_cost_string = "(min_cost_problem +="
            min_cost_string += "turnbin_switch_change_{0}_{1} >= -turnbin_switch_{0}_{1})" \
                .format(i, j)
            exec(min_cost_string)

        for j in range(Pump_number):

            # 累进功率表达式，即当前时刻水站单位水轮机的累积功率
            pump_power_string = ""
            for k in range(Pump_unit_list[j].turnbin_number):
                # 累进每一水轮机的功率
                for m in range(i):
                    pump_power_string += "+ turnbin_switch_{0}_{1} * {2} ".format(m, j,
                                                                                  Pump_unit_list[j].turnbin_list[
                                                                                      k].power_change)
            pump_power_string = pump_power_string[1:]

            # 水位约束
            min_cost_string = "(min_cost_problem +="
            min_cost_string += "{0} + ({1}) * {2} * {3} / ({4} * {5} * {6}) <= {7})" \
                .format(Pump_unit_list[j].volumn0, pump_power_string, T, Pump_efficiency,
                        water_density, g, Pump_height, Pump_volume_max)
            exec(min_cost_string)

            min_cost_string = "(min_cost_problem +="
            min_cost_string += "{0} + ({1}) * {2} * {3} / ({4} * {5} * {6}) >= 0)" \
                .format(Pump_unit_list[j].volumn0, pump_power_string, T, Pump_efficiency,
                        water_density, g, Pump_height)
            exec(min_cost_string)

        # 电化学约束
        for j in range(Battery_number):
            min_cost_string = "(min_cost_problem +="
            min_cost_string += "{0} - {1} * {2} * {3} / 60 <= {4})".format( \
                Battery_unit_list[j].volumn0, run_volumn_string, T, \
                Battery_efficiency, Battery_volumn_max)
            exec(min_cost_string)

            min_cost_string = "(min_cost_problem +="
            min_cost_string += "{0} - {1} * {2} * {3} / 60 >= 0)".format( \
                Battery_unit_list[j].volumn0, run_volumn_string, T, \
                Battery_efficiency)
            exec(min_cost_string)

        # 氢储能约束
        for j in range(H2_number):

            # w1、w2和z1、z2的基本约束
            min_cost_string = "(min_cost_problem +="
            min_cost_string += "H2_power_w1_{0}_{1} + H2_power_w2_{0}_{1} == 1)" \
                .format(i, j)
            exec(min_cost_string)

            min_cost_string = "(min_cost_problem +="
            min_cost_string += "H2_power_z1_{0}_{1} + H2_power_z2_{0}_{1} == 1)" \
                .format(i, j)
            exec(min_cost_string)

            min_cost_string = "(min_cost_problem +="
            min_cost_string += "H2_power_w1_{0}_{1} <= H2_power_z1_{0}_{1})" \
                .format(i, j)
            exec(min_cost_string)

            min_cost_string = "(min_cost_problem +="
            min_cost_string += "H2_power_w2_{0}_{1} <= H2_power_z2_{0}_{1})" \
                .format(i, j)
            exec(min_cost_string)

            # 生成氢气物质的量表达式
            produced_amount_string = ""
            for k in range(i):
                produced_amount_args = [-H2_power_max * T * 60 / 2 / Fara / H2_fuelcell_efficiency / Uref * 1e3,
                                        H2_power_max * kH2 * H2_elecell_efficiency * 60 / T * 1e-3]
                produced_amount_string += "+ H2_power_w1_{0}_{1} * {2} + H2_power_w2_{0}_{1} * {3}" \
                    .format(i, j, produced_amount_args[0], produced_amount_args[1])
            produced_amount_args = produced_amount_args[1:]

            # 氢气的物质的量约束
            min_cost_string = "(min_cost_problem +="
            min_cost_string += "{0} + {1} >= 0)".format(H2_unit_list[j].amount0,
                                                        produced_amount_string)
            exec(min_cost_string)

            # 储罐压强约束
            min_cost_string = "(min_cost_problem +="
            pressure_args = R * H2_T / H2_tank_volumn
            min_cost_string += "({0} + {1}) * {2} <= {3})".format(H2_unit_list[j].amount0, \
                                                                  produced_amount_string, pressure_args,
                                                                  H2_pressure_max)
            exec(min_cost_string)

    min_cost_problem.solve()


# 模拟退火算法
def simulated_annealing(min_cost, initial_temperature, cooling_rate, iteration_limit,
                        min_temperature, pump_current_solution,
                        battery_current_solution, H2_current_solution,
                        turnbin_list, Pump_unit_list, Battery_unit_list, H2_unit_list):
    # 把线性规划数据丢进去/叠加噪声丢进去进行迭代

    # 初始化温度和已迭代次数
    temperature = initial_temperature
    iteration = 0
    pump_neighbor_solution = []
    battery_neighbor_solution = []
    H2_neighbor_solution = []

    while temperature > min_temperature and iteration < iteration_limit:

        # 生成邻域解
        for i in range(int(24 * 60 / T)):

            # 水轮机开关状态的邻域解在-1、0、1之间随机变化
            pump_neighbor_solution.append([random.randint(-1, 1)
                                           for j in pump_current_solution[i]])

            # 电池出力的邻域解在原解基础上以0.1倍的最大出力作为变化范围进行变化
            for j in range(Battery_number):
                battery_neighbor_solution.append([battery_current_solution[i][j] +
                                                  random.uniform(-0.1 * Battery_power_max_list[j],
                                                                 0.1 * Battery_power_max_list[j])])

            # 氢储能出力的邻域解在原解基础上以0.1倍的最大出力作为变化范围进行变化
            H2_neighbor_solution.append(j + random.uniform(-10, 10)
                                        for j in H2_current_solution[i])

        # 计算目标函数值
        current_value = min_cost(pump_current_solution, battery_current_solution,
                                 H2_current_solution, turnbin_list, Pump_unit_list,
                                 Battery_unit_list, H2_unit_list)
        neighbor_value = min_cost(pump_neighbor_solution, battery_neighbor_solution,
                                  H2_neighbor_solution, turnbin_list, Pump_unit_list,
                                  Battery_unit_list, H2_unit_list)

        # 如果邻居解更好，接受邻居解并降温
        if neighbor_value < current_value:
            pump_current_solution = pump_neighbor_solution
            battery_current_solution = battery_neighbor_solution
            H2_current_solution = H2_neighbor_solution
            temperature *= cooling_rate

            # 否则以一定的概率接受当前解并降温
        else:
            acceptance_probability = math.exp((current_value - neighbor_value)
                                              / temperature)

            if random.random() < acceptance_probability:
                pump_current_solution = pump_neighbor_solution
                battery_current_solution = battery_neighbor_solution
                H2_current_solution = H2_neighbor_solution
                temperature *= cooling_rate

        iteration += 1

        print(current_value)
    return current_value


def main():
    # 抽水蓄能初始化
    Pump_unit_list = []  # 抽水蓄能单元列表
    Turnbin_list = []  # 水轮机列表
    Pump_volumn0_list = [0.8 * Pump_volume_max]  # 抽水蓄能初始库容
    # 按水站总数目开始循环建立水站单元对象
    for i in range(Pump_number):
        Pump_unit_list.append(Pump_unit(3, Pump_volumn0_list[i]))
        # 按各水站拥有的水轮机数目开始循环建立水轮机对象，并存入水轮机列表
        for j in range(Pump_unit_list[i].turnbin_number):
            Pump_unit_list[i].init_turnbin(Pump_unit.turnbin(300, 0))
            Turnbin_list.append(Pump_unit_list[i].turnbin_list[j])

    # 电化学储能初始化
    Battery_unit_list = []  # 电化学储能单元列表
    # 电池初始容量
    # Battery_volumn0_list = [75, 17.5, 182.5, 45, 62.5, 95, 157.5, 212.5, 215, 195, 10, 202.5]
    Battery_volumn0_list = [900, 900, 900, 900, 900, 900, 900, 900, 900, 900, 900, 900]
    # 按电池总数目开始循环建立电池单元对象
    for i in range(Battery_number):
        Battery_unit_list.append(Battery_unit(0, Battery_volumn0_list[i], 1800))

    # 氢储能初始化
    H2_unit_list = []  # 氢储能单元列表
    H2_volumn0_list = [800, 400]  # 氢储能罐初始状态（氢气物质的量）
    # 按氢能站数目开始循环建立氢能站单元对象
    for i in range(H2_number):
        H2_unit_list.append(H2_unit(0, H2_volumn0_list[i]))

    # 生成初始解
    pump_current_solution = []  # 抽蓄解矩阵，存储各水轮机的开关状态
    battery_current_solution = []  # 电化学解矩阵，存储各电池的出力功率
    H2_current_solution = []  # 氢能解矩阵，存储各氢能站的出力功率

    for i in range(int(24 * 60 / T)):  # 按总时刻开始循环建立每一时刻的状态行
        # 初始化抽蓄解矩阵，每一行为一个时刻，每一列为各水轮机的开关状态，通过依次分块标识
        # 水轮机属于哪个水站。如第0、1、2列标识水站0，第3、4列标识水站1
        pump_current_switch_each_tik = []
        # 按水轮机总数开始循环随机建立每一水轮机在每一时刻的开关状态
        for j in range(len(Turnbin_list)):
            pump_current_switch_each_tik.append(random.randint(-1, 1))
        pump_current_solution.append(pump_current_switch_each_tik)

        # 初始化电化学解矩阵，每一行为一个时刻，每一列为各电池的出力功率
        battery_current_power_each_tik = []
        # 按电池总数开始循环随机建立每一电池在每一时刻的出力状态
        for j in range(Battery_number):
            battery_current_power_each_tik.append(random.uniform
                                                  (-Battery_power_max_list[j], Battery_power_max_list[j]))
        battery_current_solution.append(battery_current_power_each_tik)

        # 初始化氢能解矩阵，每一行为一个时刻，每一列为各氢能站的出力功率
        H2_current_power_each_tik = []
        # 按氢能站总数开始循环随机建立每一氢能站在每一时刻的出力状态
        for j in range(H2_number):
            H2_current_power_each_tik.append(random.uniform(-H2_power_max,
                                                            H2_power_max))
        H2_current_solution.append(H2_current_power_each_tik)

        # 计算线性规划结果
    linear_result = linear_planning(Turnbin_list, Pump_unit_list, Battery_unit_list, H2_unit_list)

    # 计算模拟退火结果
    simulated_result = simulated_annealing(min_cost, 1000, 0.995, 100000, 1e-6,
                                           pump_current_solution, battery_current_solution,
                                           H2_current_solution, Turnbin_list, Pump_unit_list,
                                           Battery_unit_list, H2_unit_list)

    # 计算遗传算法结果
    heredity_result = heredity(min_cost, pump_current_solution, battery_current_solution,
                               H2_current_solution, Turnbin_list, Pump_unit_list,
                               Battery_unit_list, H2_unit_list)
    # 三者结果进行对比取优，并输出
    return compare(linear_result, simulated_result, heredity_result)

if __name__ == '__main__':
    main()

