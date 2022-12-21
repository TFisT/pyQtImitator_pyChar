from PyQt5 import QtCore
from PyQt5.QtWidgets import QStyledItemDelegate, QTableView
from PyQt5.QtCore import Qt, QModelIndex, QPoint


class MyDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(MyDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if index.column() == 0:
            if index.data() == 1:  # в зависимости от текста в ячейке изменить цвет ячейки
                painter.fillRect(option.rect, Qt.darkGreen)  # выделить ячейку цветом
            #else:
            #    painter.setBrush(Qt.color0)
            QStyledItemDelegate.paint(self, painter, option, index)

        elif index.column() == 1:
            if index.data() == 3:
                painter.setBrush(Qt.darkGreen)
                painter.drawEllipse(option.rect.topLeft().x() + 10, option.rect.topLeft().y() + 3, 13, 13)
            elif index.data() == 1:
                painter.setBrush(Qt.darkGreen)
                painter.drawRect(option.rect.topLeft().x() + 10, option.rect.topLeft().y() + 3, 13, 13)

        elif index.column() == 2:
            if index.data()[1] == 'DI':
                painter.fillRect(option.rect, Qt.yellow)  # выделить ячейку цветом
            txt = index.data()[0]
            painter.drawText(option.rect, Qt.AlignLeft | Qt.AlignVCenter, txt)

        elif index.column() == 3:
            if index.data() == 1:
                painter.setBrush(Qt.darkGreen)
                painter.drawEllipse(option.rect.topLeft().x() + 10, option.rect.topLeft().y() + 3, 13, 13)

        elif index.column() == 4:
            if index.data() == 1:
                painter.setBrush(Qt.darkGreen)
                painter.drawRect(option.rect.topLeft().x() + 10, option.rect.topLeft().y() + 3, 13, 13)

        elif index.column() == 5:
            if index.data()[0] == 1:
                #painter.setBrush(Qt.darkGreen)
                painter.fillRect(option.rect, Qt.darkGreen)  # выделить ячейку цветом
            txt = index.data()[1]
            painter.drawText(option.rect, Qt.AlignLeft | Qt.AlignVCenter, txt)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)


class Model(QtCore.QAbstractTableModel):
    layoutChanged = QtCore.pyqtSignal() #!!! без этого объявления tableview не обновлялся
    dataChanged = QtCore.pyqtSignal(QModelIndex, QModelIndex)
    def __init__(self, spin, Num):
        QtCore.QAbstractTableModel.__init__(self)

        self.sign = {}
        self.colLabels = {0: 'Имитировать', 1: '!', 2: 'Сигнал', 3: 'Лог', 4: '^', 5: 'Контакт'}
        self.col_spin = {0: 'imit', 1: 'priority', 2: 'name', 3: 'logix', 4: 'inv', 5: 'io_val'}
        if Num >= 0: #номер выбранного элемента
            self.sign = self.__create_dict_sign(spin[Num].params['sign'])
            #self.sign = spin[Num].params['sign']['DO'] #словарь сигналов - пока только DO

    def __create_dict_sign(self, sign): # все сигналы DI DO AI AO в словарь _sign   !!!Пока все сигналы, потом только привязаные к io
        _sign = {}
        ind = 0
        for key, value in sign['DI'].items():
            _sign[ind] = value
            _sign[ind]['type_sign'] = 'DI'
            _sign[ind]['key_sign'] = key
            ind += 1
        for key, value in sign['DO'].items():
            _sign[ind] = value
            _sign[ind]['type_sign'] = 'DO'
            _sign[ind]['key_sign'] = key
            ind += 1
        for key, value in sign['AI'].items():
            _sign[ind] = value
            _sign[ind]['type_sign'] = 'AI'
            _sign[ind]['key_sign'] = key
            ind += 1
        for key, value in sign['AO'].items():
            _sign[ind] = value
            _sign[ind]['type_sign'] = 'AO'
            _sign[ind]['key_sign'] = key
            ind += 1
        return _sign

    def update_model(self, sign):
        self.sign = self.__create_dict_sign(sign) #['DO'] #словарь сигналов - пока только DO
        #print('upd_model ', self.sign)
        #self.layoutAboutToBeChanged.emit()
        #self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit() #обновление визуализации

    def rowCount(self, parent):
        return len(self.sign)

    def columnCount(self, parent):
        return len(self.colLabels)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole:
            return QtCore.QVariant()
        value = ''
        if role == Qt.DisplayRole or role == Qt.EditRole: # or role == Qt.CheckStateRole:
            row = index.row()
            col = index.column()
            if row in self.sign:
                if col == 2:
                    value = [self.sign[row][self.col_spin[2]], self.sign[row]['type_sign']]
                elif col == 5:
                    value = [self.sign[row][self.col_spin[5]], self.sign[row]['io']]
                else:
                    value = self.sign[row][self.col_spin[col]]
        return value

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable #Qt.ItemIsUserCheckable
        elif index.column() in (1, 4):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled #| Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            self.sign[index.row()][self.col_spin[index.column()]] = value
            #self.emit(QtCore.pyqtSignal("dataChanged(QModelIndex, QModelIndex)"), index, index)
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QtCore.QVariant(self.colLabels[section])
        return QtCore.QVariant()

class CustomTableView(QTableView):
    def __init__(self, parent):
        QTableView.__init__(self)
        self.parent = parent

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            index = self.indexAt(QPoint(e.x(), e.y()))
            if index.isValid() and (index.flags() & Qt.ItemIsSelectable):
                if index.column() != 1 or (index.column() == 1 and index.data() < 2): #в столбце приоритета при значении >= 2 запрещаем изменение по клику
                    value = (int(index.data())+1)%2
                    self.model().setData(index, value, Qt.EditRole)
                if self.parent.Num >= 0:
                    obj = self.parent.spin[self.parent.Num]
                    obj._update()
