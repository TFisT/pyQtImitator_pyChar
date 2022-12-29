from time import sleep, time
from PyQt5.QtCore import pyqtSignal, QThread

class cl_Algoritm(QThread):
    finished = pyqtSignal()

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.th_spin = data # <-- data которая нужна для расчетов, и которую получим из основного потока
        # # Чтение из файла
        # with open('TypeJSON\\DO_wrMW.json', encoding='utf-8') as fp:
        #     # json сохраняет ключи в sting, поэтому необходимо преобразование в int
        #     self.DO_wrMW = json.load(fp, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit()
        #                                                        else k: v for k, v in d.items()})  # ensure_ascii=False - русские буквы в файле

    def run(self):
        from app import rdMW, wrMW  # обращение к глобальной переменной из app
        while True: # БЕСКОНЕЧНЫЙ ЦИКЛ
            if self.parent.Num != -1:
                self.th_spin = self.parent.spin #переопределение ссылки на глобальный список spin, т.к. после удаления в локальном остаются удаленные элементы
                #цикл алгоритма - цикл по всем элементам spin
                for i in range(len(self.th_spin)):
                    obj = self.th_spin[i]
                    obj.Algoritm()

                    #обработка всех DI для всех элементов
                    for DI in obj.params['sign']['DI'].values():
                        #rdMW -> spin['DI']['io_val']
                        if (DI['MW'] != -1) and (DI['i'] != -1): #модуль и канал выбран = слово и бит установлены
                            bi = 0x0001 << DI['i']  # в слове bi устанавливаем бит i (остальные биты = 0)
                            DI['io_val'] = (rdMW[DI['MW']] & bi != 0)
                            # приоритета состояния сигнала в колонке «Имитировать» над сигналом в колонке «Контакт»
                            if DI['priority'] == 1:
                                DI['logix'] = DI['imit']  # имитация
                            else:
                                # если инверсия, то проинветировать значение со входа в логику
                                if DI['inv'] == 0:
                                    DI['logix'] = DI['io_val']
                                else:
                                    DI['logix'] = not DI['io_val']

                    #обработка всех DO для всех элементов
                    for DO in obj.params['sign']['DO'].values():
                        # приоритета состояния сигнала в колонке «Имитировать» над сигналом в колонке «Контакт»
                        if DO['priority'] == 1:
                            DO['logix'] = DO['imit'] #значение Логика = имитируемое значение
                        # если инверсия, то проинветировать имитируемое значение или значение из логики
                        if DO['inv'] == 0:
                            DO['io_val'] = DO['logix']
                        else:
                            DO['io_val'] = not DO['logix']

                        #spin['DO']['io_val'] -> wrMW
                        if (DO['MW'] != -1) and (DO['i'] != -1): #модуль и канал выбран = слово и бит установлены
                            # установить/сбросить в слове MW бит i в значение DO['io_val']
                            bi = 0x0001 << DO['i'] # в слове bi устанавливаем бит i (остальные биты = 0)
                            if DO['io_val'] == 1:
                                wrMW[DO['MW']] = wrMW[DO['MW']] | bi #установить бит i
                            else:
                                wrMW[DO['MW']] = wrMW[DO['MW']] & ~bi #сбросить бит i

                    obj.update() #обновить все элементы в spinArea


                #print(wrMW[0])
                if self.parent.Num != -1:
                    self.parent.model.update_model(self.th_spin[self.parent.Num].params['sign'])  # обновляет таблицу table для выбранного элемента
                    self.parent.modelTm.update_model(self.th_spin[self.parent.Num].tm)  # обновляет таблицу tableTm для выбранного элемента


                sleep(0.1) # 100 мс

        self.finished.emit()


class clTmOneSec(QThread):  #поток меняющий каждую секунду бит self.parent.tmOneSec
    second = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.sec = 0

    def run(self):
        while True:
            #self.parent.tmOneSec = self.sec % 2
            #print(self.sec, self.parent.tmOneSec)
            self.second.emit(self.sec)
            sleep(1)
            self.sec = (self.sec + 1)%60