# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 22:12:52 2023

@author: Jawk
"""

import sys
# import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton,\
        QMessageBox, QFileDialog, QComboBox, QSlider, QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
import csv

file = csv.reader(open("D:\sj.csv"))
power_list = [row for row in file]
class Window(QWidget):
    def __init__(self):
        super().__init__()


        # 设置背景图片
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap("D:\进入界面（2023-6-23）.png"))


        
        '''
        # 设置图表
        self.widget1 = QWidget(self)
        self.widget1.setFixedSize(150, 150)
        self.widget1.move(920, 160)
        self.widget1.setStyleSheet("background-color:rgb(191, 191, 191)")
        
        # 绘条形图
        def open_plot1():
            # 创建一个Matplotlib figure对象
            fig = Figure(figsize=(4, 4), dpi=80)
            fig.set_facecolor("#bfbfbf")
            plot = fig.add_subplot()
            x = ["wind", "chemical", "solar"]
            y = [2034, 2330, 1930]
            plot.bar(x, y)
            plot.tick_params(axis="x", labelsize=8, rotation=0)
            plot.tick_params(axis="y", labelsize=10, rotation=90)
            plot.set_ylim(1900, None)
            plot.patch.set_facecolor("#bfbfbf")
            
            for i in range(len(x)):
                plot.text(i, y[i], y[i], ha='center', va='bottom')
            plot.get_children()[0].set_color("#585e71")
            plot.get_children()[1].set_color("#585e71")
            plot.get_children()[2].set_color("#585e71")

            # 为Matplotlib figure创建一个canvas对象
            canvas = FigureCanvas(fig)
            canvas.setFixedSize(150, 150)
            return canvas
        
        open_plot1().setParent(self.widget1)
        
        # 设置图表
        self.widget2 = QWidget(self)
        self.widget2.setFixedSize(150, 150)
        self.widget2.move(1070, 160)
        self.widget2.setStyleSheet("background-color:rgb(191, 191, 191)")
        
        # 绘条形图
        def open_plot2():
            # 创建一个Matplotlib figure对象
            fig = Figure(figsize=(4, 4), dpi=80)
            fig.set_facecolor("#bfbfbf")
            plot = fig.add_subplot()
            x = ["wind", "chemical", "solar"]
            y = [2034, 2330, 1930]
            plot.bar(x, y)
            plot.tick_params(axis="x", labelsize=8, rotation=0)
            plot.tick_params(axis="y", labelsize=10, rotation=90)
            plot.set_ylim(1900, None)
            plot.patch.set_facecolor("#bfbfbf")
            
            for i in range(len(x)):
                plot.text(i, y[i], y[i], ha='center', va='bottom')
            plot.get_children()[0].set_color("#585e71")
            plot.get_children()[1].set_color("#585e71")
            plot.get_children()[2].set_color("#585e71")

            # 为Matplotlib figure创建一个canvas对象
            canvas = FigureCanvas(fig)
            canvas.setFixedSize(150, 150)
            return canvas
        
        open_plot2().setParent(self.widget2)
        '''
        
        
        self.combobox = QComboBox(self)
        self.combobox.move(20, 30)
        self.combobox.setStyleSheet("font:18px Microsoft YaHei; color:white; background-color:rgb(47, 52, 73)")
        self.combobox.setFixedWidth(160)
        self.combobox.addItem("导入...")        
        self.combobox.addItem("导入风光负荷数据")
        self.combobox.addItem("导入储能数据")
        self.combobox.currentIndexChanged.connect(self.importing)

        '''
        self.combobox = QComboBox(self)
        self.combobox.move(200, 30)
        self.combobox.setStyleSheet("font:18px Microsoft YaHei; color:white; background-color:rgb(47, 52, 73)")
        self.combobox.addItem("线性规划")
        self.combobox.addItem("模拟退火算法")
        self.combobox.addItem("遗传算法")
        '''

        self.checkbox1 = QCheckBox(self)
        self.checkbox1.setText("线性规划")
        self.checkbox1.setStyleSheet("font:14px Microsoft YaHei; color:white; background-color:rgb(47, 52, 73)")
        self.checkbox1.move(200, 10)

        self.checkbox2 = QCheckBox(self)
        self.checkbox2.setText("模拟退火算法")
        self.checkbox2.setStyleSheet("font:14px Microsoft YaHei; color:white; background-color:rgb(47, 52, 73)")
        self.checkbox2.move(200, 35)

        self.checkbox3 = QCheckBox(self)
        self.checkbox3.setText("遗传算法")
        self.checkbox3.setStyleSheet("font:14px Microsoft YaHei; color:white; background-color:rgb(47, 52, 73)")
        self.checkbox3.move(200, 60)
        
        self.button1 = QPushButton("湖南", self)
        self.button1.move(20, 130)
        self.button1.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button1.clicked.connect(self.open_window)
                
        self.button2 = QPushButton("湖北", self)
        self.button2.move(20, 160)
        self.button2.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button2.clicked.connect(self.open_window2)

        self.button3 = QPushButton("河南", self)
        self.button3.move(20, 190)
        self.button3.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button3.clicked.connect(self.open_window3)
        
        self.button4 = QPushButton("河北", self)
        self.button4.move(20, 220)
        self.button4.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button4.clicked.connect(self.open_window4)
        
        self.button5 = QPushButton("山西", self)
        self.button5.move(20, 250)
        self.button5.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button5.clicked.connect(self.open_window5)
        
        self.button6 = QPushButton("天津", self)
        self.button6.move(20, 280)
        self.button6.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button6.clicked.connect(self.open_window6)
        
        self.button7 = QPushButton("北京", self)
        self.button7.move(20, 310)
        self.button7.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button7.clicked.connect(self.open_window7)
        
        self.button8 = QPushButton("山东", self)
        self.button8.move(20, 340)
        self.button8.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button8.clicked.connect(self.open_window8)
        
        self.button9 = QPushButton("江苏", self)
        self.button9.move(20, 370)
        self.button9.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button9.clicked.connect(self.open_window9)
        
        self.button10 = QPushButton("浙江", self)
        self.button10.move(20, 400)
        self.button10.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button10.clicked.connect(self.open_window10)
        
        self.button11 = QPushButton("上海", self)
        self.button11.move(20, 430)
        self.button11.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button11.clicked.connect(self.open_window11)
        
        self.button12 = QPushButton("安徽", self)
        self.button12.move(20, 460)
        self.button12.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button12.clicked.connect(self.open_window12)
        
        self.button13 = QPushButton("江西", self)
        self.button13.move(20, 490)
        self.button13.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button13.clicked.connect(self.open_window13)
        
        self.button14 = QPushButton("福建", self)
        self.button14.move(20, 520)
        self.button14.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button14.clicked.connect(self.open_window14)
        
        # 成员变量初始化为 None
        self.window = None
        self.window1 = None
        self.window2 = None
        self.window3 = None
        self.window4 = None
        self.window5 = None
        self.window6 = None
        self.window7 = None
        self.window8 = None
        self.window9 = None
        self.window10 = None
        self.window11 = None
        self.window12 = None
        self.window13 = None
        self.window14 = None
        
        # 创建时间轴对象
        self.timeslider = QSlider(Qt.Horizontal, self)
        self.timeslider.setFixedWidth(180)
        self.timeslider.setRange(0, 95)
        self.timeslider.setSingleStep(1)
        self.timeslider.setStyleSheet("QSlider::handle:horizontal{background-color:#3f4459; \
                                      width: 15px; margin: -7px -7px -7px -7px;}")
        self.timeslider.move(140, 607)
    
    def importing(self):
        self.open_file()

    def open_window(self):
        
        msg_box = QMessageBox(QMessageBox.Information, '提示', '计算中……')
        msg_box.setStandardButtons(QMessageBox.Cancel)
        msg_button = msg_box.button(QMessageBox.Cancel)
        msg_button.animateClick(26400)
        msg_button.hide()
        msg_box.exec_()
        self.hide()

        self.window = QWidget()
        self.window.setFixedSize(1280, 720)
        self.window.setWindowTitle("湖南")
        background = QLabel(self.window)
        background.lower()
        background.setPixmap(QPixmap("D://运行结果（2023-6-26）.png"))

        self.power_image1 = QLabel(self.window)
        self.power_image1.raise_()
        self.power_image1.setPixmap(QPixmap("D://氢储能(2).jpg"))
        self.power_image1.move(890, 80)

        self.power_image2 = QLabel(self.window)
        self.power_image2.setPixmap(QPixmap("D://电化学(2).jpg"))
        self.power_image2.move(890, 280)

        self.power_image3 = QLabel(self.window)
        self.power_image3.setPixmap(QPixmap("D://抽水蓄能(2).jpg"))
        self.power_image3.move(890, 480)

        self.button = QPushButton("导出", self.window)
        self.button.move(20,30)
        self.button.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button.clicked.connect(self.save_file)
            
        self.button1 = QPushButton("常德", self.window)
        self.button1.move(20, 130)
        self.button1.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button1.clicked.connect(self.open_window1)
        
        self.button2 = QPushButton("郴州", self.window)
        self.button2.move(20, 160)
        self.button2.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button2.clicked.connect(self.open_window2)

        self.button3 = QPushButton("怀化", self.window)
        self.button3.move(20, 190)
        self.button3.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button3.clicked.connect(self.open_window3)
        
        self.button4 = QPushButton("衡阳", self.window)
        self.button4.move(20, 220)
        self.button4.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button4.clicked.connect(self.open_window4)
        
        self.button5 = QPushButton("娄底", self.window)
        self.button5.move(20, 250)
        self.button5.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button5.clicked.connect(self.open_window5)
        
        self.button6 = QPushButton("邵阳", self.window)
        self.button6.move(20, 280)
        self.button6.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button6.clicked.connect(self.open_window6)
        
        self.button7 = QPushButton("湘潭", self.window)
        self.button7.move(20, 310)
        self.button7.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button7.clicked.connect(self.open_window7)
        
        self.button8 = QPushButton("湘西", self.window)
        self.button8.move(20, 340)
        self.button8.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button8.clicked.connect(self.open_window8)
        
        self.button9 = QPushButton("永州", self.window)
        self.button9.move(20, 370)
        self.button9.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button9.clicked.connect(self.open_window9)
        
        self.button10 = QPushButton("岳阳", self.window)
        self.button10.move(20, 400)
        self.button10.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button10.clicked.connect(self.open_window10)
        
        self.button11 = QPushButton("长沙", self.window)
        self.button11.move(20, 430)
        self.button11.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button11.clicked.connect(self.open_window11)
        
        self.button12 = QPushButton("株洲", self.window)
        self.button12.move(20, 460)
        self.button12.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button12.clicked.connect(self.open_window12)
        
        self.button13 = QPushButton("益阳", self.window)
        self.button13.move(20, 490)
        self.button13.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button13.clicked.connect(self.open_window13)
        
        self.button14 = QPushButton("张家界", self.window)
        self.button14.move(20, 520)
        self.button14.setStyleSheet("color:white; background-color:rgb(47, 52, 73)")
        self.button14.clicked.connect(self.open_window14)

        self.button15 = QPushButton("6", self.window)
        self.button15.move(657, 328)
        self.button15.setFixedSize(20, 20)
        self.button15.setStyleSheet("font:16px Microsoft YaHei; font-weight:700; color:rgb(47, 52, 73); background-color:rgb(0, 255, 255)")
        self.button15.clicked.connect(self.change_image1)

        self.button16 = QPushButton("8", self.window)
        self.button16.move(626, 557)
        self.button16.setFixedSize(20, 20)
        self.button16.setStyleSheet("font:16px Microsoft YaHei; font-weight:700; color:rgb(47, 52, 73); background-color:rgb(0, 255, 255)")
        self.button16.clicked.connect(self.change_image2)
        
        # 创建时间轴对象
        self.timeslider1 = QSlider(Qt.Horizontal, self.window)
        self.timeslider1.setFixedWidth(180)
        self.timeslider1.setRange(0, 95)
        self.timeslider1.setSingleStep(1)
        self.timeslider1.setStyleSheet("QSlider::handle:horizontal{background-color:#3f4459; \
                                      width: 15px; margin: -7px -7px -7px -7px;}")
        self.timeslider1.move(140, 607)
        self.timeslider1.valueChanged.connect(self.timing)
        self.timeslider1.valueChanged.connect(self.power)
        
        # 创建时间对象label
        self.timelabel = QLabel(self.window)
        self.timelabel.setText("--:--")
        self.timelabel.setStyleSheet("font:24px Microsoft YaHe; font-weight:700; color:rgb(47, 52, 73)")
        self.timelabel.setFixedWidth(120)
        self.timelabel.move(330, 605)
        
        # 创建储能对象出力label
        self.power_label_list = []
        for i in range(15):
            self.power_label_list.append(QLabel(self.window))
            self.power_label_list[i].setText("------")
            self.power_label_list[i].setFixedWidth(200)
            self.power_label_list[i].setStyleSheet("font:18px Microsoft YaHe; font-weight:700; color:rgb(47, 52, 73)")
            self.power_label_list[i].move(330, 165+24*i)

        
        self.window.show()

    def change_image1(self):
        self.power_image1.setPixmap(QPixmap("D://6号 (2)(1).jpg"))
        self.power_image2.hide()
        self.power_image2.lower()
        self.power_image3.hide()
        self.power_image3.lower()

    def change_image2(self):
        self.power_image1.setPixmap(QPixmap("D://8号 (2)(1).jpg"))
        self.power_image2.hide()
        self.power_image2.lower()
        self.power_image3.hide()
        self.power_image3.lower()
    def timing(self, new_value):
        if new_value//4 < 10:
            if 15*(new_value%4) == 0:
                self.timelabel.setText("0{0}:0{1}".format(new_value//4, 15*(new_value%4)))
            else:
                self.timelabel.setText("0{0}:{1}".format(new_value//4, 15*(new_value%4)))
        else:
            if 15*(new_value%4) == 0:
                self.timelabel.setText("{0}:0{1}".format(new_value//4, 15*(new_value%4)))
            else:
                self.timelabel.setText("{0}:{1}".format(new_value//4, 15*(new_value%4)))
                
    def power(self, new_value):
        for i in range(15):
            self.power_label_list[i].setText(power_list[new_value][i])

    
    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "打开文件", "D://", "Microsoft excel files (*.xlsx)")
    def save_file(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "保存文件", "D://", "Microsoft excel files (*.xlsx)")

    # def change_image1(self):


    def open_window1(self):
        if not self.window1:  # 检查对象是否已经创建
            self.window1 = QWidget()
            self.window1.setFixedSize(1280, 720)
            self.window1.setWindowTitle("长沙")
            background = QLabel(self.window1)
            background.setPixmap(QPixmap("background1.png"))
        self.window1.show()

    def open_window2(self):
        if not self.window2:  # 检查对象是否已经创建
            self.window2 = QWidget()
            self.window2.setFixedSize(1280, 720)
            self.window2.setWindowTitle("株洲")
            background = QLabel(self.window2)
            background.setPixmap(QPixmap("background2.png"))
        self.window2.show()
        
    def open_window3(self):
        if not self.window3:  # 检查对象是否已经创建
            self.window3 = QWidget()
            self.window3.setFixedSize(1280, 720)
            self.window3.setWindowTitle("湘潭")
            background = QLabel(self.window3)
            background.setPixmap(QPixmap("background2.png"))
        self.window3.show()
        
    def open_window4(self):
        if not self.window4:  # 检查对象是否已经创建
            self.window4 = QWidget()
            self.window4.setFixedSize(1280, 720)
            self.window4.setWindowTitle("衡阳")
            background = QLabel(self.window4)
            background.setPixmap(QPixmap("background2.png"))
        self.window4.show()
        
    def open_window5(self):
        if not self.window5:  # 检查对象是否已经创建
            self.window5 = QWidget()
            self.window5.setFixedSize(1280, 720)
            self.window5.setWindowTitle("邵阳")
            background = QLabel(self.window5)
            background.setPixmap(QPixmap("background2.png"))
        self.window5.show()
        
    def open_window6(self):
        if not self.window6:  # 检查对象是否已经创建
            self.window6 = QWidget()
            self.window6.setFixedSize(1280, 720)
            self.window6.setWindowTitle("岳阳")
            background = QLabel(self.window6)
            background.setPixmap(QPixmap("background2.png"))
        self.window6.show()
        
    def open_window7(self):
        if not self.window7:  # 检查对象是否已经创建
            self.window7 = QWidget()
            self.window7.setFixedSize(1280, 720)
            self.window7.setWindowTitle("常德")
            background = QLabel(self.window7)
            background.setPixmap(QPixmap("background2.png"))
        self.window7.show()
        
    def open_window8(self):
        if not self.window8:  # 检查对象是否已经创建
            self.window8 = QWidget()
            self.window8.setFixedSize(1280, 720)
            self.window8.setWindowTitle("张家界")
            background = QLabel(self.window8)
            background.setPixmap(QPixmap("background2.png"))
        self.window8.show()
        
    def open_window9(self):
        if not self.window9:  # 检查对象是否已经创建
            self.window9 = QWidget()
            self.window9.setFixedSize(1280, 720)
            self.window9.setWindowTitle("益阳")
            background = QLabel(self.window9)
            background.setPixmap(QPixmap("background2.png"))
        self.window9.show()
        
    def open_window10(self):
        if not self.window10:  # 检查对象是否已经创建
            self.window10 = QWidget()
            self.window10.setFixedSize(1280, 720)
            self.window10.setWindowTitle("郴州")
            background = QLabel(self.window10)
            background.setPixmap(QPixmap("background2.png"))
        self.window10.show()
        
    def open_window11(self):
        if not self.window11:  # 检查对象是否已经创建
            self.window11 = QWidget()
            self.window11.setFixedSize(1280, 720)
            self.window11.setWindowTitle("永州")
            background = QLabel(self.window11)
            background.setPixmap(QPixmap("background2.png"))
        self.window11.show()
        
    def open_window12(self):
        if not self.window12:  # 检查对象是否已经创建
            self.window12 = QWidget()
            self.window12.setFixedSize(1280, 720)
            self.window12.setWindowTitle("怀化")
            background = QLabel(self.window12)
            background.setPixmap(QPixmap("background2.png"))
        self.window12.show()
        
    def open_window13(self):
        if not self.window13:  # 检查对象是否已经创建
            self.window13 = QWidget()
            self.window13.setFixedSize(1280, 720)
            self.window13.setWindowTitle("娄底")
            background = QLabel(self.window13)
            background.setPixmap(QPixmap("background2.png"))
        self.window13.show()
        
    def open_window14(self):
        if not self.window14:  # 检查对象是否已经创建
            self.window14 = QWidget()
            self.window14.setFixedSize(1280, 720)
            self.window14.setWindowTitle("湘西")
            background = QLabel(self.window14)
            background.setPixmap(QPixmap("background2.png"))
        self.window14.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.setFixedSize(1280, 720)
    window.setWindowTitle("储能优化程序设计 ver0.1")
    window.show()
    sys.exit(app.exec_())
