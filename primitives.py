import math
from PyQt5 import Qt
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainterPath


class primitives():

    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def __init__(self, qp):
        self.qp = qp

    def draw_triangle(self, color=Qt.qGreen, x=0, y=0, a=10, direction=UP):
        d = a * math.tan(math.radians(30))
        pos_top = QPointF(x, y)
        if direction == self.UP:
            pos_2 = QPointF(x - d, y + a)
            pos_3 = QPointF(x + d, y + a)
        elif direction == self.DOWN:
            pos_2 = QPointF(x + a, y)
            pos_3 = QPointF(x + d, y + a)
        elif direction == self.RIGHT:
            pos_2 = QPointF(x + a, y+d)
            pos_3 = QPointF(x, y + a)
        elif direction == self.LEFT:
            pos_2 = QPointF(x - a, y+d)
            pos_3 = QPointF(x, y + a)

        self.qp.setBrush(color)
        path = QPainterPath()
        path.moveTo(pos_top)
        path.lineTo(pos_3)
        path.lineTo(pos_2)
        path.lineTo(pos_top)
        self.qp.drawPath(path)


