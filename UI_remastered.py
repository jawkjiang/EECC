# -*- coding: utf-8 -*-

import sys
import csv
import os
import io
from functools import partial

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMessageBox, QFileDialog, QComboBox, QSlider, \
    QCheckBox, QGroupBox, QLineEdit, QTextEdit, QTableView, QHeaderView, QAbstractItemView, QTableWidgetItem, QMenu, \
    QAction, QFormLayout, QScrollArea, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QEvent, QSize

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import algorithm

# 获取exe根目录
base_path: str
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)

QApplication.addLibraryPath(base_path + "/plugins")

# 读取出力数据
file = csv.reader(open(base_path + "/data/sj.csv"))
power_list = [row for row in file]

province_list = ["湖南", "湖北", "河南", "河北", "山西", "天津", "北京", "山东", "江苏", "浙江", "上海", "安徽",
                 "江西", "福建"]


# 绘制进入页面
class EntryWindow(QWidget):

    # 界面初始化
    def __init__(self):
        super().__init__()

        # 设置界面标题
        self.setWindowTitle("储能优化程序ver0.2")
        # 设置页面图标
        self.setWindowIcon(QIcon(base_path + "/images/软件图标.png"))
        # 设置界面大小
        self.resize(1280, 720)
        # 设置背景图片
        self.background_image = QLabel(self)
        self.background_image.setPixmap(QPixmap(base_path + "/images/进入界面（2023-6-23）.png"))

        # 设置导入框
        self.import_combobox = QComboBox(self)
        self.import_combobox.move(20, 30)
        self.import_combobox.setFixedHeight(30)
        self.import_combobox.setFixedWidth(160)
        self.import_combobox.setStyleSheet("font:16px Microsoft YaHei; color:white; background-color:rgb(47, 52, "
                                           "73); border-radius: 3px")
        self.import_combobox.addItem("导入...")
        self.import_combobox.addItem("导入风光负荷数据")
        self.import_combobox.addItem("导入储能数据")
        self.import_combobox.currentIndexChanged.connect(self.open_file)

        # 设置算法复选框
        algorithm_list = ["线性规划", "模拟退火算法", "遗传算法"]
        for i in algorithm_list:
            exec(f"self.checkbox{algorithm_list.index(i)}_algorithm = QCheckBox(self)")
            exec(f"self.checkbox{algorithm_list.index(i)}_algorithm.setText(i)")
            # 确定复选框位置，在(200,  10 + 25 * index)处
            exec(f"self.checkbox{algorithm_list.index(i)}_algorithm.move(200, {10 + 25 * algorithm_list.index(i)})")
            exec(f"self.checkbox{algorithm_list.index(i)}_algorithm.setFixedHeight(24)")
            exec(f"self.checkbox{algorithm_list.index(i)}_algorithm.setFixedWidth(120)")
            exec(f"self.checkbox{algorithm_list.index(i)}_algorithm.setStyleSheet(\"font:14px Microsoft YaHei; "
                 f"color:white; background-color:rgb(47, 52, 73); border-radius: 3px\")")

        # 设置AI交互窗口按钮
        self.button_ai = QPushButton(self)
        self.button_ai.setText("AI交互")
        self.button_ai.move(340, 30)
        self.button_ai.setFixedHeight(30)
        self.button_ai.setFixedWidth(80)
        self.button_ai.setStyleSheet("color:white; background-color:rgb(47, 52, 73); border-radius: 3px")
        self.button_ai.clicked.connect(lambda: self.ai_window.show())

        # 设置电站信息按钮
        self.button_station = QPushButton(self)
        self.button_station.setText("电站信息")
        self.button_station.move(440, 30)
        self.button_station.setFixedHeight(30)
        self.button_station.setFixedWidth(80)
        self.button_station.setStyleSheet("color:white; background-color:rgb(47, 52, 73); border-radius: 3px")
        self.station_window0 = StationWindow("湖南")
        self.button_station.clicked.connect(lambda: self.station_window0.show())

        # 设置省份按钮
        for i in province_list:
            exec(f"self.button{province_list.index(i)}_province = QPushButton(self)")
            exec(f"self.button{province_list.index(i)}_province.setText(i)")
            # 确定按钮位置，在(20,  130 + 30 * index)处
            exec(f"self.button{province_list.index(i)}_province.move(20, {130 + 30 * province_list.index(i)})")
            exec(f"self.button{province_list.index(i)}_province.setFixedHeight(28)")
            exec(f"self.button{province_list.index(i)}_province.setFixedWidth(90)")
            exec(f"self.button{province_list.index(i)}_province.setStyleSheet(\"color:white; background-color:rgb(47, "
                 f"52, 73); border-radius: 3px\")")
            exec(f"self.button{province_list.index(i)}_province.clicked.connect(partial(self.calculate, "
                 f"{province_list.index(i)}))")

        # 设置时间轴
        self.time_slider = QSlider(Qt.Horizontal, self)
        self.time_slider.setFixedWidth(180)
        self.time_slider.setRange(0, 95)
        self.time_slider.setSingleStep(1)
        self.time_slider.setStyleSheet("QSlider::handle:horizontal{background-color:#3f4459; \
                                      width: 15px; margin: -7px -7px -7px -7px; border-radius: 3px;}")
        self.time_slider.move(140, 607)

        # 设置AI交互界面
        self.ai_window = AIWindow()

    def open_file(self):
        opening_file: str
        # 导入风光负荷数据
        if self.import_combobox.currentIndex() == 1:
            opening_file, _ = QFileDialog.getOpenFileName(self, "打开文件", "D://", "Microsoft excel files (*.xlsx)")
            return opening_file
        # 导入储能数据
        elif self.import_combobox.currentIndex() == 2:
            opening_file, _ = QFileDialog.getOpenFileName(self, "打开文件", "D://", "Microsoft excel files (*.xlsx)")
            return opening_file
        else:
            pass

    def calculate(self, num):
        try:
            # 弹出运算结果界面
            exec(f"self.result_window{int(num)}.show()")
            self.hide()
        # 如果运算结果界面不存在，则创建
        except AttributeError:
            # 弹出提示框
            msg_box = QMessageBox(QMessageBox.Information, '提示', '计算中……')
            msg_box.setStandardButtons(QMessageBox.Cancel)
            msg_button = msg_box.button(QMessageBox.Cancel)
            msg_button.animateClick(1000)
            msg_button.hide()
            msg_box.exec_()
            # 隐藏进入界面
            self.hide()
            exec(f"self.result_window{int(num)} = ResultWindow(self, {int(num)})")
            exec(f"self.result_window{int(num)}.show()")

    # 关闭窗口时弹出提示框
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', '是否要退出程序？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class StationWindow(QWidget):

    def __init__(self, province):
        super().__init__()
        self.province = province

        self.setWindowTitle("电站管理窗口")
        self.setFixedSize(800, 600)

        self.setWindowIcon(QIcon(base_path + "/images/软件图标.png"))

        self.label_province = QLabel(self)
        self.label_province.setText("当前省份：")
        self.label_province.move(20, 20)
        self.label_province.setFixedHeight(30)
        self.label_province.setFixedWidth(120)
        self.label_province.setStyleSheet("font:14px Microsoft YaHei; color:black;")

        self.combobox_province = QComboBox(self)
        self.combobox_province.move(100, 22)
        self.combobox_province.setFixedWidth(120)
        self.combobox_province.setStyleSheet("font:14px Microsoft YaHei; color:black;")
        self.combobox_province.addItems(province_list)
        self.combobox_province.setCurrentIndex(province_list.index(province))
        self.combobox_province.currentIndexChanged.connect(self.change_province)

        self.button_station_new = QPushButton(self)
        self.button_station_new.setText("新建电站(N)")
        self.button_station_new.move(300, 20)
        self.button_station_new.setFixedHeight(30)
        self.button_station_new.setFixedWidth(120)
        self.button_station_new.setStyleSheet("font:14px Microsoft YaHei; background-color: rgb(225, 225, 225); "
                                              "border: 1px solid rgb(173, 173, 173); border-radius: 3px")
        self.new_window0 = self.new_window(self)
        self.button_station_new.clicked.connect(lambda: self.new_window0.show())
        self.button_station_new.setShortcut("ctrl+N")

        self.button_station_save = QPushButton(self)
        self.button_station_save.setText("保存(S)")
        self.button_station_save.move(440, 20)
        self.button_station_save.setFixedHeight(30)
        self.button_station_save.setFixedWidth(120)
        self.button_station_save.setStyleSheet("font:14px Microsoft YaHei; background-color: rgb(225, 225, 225); "
                                               "border: 1px solid rgb(173, 173, 173); border-radius: 3px")
        self.button_station_save.clicked.connect(lambda: self.save(self))

        self.tableview = QTableView(self)
        self.tableview.move(20, 70)
        self.tableview.setFixedHeight(480)
        self.tableview.setFixedWidth(760)
        self.tableview.setStyleSheet("color:black; background-color:white; border-radius: 3px")
        self.tableview.horizontalHeader().setStyleSheet(
            "color:black; background-color:rgb(47, 52, 73); border-radius: 3px")
        self.tableview.verticalHeader().setStyleSheet(
            "color:black; background-color:rgb(47, 52, 73); border-radius: 3px")
        self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableview.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableview.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableview.setShowGrid(True)
        self.tableview.setAlternatingRowColors(True)
        self.tableview.setSortingEnabled(True)
        self.tableview.setMouseTracking(True)

        self.tableview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.context_menu = QMenu()
        self.tableview.customContextMenuRequested.connect(self.show_context_menu)

        # 初始化电站信息
        self.tableview_model = QStandardItemModel()
        self.tableview_model.setHorizontalHeaderLabels(["电站名称", "电站类型", "装机容量", "备注"])
        self.tableview_model.setRowCount(0)
        self.tableview_model.setColumnCount(4)
        try:
            with open(base_path + f"/data/{province}.csv", "r") as self.station_file:
                self.station_file_reader = csv.reader(self.station_file)
                station_list = [row for row in self.station_file_reader]
                for i in range(len(station_list)):
                    for j in range(4):
                        try:
                            self.tableview_model.setItem(i, j, QStandardItem(station_list[i][j]))
                        except IndexError:
                            pass
            self.station_file.close()
        except FileNotFoundError:
            pass

        self.tableview.setModel(self.tableview_model)

    def change_province(self, index):
        try:
            exec(f"self.station_window{index}.show()")
            self.hide()
        except AttributeError:
            self.hide()
            exec(f"self.station_window{index} = StationWindow(province_list[{index}])")
            exec(f"self.station_window{index}.show()")

    class new_window(QWidget):

        def __init__(self, station_window):
            super().__init__()

            self.setWindowTitle("新建电站")
            self.setFixedSize(400, 300)
            self.setWindowIcon(QIcon(base_path + "/images/软件图标.png"))

            self.label_station_name = QLabel(self)
            self.label_station_name.setText("电站名称：")
            self.label_station_name.move(20, 20)
            self.label_station_name.setFixedWidth(80)
            self.label_station_name.setFixedHeight(30)
            self.label_station_name.setStyleSheet("font:14px Microsoft YaHei;")

            self.input_station_name = QLineEdit(self)
            self.input_station_name.move(100, 20)
            self.input_station_name.setFixedWidth(280)
            self.input_station_name.setFixedHeight(30)
            self.input_station_name.setStyleSheet("font:14px Microsoft YaHei;")

            self.label_station_type = QLabel(self)
            self.label_station_type.setText("电站类型：")
            self.label_station_type.move(20, 70)
            self.label_station_type.setFixedWidth(80)
            self.label_station_type.setFixedHeight(30)
            self.label_station_type.setStyleSheet("font:14px Microsoft YaHei;")

            self.input_station_type = QComboBox(self)
            self.input_station_type.move(100, 70)
            self.input_station_type.setFixedWidth(280)
            self.input_station_type.setFixedHeight(30)
            self.input_station_type.setStyleSheet("font:14px Microsoft YaHei;")
            self.input_station_type.addItems(["电化学", "抽水蓄能", "氢储能"])

            self.label_station_capacity = QLabel(self)
            self.label_station_capacity.setText("装机容量：")
            self.label_station_capacity.move(20, 120)
            self.label_station_capacity.setFixedWidth(80)
            self.label_station_capacity.setFixedHeight(30)
            self.label_station_capacity.setStyleSheet("font:14px Microsoft YaHei;")

            self.input_station_capacity = QLineEdit(self)
            self.input_station_capacity.move(100, 120)
            self.input_station_capacity.setFixedWidth(280)
            self.input_station_capacity.setFixedHeight(30)
            self.input_station_capacity.setStyleSheet("font:14px Microsoft YaHei;")

            self.label_station_remark = QLabel(self)
            self.label_station_remark.setText("备注：")
            self.label_station_remark.move(20, 170)
            self.label_station_remark.setFixedWidth(80)
            self.label_station_remark.setFixedHeight(30)
            self.label_station_remark.setStyleSheet("font:14px Microsoft YaHei;")

            self.input_station_remark = QLineEdit(self)
            self.input_station_remark.move(100, 170)
            self.input_station_remark.setFixedWidth(280)
            self.input_station_remark.setFixedHeight(30)
            self.input_station_remark.setStyleSheet("font:14px Microsoft YaHei;")

            self.button_confirm = QPushButton("确定", self)
            self.button_confirm.move(100, 220)
            self.button_confirm.setFixedWidth(80)
            self.button_confirm.setFixedHeight(30)
            self.button_confirm.setStyleSheet("font:14px Microsoft YaHei;")

            self.button_cancel = QPushButton("取消", self)
            self.button_cancel.move(300, 220)
            self.button_cancel.setFixedWidth(80)
            self.button_cancel.setFixedHeight(30)
            self.button_cancel.setStyleSheet("font:14px Microsoft YaHei;")

            self.button_confirm.clicked.connect(lambda: self.confirm(station_window))
            self.button_cancel.clicked.connect(self.cancel)

        def confirm(self, station_window):
            station_window.tableview_model.appendRow([
                QStandardItem(self.input_station_name.text()),
                QStandardItem(self.input_station_type.currentText()),
                QStandardItem(self.input_station_capacity.text()),
                QStandardItem(self.input_station_remark.text())
            ])
            self.close()

        def cancel(self):
            self.close()

    def show_context_menu(self, pos):
        self.context_menu.clear()
        edit_action = QAction('编辑', self)
        delete_action = QAction('删除', self)
        self.context_menu.addAction(edit_action)
        self.context_menu.addAction(delete_action)
        action = self.context_menu.exec_(self.tableview.mapToGlobal(pos))

        if action == edit_action:
            row = self.tableview.currentIndex().row()
            edit_list = []
            for col in range(self.tableview.model().columnCount()):
                editor = QLineEdit(self.tableview)
                editor.setText(self.tableview.model().data(self.tableview.model().index(row, col)))
                editor.installEventFilter(self)
                self.tableview.setIndexWidget(self.tableview.model().index(row, col), editor)
                edit_list.append(editor)

        elif action == delete_action:
            self.tableview_model.removeRow(self.tableview.currentIndex().row())

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            row = self.tableview.currentIndex().row()
            for col in range(self.tableview.model().columnCount()):
                self.tableview_model.setData(self.tableview_model.index(row, col), self.edit_list[col].text())
                self.tableview.setIndexWidget(self.tableview.model().index(row, col), None)
            return True
        return super().eventFilter(obj, event)

    def save(self, station_window):
        with open(f"data/{station_window.province}.csv", "w") as station_file:
            station_file.truncate(0)
            writer = csv.writer(station_file, delimiter=',', lineterminator='\n')
            for row in range(self.tableview_model.rowCount()):
                writer.writerow([
                    self.tableview_model.data(self.tableview_model.index(row, 0)),
                    self.tableview_model.data(self.tableview_model.index(row, 1)),
                    self.tableview_model.data(self.tableview_model.index(row, 2)),
                    self.tableview_model.data(self.tableview_model.index(row, 3))
                ])


class AIWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI交互窗口")
        self.setFixedSize(800, 600)

        self.setWindowIcon(QIcon(base_path + "/images/软件图标.png"))

        self.input_text = QLineEdit(self)
        self.input_text.move(20, 20)
        self.input_text.setFixedWidth(760)
        self.input_text.setStyleSheet("font:16px Microsoft YaHei; color:black;")

        self.combobox_prompt = QComboBox(self)
        self.combobox_prompt.move(40, 63)
        self.combobox_prompt.setFixedWidth(150)
        self.combobox_prompt.setStyleSheet("font:16px Microsoft YaHei; color:black;")
        self.combobox_prompt.addItem("AI参数配置")
        self.combobox_prompt.addItem("ChatGPT聊天")

        self.combobox_model = QComboBox(self)
        self.combobox_model.move(440, 63)
        self.combobox_model.setFixedWidth(200)
        self.combobox_model.setStyleSheet("font:16px Microsoft YaHei; color:black;")
        self.combobox_model.addItem("gpt-3.5-turbo")
        self.combobox_model.addItem("gpt-3.5-turbo-16k")
        self.combobox_model.addItem("gpt-4")
        self.combobox_model.addItem("gpt-4-32k")
        self.combobox_model.addItem("text-davinci-003")
        self.combobox_model.addItem("text-embedding-ada-002")

        self.button_send = QPushButton("发送", self)
        self.button_send.move(660, 61)
        self.button_send.setFixedWidth(120)
        self.button_send.setStyleSheet("font:16px Microsoft YaHei; color:black;")
        self.button_send.setShortcut("ctrl+return")

        self.output_text = QTextEdit(self)
        self.output_text.move(20, 100)
        self.output_text.setFixedWidth(760)
        self.output_text.setFixedHeight(480)
        self.output_text.setStyleSheet("font:16px Microsoft YaHei;"
                                       "color:black;")
        self.output_text.setReadOnly(True)

        self.button_send.clicked.connect(lambda: self.AI_connect(self.combobox_model.currentText()))

    def AI_connect(self, model):
        import OpenAIConnection
        self.output_text.append("用户：\n" + self.input_text.text() + "\n--------------------------")
        self.output_text.append(
            "AI：\n" + OpenAIConnection.chat(self.input_text.text(), model) + "\n--------------------------")


class ResultWindow(QWidget):

    def __init__(self, entry_window: EntryWindow, num):
        super().__init__()

        self.setWindowTitle(str(province_list[num]))
        self.setFixedSize(1280, 720)

        self.setWindowIcon(QIcon(base_path + "/images/软件图标.png"))

        self.background_image = QLabel(self)
        self.background_image.setPixmap(QPixmap(base_path + f"/images/运行结果（{province_list[num]}）.png"))

        # 设置导出按钮
        self.button_export = QPushButton("导出", self)
        self.button_export.move(20, 30)
        self.button_export.setFixedHeight(30)
        self.button_export.setFixedWidth(90)
        self.button_export.setStyleSheet("color:white; background-color:rgb(47, 52, 73); border-radius: 3px")
        self.button_export.clicked.connect(self.save_file)

        self.button_ai = QPushButton(self)
        self.button_ai.setText("返回")
        self.button_ai.move(120, 30)
        self.button_ai.setFixedHeight(30)
        self.button_ai.setFixedWidth(90)
        self.button_ai.setStyleSheet("color:white; background-color:rgb(47, 52, 73); border-radius: 3px")
        self.button_ai.clicked.connect(lambda: entry_window.show())
        self.button_ai.clicked.connect(lambda: self.hide())

        # 设置省份按钮
        for i in province_list:
            exec(f"self.button{province_list.index(i)}_province = QPushButton(self)")
            exec(f"self.button{province_list.index(i)}_province.setText(i)")
            # 确定按钮位置，在(20,  130 + 30 * index)处
            exec(f"self.button{province_list.index(i)}_province.move(20, {130 + 30 * province_list.index(i)})")
            exec(f"self.button{province_list.index(i)}_province.setFixedHeight(28)")
            exec(f"self.button{province_list.index(i)}_province.setFixedWidth(90)")
            exec(f"self.button{province_list.index(i)}_province.setStyleSheet(\"color:white; background-color:rgb(47, "
                 f"52, 73); border-radius: 3px\")")
            exec(f"self.button{province_list.index(i)}_province.clicked.connect(partial(entry_window.calculate, "
                 f"{province_list.index(i)}))")
            exec(f"self.button{province_list.index(i)}_province.clicked.connect(self.hide)")

        # 设置时间轴
        self.time_slider = QSlider(Qt.Horizontal, self)
        self.time_slider.setFixedWidth(180)
        self.time_slider.setRange(0, 95)
        self.time_slider.setSingleStep(1)
        self.time_slider.setStyleSheet("QSlider::handle:horizontal{background-color:#3f4459; \
                                      width: 15px; margin: -7px -7px -7px -7px; border-radius: 3px;}")

        self.time_slider.move(140, 607)
        # 链接时间轴与时间对象label
        self.time_slider.valueChanged.connect(self.time_change)
        # 链接时间轴与储能对象出力label
        self.time_slider.valueChanged.connect(self.power_change)

        # 创建时间对象label
        self.time_label = QLabel(self)
        self.time_label.setText("--:--")
        self.time_label.setStyleSheet("font:24px Microsoft YaHe; font-weight:700; color:rgb(47, 52, 73)")
        self.time_label.setFixedWidth(120)
        self.time_label.move(330, 605)

        # 创建储能对象出力label
        self.power_label_list = []
        for i in range(15):
            self.power_label_list.append(QLabel(self))
            self.power_label_list[i].setText("------")
            self.power_label_list[i].setFixedWidth(200)
            self.power_label_list[i].setStyleSheet("font:18px Microsoft YaHe; font-weight:700; color:rgb(47, 52, 73)")
            self.power_label_list[i].move(330, 165 + 24 * i)

        # 大地图按钮示例
        self.button_6 = QPushButton("6", self)
        self.button_6.move(657, 328)
        self.button_6.setFixedSize(20, 20)
        self.button_6.setStyleSheet("font:16px Microsoft YaHei; font-weight:700; color:rgb(47, 52, "
                                    "73); background-color:rgb(0, 255, 255)")
        self.button_6.clicked.connect(self.image_show)

        self.button_8 = QPushButton("8", self)
        self.button_8.move(626, 557)
        self.button_8.setFixedSize(20, 20)
        self.button_8.setStyleSheet("font:16px Microsoft YaHei; font-weight:700; color:rgb(47, 52, "
                                    "73); background-color:rgb(0, 255, 255)")
        self.button_8.clicked.connect(self.image_show)

        self.form_window = QWidget(self)
        self.form_window.move(890, 80)
        self.form_window.resize(350, 600)
        self.form_window.setStyleSheet("background-color:rgb(195, 198, 197)")
        self.form_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.form = QFormLayout(self.form_window)
        self.form.setVerticalSpacing(10)

    # 设置导出文件函数
    def save_file(self):
        saving_file, _ = QFileDialog.getSaveFileName(self, "保存文件", "D://", "Microsoft excel files (*.xlsx)")
        return saving_file

    # 设置时间轴与时间对象label的链接函数
    def time_change(self, new_value):
        if new_value // 4 < 10:
            if new_value % 4 == 0:
                self.time_label.setText("0{0}:0{1}".format(new_value // 4, 15 * (new_value % 4)))
            else:
                self.time_label.setText("0{0}:{1}".format(new_value // 4, 15 * (new_value % 4)))
        else:
            if new_value % 4 == 0:
                self.time_label.setText("{0}:0{1}".format(new_value // 4, 15 * (new_value % 4)))
            else:
                self.time_label.setText("{0}:{1}".format(new_value // 4, 15 * (new_value % 4)))

    # 设置时间轴与储能对象出力label的链接函数
    def power_change(self, new_value):
        for i in range(15):
            self.power_label_list[i].setText(power_list[new_value][i])

    # 设置储能对象出力图的链接函数
    def image_show(self):
        for i in range(15):
            x = [j for j in range(96)]
            y = []
            for j in range(96):
                y.append(power_list[j][i])
            fig = plt.figure(figsize=(300 / 100, 400 / 100), dpi=100)
            ax = fig.add_subplot(111)
            ax.invert_yaxis()
            plt.plot(x, y)
            plt.tick_params(labelsize=6)
            plt.subplots_adjust(left=0.2, right=0.95, bottom=0.15, top=0.89)
            plt.title(f"{i+1}号储能对象出力图", font="Microsoft YaHei", fontsize=10)
            plt.xlabel("时间/15min", font="Microsoft YaHei", fontsize=8)
            plt.ylabel("出力/kW", font="Microsoft YaHei", fontsize=8, labelpad=-2)
            figure_canvas = FigureCanvas(fig)

            buffer = io.BytesIO()
            figure_canvas.print_png(buffer)
            buffer.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            plt.close(fig)

            label = QLabel()
            label.setPixmap(pixmap)
            self.form.addRow(label)

            exec(f"Button{i+1} = QPushButton()")
            exec(f"Button{i+1}.setFixedSize(20, 20)")
            exec(f"Button{i+1}.setIcon(QIcon('images/放大.jpg'))")
            exec(f"Button{i+1}.setIconSize(QSize(20, 20))")
            # 按下按钮后弹出新窗口
            exec(f"Button{i+1}.clicked.connect(partial(self.enlarge, {i+1}))")

            exec(f"self.form.addRow(Button{i+1})")

        scroll = QScrollArea(self)
        scroll.setWidget(self.form_window)
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.move(890, 80)
        scroll.resize(350, 600)
        scroll.setStyleSheet("background-color:rgb(195, 198, 197)")
        scroll.show()

    def enlarge(self, number):
        try:
            exec(f"self.enlarge_window{number}.show()")
        except AttributeError:
            exec(f"self.enlarge_window{number} = self.enlarge_window(number)")
            exec(f"self.enlarge_window{number}.show()")

    class enlarge_window(QWidget):

        def __init__(self, number):
            super().__init__()

            self.setWindowTitle(f"{number}号储能对象出力图")
            self.resize(800, 600)
            self.setStyleSheet("background-color:rgb(255, 255, 255)")

            x = [j for j in range(96)]
            y = []
            for j in range(96):
                y.append(power_list[j][number - 1])
            self.fig = plt.figure(figsize=(800 / 100, 600 / 100), dpi=100)
            ax = self.fig.add_subplot(111)
            ax.invert_yaxis()
            plt.plot(x, y)
            plt.tick_params(labelsize=10)
            plt.subplots_adjust(left=0.1, right=0.95, bottom=0.15, top=0.9)
            plt.title(f"{number}号储能对象出力图", font="Microsoft YaHei", fontsize=16)
            plt.xlabel("时间/15min", font="Microsoft YaHei", fontsize=14)
            plt.ylabel("出力/kW", font="Microsoft YaHei", fontsize=14, labelpad=-2)
            self.figure_canvas = FigureCanvas(self.fig)

            self.buffer = io.BytesIO()
            self.figure_canvas.print_png(self.buffer)
            self.buffer.seek(0)

            self.pixmap = QPixmap()
            self.pixmap.loadFromData(self.buffer.getvalue())
            plt.close(self.fig)

            self.label = QLabel(self)
            self.label.setPixmap(self.pixmap)
            self.label.move(0, 0)
            self.label.resize(800, 600)

            self.show()

    # 设置大地图按钮的链接函数
    def image1_change(self):
        self.image1_power.setPixmap(QPixmap(base_path + "/images/6号 (2)(1).jpg"))
        self.image2_power.hide()
        self.image3_power.hide()

    def image2_change(self):
        self.image1_power.setPixmap(QPixmap(base_path + "/images/8号 (2)(1).jpg"))
        self.image2_power.hide()
        self.image3_power.hide()

    # 弹出退出提示框
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', '是否要退出程序？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


# 主程序入口
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EntryWindow()
    window.show()
    sys.exit(app.exec_())
