import sys
from PyQt5 import QtWidgets, QtGui, QtCore


#TODO: implementar animação de um pacote sendo movido para outro
#TODO: pesquisar artgos sobre visualização de arquiteturas em software

class PackageObject(QtWidgets.QGraphicsObject):
    def __init__(self, parent, posx, posy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.polygon = QtGui.QPolygonF([
            QtCore.QPointF(0.0, 0.0),
            QtCore.QPointF(0.0, 20.0),
            QtCore.QPointF(80.0, 20.0),
            QtCore.QPointF(80.0, 0.0)
        ])
        self.posx = posx
        self.posy = posy
        self.setPos(self.mapFromScene(self.posx, self.posy))
        self.setParentItem(parent)
        
        self.penWidth = 1.0
        self.color = QtCore.Qt.red

        self.textItem = QtWidgets.QGraphicsTextItem()
        self.textItem.setParentItem(self)
        self.textItem.setDefaultTextColor(QtCore.Qt.white)
        self.textItem.setTextWidth(self.boundingRect().width())
        self.textItem.setHtml("<div style=\"text-align:center;\"> posy %s </div>" % posy)

        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        self.color = QtCore.Qt.white
        self.update()

    def mouseReleaseEvent(self, event):
        self.color = QtCore.Qt.red
        self.update()

    def hoverEnterEvent(self, event):
        self.anim = QtCore.QPropertyAnimation(self, b"pos")
        self.anim.setEndValue(
            QtCore.QPointF(
                self.pos().x() + 5.0,
                self.pos().y()
            )
        )
        self.anim.setDuration(50)
        self.anim.start()

    def hoverLeaveEvent(self, event):
        self.anim = QtCore.QPropertyAnimation(self, b"pos")
        self.anim.setEndValue(
            QtCore.QPointF(
                self.posx, self.posy
            )
        )
        self.anim.setDuration(50)
        self.anim.start()

    def boundingRect(self):
        return QtCore.QRectF(
            0.0 - self.penWidth / 2,
            0.0 - self.penWidth / 2,
            80.0 + self.penWidth,
            20.0 + self.penWidth
        )

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtCore.Qt.black,  self.penWidth, QtCore.Qt.SolidLine))        
        painter.setBrush(QtGui.QBrush(self.color, QtCore.Qt.SolidPattern))
        painter.drawPolygon(self.polygon)


class BufferObject(QtWidgets.QGraphicsObject):
    def __init__(self, posx, posy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.polygon = QtGui.QPolygonF([
            QtCore.QPointF(0.0, 0.0),
            QtCore.QPointF(0.0, 300.0),
            QtCore.QPointF(200.0, 300.0),
            QtCore.QPointF(200.0, 0.0)
        ])
        self.posx = posx
        self.posy = posy
        self.setPos(self.mapFromScene(self.posx, self.posy))
        self.packages = [
            PackageObject(parent=self, posx=10.0, posy=10.0),
            PackageObject(parent=self, posx=10.0, posy=41.0),
            PackageObject(parent=self, posx=10.0, posy=72.0),
            PackageObject(parent=self, posx=10.0, posy=103.0)
        ]
        self.penWidth = 2.0
        self.color = QtCore.Qt.blue

    def mousePressEvent(self, event):
        self.color = QtCore.Qt.white
        self.update()

    def mouseReleaseEvent(self, event):
        self.color = QtCore.Qt.blue
        self.update()

    def boundingRect(self):
        return QtCore.QRectF(
            0.0 - self.penWidth / 2,
            0.0 - self.penWidth / 2,
            200.0 + self.penWidth,
            300.0 + self.penWidth
        )

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtCore.Qt.black, self.penWidth, QtCore.Qt.SolidLine))        
        painter.setBrush(QtGui.QBrush(self.color, QtCore.Qt.SolidPattern))
        painter.drawPolygon(self.polygon)


class WindowWidget(QtWidgets.QMainWindow):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args,**kwargs)        

        self.setWindowTitle(title)
        self.setGeometry(QtGui.QGuiApplication.primaryScreen().availableGeometry())

        self.scene = QtWidgets.QGraphicsScene(
            self.geometry().x(),
            self.geometry().y(),
            self.geometry().width() * 0.7,
            self.geometry().height() * 0.7
        )
        self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.gray, QtCore.Qt.SolidPattern))
        self.buffers = [
            BufferObject(posx=10.0, posy=10.0),
            BufferObject(posx=220.0, posy=10.0)
        ]
        for buffer in self.buffers:
            self.scene.addItem(buffer)
        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.setCentralWidget(self.view)

        self.grabKeyboard()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            print("Right")
        elif event.key() == QtCore.Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = WindowWidget(title='OrCS-visual')
    window.showMaximized()
    sys.exit(app.exec_())
