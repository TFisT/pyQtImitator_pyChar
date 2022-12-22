import sys
#import math
#import pandas as pd # библиотека для csv
from time import sleep
import json
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QGridLayout, QWidget, qApp, QAction, QTableWidget,
                             QTableWidgetItem, QPushButton, QScrollArea, QVBoxLayout, QHBoxLayout, QStackedLayout,
                             QStatusBar, QFileDialog, QAbstractItemView, QTableView, QStyleOptionButton, QStyle,
                             QItemDelegate, )
from PyQt5.QtCore import QSize, Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QFont, QIcon, QImage, QKeyEvent, QPixmap, QColor, QBrush, QPainter
#from random import randint
#from PyQt5 import uic
from sh import cl_sh
from di import cl_di
from zd import cl_zd
from algoritms import cl_Algoritm, clTmOneSec
from modbus_client_master import cl_modbus
from model_tableview import Model, MyDelegate, CustomTableView
from model_tableTm import ModelTm

#MW = [0 for _ in range(65536)]  #Область памяти Modbus для одного сервера Modbus
rdMW = [0 for _ in range(127)]  #Область памяти для чтения Modbus для одного сервера Modbus
wrMW = [i for i in range(127)]  #Область памяти для записи Modbus для одного сервера Modbus

# Наследуемся от QMainWindow
class Window(QMainWindow):
    # Переопределяем конструктор класса
    def __init__(self):
        super().__init__()
        #self.ui = uic.loadUi('main.ui', self)
        #self.ui.show()

        # Обязательно нужно вызвать метод супер класса
        QMainWindow.__init__(self)
        self.setAcceptDrops(True)

        self.spin = []
        self.Num = -1
        self.Cnt_columns = 4 #количество столбцов в ScrollArea
        self.tmOneSec = 0

        self.setMinimumSize(QSize(1000, 468))  # Устанавливаем размеры
        self.setWindowTitle("Имитатор основное окно")  # Устанавливаем заголовок окна
        #self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint) # делаем окно onTop
        h_layout = QHBoxLayout()
        self.v1_layout = QGridLayout()
        self.v2_layout = QVBoxLayout()
        self.v1gr_layout = QGridLayout()
        self.v1_layout.addLayout(self.v1gr_layout,0,0)
        self.stacklayout = QStackedLayout()
        h_layout.addLayout(self.v1_layout)
        h_layout.addLayout(self.v2_layout)
        #h_layout.addLayout(self.stacklayout)
        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)  # Устанавливаем центральный виджет
        self.central_widget.setLayout(h_layout)  # Устанавливаем данное размещение в центральный виджет


        self.table = CustomTableView(self)
        #self.table.setStyleSheet('selection-background-color:white;') # избавиться от выделения
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSelectionMode(QAbstractItemView.NoSelection) #QTableWidget.SingleSelection
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(10)
        self.model = Model(self.spin, self.Num)
        self.table.setModel(self.model)
        #self.table.setItemDelegateForColumn(0, Btn_Delegate())
        self.table.setItemDelegate(MyDelegate())
        #self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, 84)
        self.table.setColumnWidth(1, 25)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 25)
        self.table.setColumnWidth(4, 25)
        self.table.setColumnWidth(5, 64)

        self.tableTm = QTableView(self)
        self.tableTm.setFocusPolicy(Qt.NoFocus)
        self.tableTm.setSelectionMode(QAbstractItemView.NoSelection) #QTableWidget.SingleSelection
        self.tableTm.setAlternatingRowColors(True)
        self.tableTm.verticalHeader().setDefaultSectionSize(10)
        self.modelTm = ModelTm(self, self.spin, self.Num)
        self.tableTm.setModel(self.modelTm)
        self.tableTm.setColumnWidth(0, 205)
        self.tableTm.setColumnWidth(1, 100)
        self.tableTm.setColumnWidth(2, 110)
        #self.tableTm.verticalHeader().setDefaultAlignment(Qt.AlignRight)



        self.scroll_area = QScrollArea()
        self.scroll_area.setGeometry(QtCore.QRect(0, 0, 500, 500))
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scrollAreaComponents = QWidget()
        self.grbox = QGridLayout()
        #Установить привязку к верху
        self.grbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.grbox.setContentsMargins(0,0,0,0)
        self.grbox.setSpacing(2)
        #Установить размер в 4 столбца
        # self.grbox.setColumnStretch(0, 1)
        # self.grbox.setColumnStretch(1, 1)
        # self.grbox.setColumnStretch(2, 1)
        # self.grbox.setColumnStretch(3, 1)
        for i in range(self.Cnt_columns):
            self.grbox.setColumnStretch(i, 1)
        self.scrollAreaComponents.setLayout(self.grbox)
        self.scroll_area.setWidget(self.scrollAreaComponents)

        # Размещение элементов
        self.v1_layout.addWidget(self.table, 1, 0)  # Adding the table to the grid
        self.v1_layout.addWidget(self.tableTm, 2, 0)  # Adding the table to the grid
        self.v2_layout.addWidget(self.scroll_area)

        # MENU
        self.up_action = QAction("&Поверх остальных окон", self)
        self.up_action.setCheckable(True)   #добавляет галочку выбора меню
        self.up_action.triggered.connect(self.mw_onTop)
        self.new_action = QAction("&Новый элемент", self)
        self.new_action.triggered.connect(self.add_new_Widget)
        save_action = QAction("&Сохранить конфигурацию в файл", self)
        save_action.triggered.connect(self.file_save)
        download_action = QAction("&Загрузить конфигурацию из файла", self)
        download_action.triggered.connect(self.file_load)
        self.del_action = QAction("&Удалить", self)
        self.del_action.triggered.connect(self.del_item)
        self.del_action.setEnabled(False)
        delconf_action = QAction("&Удалить конфигурацию", self)
        delconf_action.triggered.connect(self.del_all)
        setup_action = QAction("&Настройки", self)
        about_action = QAction("&О программе ...", self)
        exit_action = QAction("&Exit", self)  # Создаём Action с помощью которого будем выходить из приложения
        exit_action.setShortcut('Ctrl+Q')  # Задаём для него хоткей
        exit_action.triggered.connect(qApp.quit)    # Подключаем сигнал triggered к слоту quit у qApp.
        self.run_alg_action = QAction("&Запустить имитатор", self)
        self.run_alg_action.triggered.connect(self.run_alg)
        self.stop_alg_action = QAction("&Остановить имитатор", self)
        self.run_mb = QAction("&Запустить ModbusTCP Client", self)
        self.run_mb.triggered.connect(self.run_modbus)
        self.stop_mb = QAction("&Остановить ModbusTCP Client", self)
        # Устанавливаем в панель меню данный Action.
        menubar = self.menuBar()
        mmenu = menubar.addMenu("&Меню")
        mmenu.addAction(self.up_action)
        mmenu.addSeparator()
        mmenu.addAction(self.new_action)
        mmenu.addSeparator()
        mmenu.addAction(save_action)
        mmenu.addAction(download_action)
        mmenu.addSeparator()
        mmenu.addAction(self.del_action)
        mmenu.addAction(delconf_action)
        mmenu.addSeparator()
        mmenu.addAction(setup_action)
        mmenu.addSeparator()
        mmenu.addAction(about_action)
        mmenu.addSeparator()
        mmenu.addAction(exit_action)
        imenu = menubar.addMenu("&Имитатор")
        imenu.addAction(self.run_alg_action)
        imenu.addAction(self.stop_alg_action)
        mb_menu = menubar.addMenu("&Modbus")
        mb_menu.addAction(self.run_mb)
        mb_menu.addAction(self.stop_mb)

        # STATUSBAR
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.text_1 = "<h3 style='color: red;'>Имитатор остановлен.</h3>"
        self.iLabel = QLabel(f"{self.text_1}")
        self.statusbar.addPermanentWidget(self.iLabel)
        self.text_2 = "<h3 style='color: red;'>Modbus остановлен.</h3>"
        self.mbLabel = QLabel(f"{self.text_2}")
        self.statusbar.addPermanentWidget(self.mbLabel)

        #лист добавления новых элементов разного типа
        self.stackedWidget = QtWidgets.QStackedWidget(self)
        self.v1_layout.addWidget(self.stackedWidget, 0, 0)
        self.v1_layout.setRowMinimumHeight(0, 120)
        self.v1_layout.setRowStretch(1, 1)
        self.v1_layout.setRowStretch(0, 0)

        gr_box1 = QtWidgets.QGroupBox(" Добавление новых элементов ", self)
        self.stackedWidget.addWidget(gr_box1)
        gr1_layout = QGridLayout()
        gr1_layout.addWidget(QLabel("Имитатор:"), 0, 0,alignment=Qt.AlignRight)
        self.ip_cBox = QtWidgets.QComboBox(self)
        self.ip_cBox.setEnabled(False)
        gr1_layout.addWidget(self.ip_cBox, 0, 1, 1,2)
        gr1_layout.addWidget(QLabel("Тип оборудования:"), 1, 0,alignment=Qt.AlignRight)
        self.typ_cBox = QtWidgets.QComboBox(self)
        gr1_layout.addWidget(self.typ_cBox, 1, 1, 1,2)
        gr1_layout.addWidget(QLabel("Наименование:"), 2, 0,alignment=Qt.AlignRight)
        self.name_lineEdit = QtWidgets.QLineEdit(self)
        gr1_layout.addWidget(self.name_lineEdit, 2, 1, 1,2)
        self.btnCreate = QPushButton("        СОЗДАТЬ        ", self)
        self.btnCreate.setEnabled(False)
        #self.btnCreate.clicked.connect(lambda: self.generate(cl_sh))  # cl_di
        self.btnExit = QPushButton("Выход", self)
        self.btnExit.clicked.connect(self.btn_ctrl_stackedWidget)
        gr1_layout.addWidget(self.btnCreate,3,1,alignment=Qt.AlignLeft)
        gr1_layout.addWidget(self.btnExit,3,2,alignment=Qt.AlignRight)
        gr_box1.setLayout(gr1_layout)  # Закидываем область с кнопками в группу

        self.gr_box2 = QtWidgets.QGroupBox(" Управление элементом ", self) #
        self.stackedWidget.addWidget(self.gr_box2)
        self.gr2_layout = QGridLayout()
        self.gr2_label = QLabel("Имя")
        self.gr2_label.setFont(QFont('Decorative', 14))
        self.gr2_layout.addWidget(self.gr2_label, 0, 0)
        self.gr2_btnSet = QPushButton("Set", self)
        #self.gr2_btnSet.clicked.connect(self.btn_set)
        self.gr2_btnReset = QPushButton("Reset", self)
        #self.gr2_btnReset.clicked.connect(self.btn_reset)
        self.gr2_layout.addWidget(self.gr2_btnSet,1,0,alignment=Qt.AlignLeft)
        self.gr2_layout.addWidget(self.gr2_btnReset,1,1,alignment=Qt.AlignLeft)
        self.gr_box2.setLayout(self.gr2_layout)  # Закидываем область с кнопками в группу
        self.dict_obj = {1: [self.gr2_label, self.gr2_btnSet, self.gr2_btnReset]}

        self.gr_box3 = QtWidgets.QGroupBox("", self)  #
        self.stackedWidget.addWidget(self.gr_box3)
        self.dict_obj[2] = []
        self.stackedWidget.setCurrentIndex(2)

        self.stackedWidget.currentChanged.connect(self.ctrl_stackedWidget)


        self.typ_cBox.addItem("Дискретный сигнал")
        self.typ_cBox.addItem("Секция шин")
        self.typ_cBox.addItem("Задвижка")
        self.typ_cBox.currentIndexChanged[int].connect(self.typ_Change)
        self.typ_Change(0)

        self.name_lineEdit.textChanged[str].connect(self.nameChanged)
        #reg_ex = QRegExp("[0-9]+.?[0-9]{,2}") #ввод только чисел с двумя десятичными знаками
        reg_ex = QRegExp("^[\-./_ A-ZА-Яa-zа-я0-9]{1,40}$")
        input_validator = QRegExpValidator(reg_ex, self.name_lineEdit)
        self.name_lineEdit.setValidator(input_validator)

    '''
        # Создание нового окна
        self.button = QPushButton('Создать окно', self)
        self.button.setFixedSize(150, 24)
        self.button.clicked.connect(self.new_win)

        self.v2_layout.addWidget(self.button)

        self.new_window = QWidget()
        self.new_window.resize(350, 120)
        #Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.new_window.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)  # делает окно onTop
        self.new_window.setWindowTitle('Добавление новых элементов')
        new_layout = QGridLayout()
        new_layout.addWidget(QLabel("Имитатор:"), 0, 0,alignment=Qt.AlignRight)
        self.ip_cBox = QtWidgets.QComboBox(self)
        self.ip_cBox.setEnabled(False)
        new_layout.addWidget(self.ip_cBox, 0, 1, 1,2)
        new_layout.addWidget(QLabel("Тип оборудования:"), 1, 0,alignment=Qt.AlignRight)
        self.typ_cBox = QtWidgets.QComboBox(self)
        new_layout.addWidget(self.typ_cBox, 1, 1, 1,2)
        new_layout.addWidget(QLabel("Наименование:"), 2, 0,alignment=Qt.AlignRight)
        self.name_lineEdit = QtWidgets.QLineEdit(self)
        new_layout.addWidget(self.name_lineEdit, 2, 1, 1,2)
        self.btnCreate = QPushButton("        СОЗДАТЬ        ", self)
        self.btnCreate.setEnabled(False)
        #self.btnCreate.clicked.connect(lambda: self.generate(cl_sh))  # cl_di
        #self.btnExit = QPushButton("Выход", self)
        #self.btnExit.clicked.connect(self.btn_ctrl_stackedWidget)
        new_layout.addWidget(self.btnCreate,3,1,alignment=Qt.AlignLeft)
        #new_layout.addWidget(self.btnExit,3,2,alignment=Qt.AlignRight)
        self.new_window.setLayout(new_layout)  # Закидываем область с кнопками в группу

    def new_win(self):
        self.new_window.show()
    '''

    def ctrl_stackedWidget(self):
        if self.stackedWidget.currentIndex() == 0 or self.stackedWidget.currentIndex() == (self.stackedWidget.count() - 1):
            self.del_action.setEnabled(False)
        else:
            self.del_action.setEnabled(True)

    def mw_onTop(self):
        if self.up_action.isChecked():
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint) # делаем окно onTop и оставляем только кнопку закрыть
        else:
            self.setWindowFlags(Qt.WindowCloseButtonHint) # оставляем только кнопку закрыть
        self.show()

    def cl_typ(self, typ): #выбор имени класса по типу
        if typ == 0:
            sel_obj = cl_di
        elif typ == 1:
            sel_obj = cl_sh
        elif typ == 2:
            sel_obj = cl_zd
        # elif typ == 3:
        #     sel_obj = cl_vs
        # elif typ == 4:
        #     sel_obj = cl_na
        return sel_obj

    def typ_Change(self, typ):
        sel_obj = self.cl_typ(typ)
        try:    #привязка к кнопке действия создания ВЫБРАННОГО элемента
            self.btnCreate.clicked.disconnect()
        except Exception: pass
        self.btnCreate.clicked.connect(lambda: self.generate(sel_obj))


    def nameChanged(self, text):
        fl_find = False
        for cl in self.spin:
            if cl.params['name'] == text.rstrip():
                fl_find = True
                self.statusbar.showMessage("Имя элемента должно быть уникально и более 2 символов.", 3000)
                break   # break from loop for
        if len(text) >= 2 and not fl_find:
            self.btnCreate.setEnabled(True)
        else:
            self.btnCreate.setEnabled(False)

    def generate(self, link_class):
        obj = link_class(len(self.spin), self) #self.scrollAreaComponents
        obj.params['name'] = self.name_lineEdit.text()  #заносим значение в словарь
        obj.obj_num.connect(self.set_Widget)
        # obj.left_click.connect(self.set_Widget)
        obj.setFixedSize(100, 100)
        #self.grbox.addWidget(obj) #добавление без кординат не заносит в ранее занятые и удаленные ячейки
        self.grbox.addWidget(obj, self.grbox.count() // self.Cnt_columns, self.grbox.count() % self.Cnt_columns)
        self.spin.append(obj)
        self.nameChanged(self.name_lineEdit.text())

    def set_Widget(self, num):  #Отобразить панель управления выбранным элементом
        obj = self.spin[num]
        self.Num = num
        obj.add_control(self.stackedWidget, self.dict_obj)
        self.model.update_model(obj.params['sign']) #обновляет таблицу table
        self.modelTm.update_model(obj.tm)  # обновляет таблицу tableTm

    def run_alg(self):
        if len(self.spin) > 0:
            self.run_alg_action.setEnabled(False)
            # запуск потока обработки алгоритмов
            #self.thread = QThread()
            #self.worker = Algoritm(self.spin)
            #self.worker.moveToThread(self.thread)
            #self.thread.started.connect(self.worker.run)
            #self.worker.finished.connect(self.thread.quit)
            #self.worker.finished.connect(self.worker.deleteLater) #--Удаляем объект worker
            #self.thread.finished.connect(self.thread.deleteLater) #--Удаляем объект thread
            #self.thread.start()
            self.thr_alg = cl_Algoritm(self.spin, self)
            self.thr_alg.start()
            # Final resets
            self.thr_TmOneSec = clTmOneSec(self)    #поток возвращающий секунды 0-59
            self.thr_TmOneSec.start()
            self.thr_TmOneSec.second.connect(self.defOneSec)
            # Добавление постоянного сообщения в статусбар
            self.text_1 = "<h3 style='color: green;'>Имитатор запущен.</h3>"
            self.iLabel.setText(f"{self.text_1}")
            self.statusbar.update()

    def defOneSec(self, sec):   #меняет каждую секунду бит self.parent.tmOneSec
        self.tmOneSec = sec % 2
        self.repaint()   # test !!! обновление экрана. Проблема update не вызывает paintEvent

    def run_modbus(self):
        self.run_mb.setEnabled(False)
        self.thr_modbus = cl_modbus(self.spin, mainwindow=self)
        self.thr_modbus.start()
        # Добавление постоянного сообщения в статусбар
        self.text_2 = "<h3 style='color: green;'>Modbus запущен.</h3>"
        self.mbLabel.setText(f"{self.text_2}")
        self.statusbar.update()

    def add_new_Widget(self):  #Отобразить панель добавления новых объектов
        self.stackedWidget.setCurrentIndex(0)

    def btn_ctrl_stackedWidget(self):
        if self.Num >= 0:
            self.stackedWidget.setCurrentIndex(self.spin[self.Num].params['ind_stackedWidget'])
        else:
            self.stackedWidget.setCurrentIndex(self.stackedWidget.count() - 1)
        #self.stackedWidget.removeWidget(self.stackedWidget.currentWidget())

    def file_save(self):
        name = QFileDialog.getSaveFileName(self, 'Сохранить файл', 'Save', '*.json')
        if name[0] != '': # если файл выбран
            dict_params = {}
            for s in self.spin: # перенос из списка spin в словарь dict_params
                dict_params[s.params['num']] = s.params
            # Запись в файл
            with open(name[0], 'w', encoding='utf-8') as fp:              # indent=4 - сохраняет файл с переходом строк
                json.dump(dict_params, fp, ensure_ascii=False, indent=4)  # ensure_ascii=False - русские буквы в файле

    def file_load(self):
        name = QFileDialog.getOpenFileName(self, 'Открыть файл', 'Save', '*.json')
        if name[0] != '': # если файл выбран
            self.del_all()
            # Чтение из файла
            with open(name[0], encoding='utf-8') as fp:
                                            # json сохраняет ключи в sting, поэтому необходимо преобразование в int
                dict_params = json.load(fp, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit()
                                                                          else k: v for k, v in d.items()})
            for dct in dict_params.values():
                sel_obj = self.cl_typ(dct['typ'])
                obj = sel_obj(dct['num'], self, dct) #self.scrollAreaComponents
                obj.obj_num.connect(self.set_Widget)
                obj.setFixedSize(100, 100)
                self.grbox.addWidget(obj, self.grbox.count() // self.Cnt_columns, self.grbox.count() % self.Cnt_columns)   #добавить obj в группу grbox объекта scrollAreaComponents
                self.spin.append(obj)


    def del_item(self):
        if self.Num != -1:
            #print('del '+str(self.Num))
            self.stackedWidget.setCurrentIndex(self.stackedWidget.count() - 1)
            obj = self.spin[self.Num]
            self.spin.remove(obj)
            self.grbox.layout().removeWidget(obj)
            obj.deleteLater()
            del obj #= None
            for i in range(self.Num, len(self.spin)): #убираем пропуск в индексах элементов
                self.spin[i].params['num'] = i
            self.repaint_grbox()
            self.Num = -1
            self.clear_table()

    def del_allwidgets_grbox(self):
        if len(self.spin) > 0:
            self.stackedWidget.setCurrentIndex(self.stackedWidget.count() - 1)
            while self.grbox.count() > 0:
                widget = self.grbox.itemAt(0).widget()
                self.grbox.removeWidget(widget)
                widget.setParent(None)

    def repaint_grbox(self):
        self.del_allwidgets_grbox()
        for s in self.spin:
            if s.visible:
                self.grbox.addWidget(s, self.grbox.count()//self.Cnt_columns, self.grbox.count()%self.Cnt_columns)   #добавить obj в группу grbox объекта scrollAreaComponents по координатам

    def clear_table(self):
        # Очистить таблицы
        dct = {}
        dct['DI'] = {}
        dct['DO'] = {}
        dct['AI'] = {}
        dct['AO'] = {}
        self.model.update_model(dct)  # обновляет таблицу table
        dct_tm = {}
        self.modelTm.update_model(dct_tm)  # обновляет таблицу tableTm

    def del_all(self):
        if len(self.spin) > 0:
            self.stackedWidget.setCurrentIndex(self.stackedWidget.count() - 1)
            for obj in self.spin:
                self.grbox.layout().removeWidget(obj)
                obj.deleteLater()
                del obj #= None
            # while self.grbox.count() > 0:
            #     widget = self.grbox.itemAt(0).widget()
            #     self.grbox.removeWidget(widget)
            #     widget.setParent(None)
            self.spin = []
            self.Num = -1
            self.clear_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = Window()
    mw.show()
    sys.exit(app.exec())
