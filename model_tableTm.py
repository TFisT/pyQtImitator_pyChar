from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex


class ModelTm(QtCore.QAbstractTableModel):
    layoutChanged = QtCore.pyqtSignal() #!!! без этого объявления tableview не обновлялся
    dataChanged = QtCore.pyqtSignal(QModelIndex, QModelIndex)
    def __init__(self, parent, spin, Num):
        QtCore.QAbstractTableModel.__init__(self)
        self.parent = parent
        self.tm = {}
        self.colLabels = {0: 'Параметр', 1: 'Установлено', 2: 'Текущее значение'}
        if Num >= 0: #номер выбранного элемента
            self.tm = spin[Num].tm #словарь таймеров с предустановленным временем

    def update_model(self, tm):
        self.tm = tm
        self.layoutChanged.emit() #обновление визуализации

    def rowCount(self, parent):
        return len(self.tm)

    def columnCount(self, parent):
        return len(self.colLabels)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole:
            return QtCore.QVariant()
        value = ''
        if role == Qt.DisplayRole or role == Qt.EditRole:
            row = index.row()
            col = index.column()
            if (row+1) in self.tm:
                if col == 0:
                    value = self.tm[row+1].name
                elif col == 1:
                    value = self.tm[row+1].SP
                elif col == 2:
                    value = self.tm[row+1].ACC
        return value

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 1:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            if index.column() == 1:
                self.parent.spin[self.parent.Num].params['timer'][index.row()+1]['SP'] = value
                self.tm[index.row()+1].SP = value
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QtCore.QVariant(self.colLabels[section])
        return QtCore.QVariant()

