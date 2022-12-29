from PyQt5.QtWidgets import QWidget, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter
from Timer import clTimer
import json
from primitives import primitives

class cl_zd(QWidget):
    left_click = pyqtSignal()
    obj_num = pyqtSignal(int)

    def __init__(self, num, parent, dct={}):
        super().__init__(parent)
        if len(dct) == 0: #создание объекта на основе шаблонного файла json
            # Чтение из файла
            with open('TypeJSON\\zd.json', encoding='utf-8') as fp:
                                            # json сохраняет ключи в sting, поэтому необходимо преобразование в int
                self.params = json.load(fp, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit()
                                                                          else k: v for k, v in d.items()})  # ensure_ascii=False - русские буквы в файле
        else:
            self.params = dct

        self.params['num'] = num
        self.parent = parent
        self.visible = True
        self.tm = {}    # создаем словарь таймеров с предустановленным временем    #self.tm = {1: clTimer()}
        for key in self.params['timer']:
            self.tm[key] = clTimer()
            self.tm[key].name = self.params['timer'][key]['name']
            self.tm[key].SP = self.params['timer'][key]['SP']

    def paintEvent(self, event):
        #print(self.params['sign'])
        painter = QPainter(self)
        painter.begin(self)
        painter.drawRect(0, 0, 99, 99)
        painter.drawRect(57, 32, 4, 25)                                                 # прямоугольник под Аварией

        if self.params['sign']['DO']['КВО']['io_val'] == 1:    #КВО
            painter.setBrush(Qt.green)
        else: painter.setBrush(Qt.yellow)
        painter.drawRect(24, 38, 5, 34)                                                 # КВО

        if self.params['sign']['DO']['КВЗ']['io_val'] == 1:    #КВЗ
            painter.setBrush(Qt.green)
        else: painter.setBrush(Qt.yellow)
        painter.drawRect(90, 38, 5, 34)                                                 # КВЗ

        if self.params['sign']['DO']['МПО']['io_val'] == 1:    #МПО
            painter.setBrush(Qt.green)
            primitives(painter).draw_triangle(Qt.green, 84, 20, 10, primitives.UP)      # МПО

        if self.params['sign']['DO']['МПЗ']['io_val'] == 1:    #МПЗ
            painter.setBrush(Qt.yellow)
            primitives(painter).draw_triangle(Qt.yellow, 87, 20, 10, primitives.DOWN)       # МПЗ

        if self.params['sign']['DO']['КВО']['io_val'] == 1 and self.params['sign']['DO']['КВЗ']['io_val'] == 1:  # КВО и КВЗ
            if self.params['sign']['DO']['МПО']['io_val'] == 1:    #МПО
                if self.parent.tmOneSec == 0:
                    primitives(painter).draw_triangle(Qt.green, 29, 40, 30, primitives.RIGHT)  # Открывается
                    primitives(painter).draw_triangle(Qt.green, 90, 40, 30, primitives.LEFT)
                else:
                    primitives(painter).draw_triangle(Qt.black, 29, 40, 30, primitives.RIGHT)
                    primitives(painter).draw_triangle(Qt.black, 90, 40, 30, primitives.LEFT)
            elif self.params['sign']['DO']['МПЗ']['io_val'] == 1:  # МПЗ
                if self.parent.tmOneSec == 0:
                    primitives(painter).draw_triangle(Qt.yellow, 29, 40, 30, primitives.RIGHT)  # Закрывается
                    primitives(painter).draw_triangle(Qt.yellow, 90, 40, 30, primitives.LEFT)
                else:
                    primitives(painter).draw_triangle(Qt.black, 29, 40, 30, primitives.RIGHT)
                    primitives(painter).draw_triangle(Qt.black, 90, 40, 30, primitives.LEFT)
            else:
                primitives(painter).draw_triangle(Qt.green, 29, 40, 30, primitives.RIGHT)    # Промежуточное положение
                primitives(painter).draw_triangle(Qt.yellow, 90, 40, 30, primitives.LEFT)
        elif self.params['sign']['DO']['КВЗ']['io_val'] == 1:  # КВЗ
            primitives(painter).draw_triangle(Qt.green, 29, 40, 30, primitives.RIGHT)    # Открыта
            primitives(painter).draw_triangle(Qt.green, 90, 40, 30, primitives.LEFT)
        elif self.params['sign']['DO']['КВО']['io_val'] == 1:    #КВО
            primitives(painter).draw_triangle(Qt.yellow, 29, 40, 30, primitives.RIGHT)    # Закрыта
            primitives(painter).draw_triangle(Qt.yellow, 90, 40, 30, primitives.LEFT)
        else:
            primitives(painter).draw_triangle(Qt.gray, 29, 40, 30, primitives.RIGHT)    # Не определено
            primitives(painter).draw_triangle(Qt.gray, 90, 40, 30, primitives.LEFT)


        if self.params['sign']['DO']['МВО']['io_val'] == 1 or self.params['sign']['DO']['МВЗ']['io_val'] == 1:    #Муфта (МВО) или (МВЗ)
            painter.setBrush(Qt.red)
            painter.drawRect(44, 48, 32, 16)                                                # Муфта
            if self.params['sign']['DO']['МВО']['io_val'] == 1 and self.params['sign']['DO']['МВЗ']['io_val'] == 1:
                painter.drawText(50, 60, "2МВ")
            elif self.params['sign']['DO']['МВО']['io_val'] == 1:
                painter.drawText(50, 60, "МВО")
            else: painter.drawText(50, 60, "МВЗ")

        if self.params['sign']['DO']['АВ']['io_val'] == 1:    #Авария
            painter.setBrush(Qt.red)
        else: painter.setBrush(Qt.green)
        painter.drawEllipse(51, 20, 16, 16)                                                 # Авария

        if self.params['sign']['DO']['МД']['io_val'] == 1:  # Дистанционное управление
            painter.setBrush(Qt.green)
            painter.drawRect(25, 18, 16, 16)                                                 # М/Д
            painter.drawText(30, 30, "Д")
        else:
            painter.setBrush(Qt.blue)
            painter.drawRect(25, 18, 16, 16)                                                 # М/Д
            painter.setPen(Qt.white)
            painter.drawText(30, 30, "М")
            painter.setPen(Qt.black)

        painter.setBrush(Qt.red)
        if self.params['sign']['DO']['ЦЗ']['io_val'] == 0:  # Исправность цепи закрытия
            rect = QRect(3, 38, 18, 16)
            painter.drawRect(rect)                                                 # ЦЗ
            painter.drawText(rect, Qt.AlignCenter, "ЦЗ")
        if self.params['sign']['DO']['ЦО']['io_val'] == 0:  # Исправность цепи открытия
            rect = QRect(3, 56, 18, 16)
            painter.drawRect(rect)                                                 # ЦО
            painter.drawText(rect, Qt.AlignCenter, "ЦО")

        if self.params['sign']['DO']['U']['io_val'] == 0:  # Контроль напряжения питания
            painter.drawEllipse(4, 75, 16, 16)                                              # Наличие напряжения
            painter.drawText(10, 87, "U")

        painter.setBrush(Qt.green)
        st = str(1)
        rect = QRect(44, 75, 32, 16)
        painter.drawRect(rect)                                                # Процент открытия
        painter.drawText(rect, Qt.AlignCenter, st)

        #painter.setFont(QFont('Decorative', 8))
        painter.drawText(4, 12, self.params['name'])
        painter.end()

    def mousePressEvent(self, e):
        #QPushButton.mousePressEvent(self, e)
        if e.button() == Qt.LeftButton:
            self.left_click.emit()
            self.obj_num.emit(self.params['num'])
            return

    def add_control(self, stackedWidget, dict_obj):
        stackedWidget.setCurrentIndex(1) #в данном классе self.params['ind_stackedWidget']=1
        if len(dict_obj[1]) == 3:
            dict_obj[1][0].setText(self.params['name'])
            try:
                dict_obj[1][1].clicked.disconnect()
            except Exception: pass
            dict_obj[1][1].clicked.connect(self.btn_set)
            try:
                dict_obj[1][2].clicked.disconnect()
            except Exception: pass
            dict_obj[1][2].clicked.connect(self.btn_reset)

    def btn_set(self):
        self.params['sign']['DO']['КВО']['imit'] = 1 #A
        self._update()

    def btn_reset(self):
        self.params['sign']['DO']['КВО']['imit'] = 0  #A
        self._update()

    def _update(self):
        self.update()
        self.parent.model.update_model(self.params['sign'])  # обновляет таблицу table

    def Algoritm(self):
        #запуск всех таймеров
        for _tm in self.tm.values():
            _tm.start()


        self.tm[1].EN = (self.params['sign']['DI']['ОО']['logix'] == 1)
        if self.tm[1].DN:
            self.params['sign']['DO']['МПО']['logix'] = 1
