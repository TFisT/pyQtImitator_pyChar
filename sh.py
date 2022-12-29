from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter
from Timer import clTimer
import json

class cl_sh(QWidget):
    left_click = pyqtSignal()
    obj_num = pyqtSignal(int)

    def __init__(self, num, parent, dct={}):
        super().__init__(parent)
        if len(dct) == 0: #создание объекта на основе шаблонного файла json
            # Чтение из файла
            with open('TypeJSON\\sh.json', encoding='utf-8') as fp:
                                            # json сохраняет ключи в sting, поэтому необходимо преобразование в int
                self.params = json.load(fp, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit()
                                                                          else k: v for k, v in d.items()})  # ensure_ascii=False - русские буквы в файле
        else:
            self.params = dct
            #создание объекта на основе строки json
            #self.params = json.loads(st, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit()
            #                                                           else k: v for k, v in d.items()})

        '''   
        # Запись в файл
        with open('TypeJSON\\sh.json', 'w', encoding='utf-8') as fp:
            json.dump(self.params, fp, ensure_ascii=False)  # ensure_ascii=False - русские буквы в файле
        '''
        self.params['num'] = num
        self.parent = parent
        self.visible = True
        self.tm = {}    # создаем словарь таймеров с предустановленным временем    #self.tm = {1: clTimer()}
        for key in self.params['timer']:
            self.tm[key] = clTimer()
            self.tm[key].name = self.params['timer'][key]['name']
            self.tm[key].SP = self.params['timer'][key]['SP']

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.begin(self)
        painter.drawRect(0, 0, 99, 99)
        if self.params['sign']['DO']['A']['imit'] == 1:    #A
            painter.setBrush(Qt.green)
        else:
            painter.setBrush(Qt.red)
        painter.drawEllipse(40, 40, 20, 20)
        #painter.setFont(QFont('Decorative', 10)) # почемуто тормозит при добавлении первого объекта
        painter.drawText(48, 55, "U")
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
        self.params['sign']['DO']['A']['imit'] = 1 #A
        self._update()

    def btn_reset(self):
        self.params['sign']['DO']['A']['imit'] = 0  #A
        self._update()

    def _update(self):
        self.update()
        self.parent.model.update_model(self.params['sign'])  # обновляет таблицу table

    def Algoritm(self):
        #self.tm[1].SP = 2000   # должно заноситься из структуры. Обязательно перед вызовом start
        self.tm[1].start()

        self.tm[1].EN = (self.params['sign']['DO']['A']['imit'] == 0)  #A
        if self.tm[1].DN:
            self.params['sign']['DO']['A']['imit'] = 1  #A
        #print(str(self.tm.ACC))

        # значение Логика = имитируемое значение
        # for DO in self.params['sign']['DO'].values():
        #     DO['logix'] = DO['imit']

