import sys
from PyQt5 import QtWidgets, QtGui, QtCore


class SimpleItem(QtWidgets.QGraphicsItem):
    def boundingRect(self):
        penWidth = 1.0
        return QtCore.QRectF(
            -10 - penWidth / 2,
            -10 - penWidth / 2,
            200 + penWidth,
            200 + penWidth
        )

    def paint(self, painter, option, widget):
        painter.drawRoundedRect(-10, -10, 200, 200, 5, 5)


class TriangleItem(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPolygon(QtGui.QPolygonF([
            QtCore.QPointF(0, 0),
            QtCore.QPointF(0, 100),
            QtCore.QPointF(100, 100)
        ]))
        self.setPos(self.mapFromScene(50.0, 50.0))

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtCore.Qt.black,  2, QtCore.Qt.SolidLine))        
        painter.setBrush(QtGui.QBrush(QtCore.Qt.gray, QtCore.Qt.SolidPattern))
        painter.drawPolygon(self.polygon())
