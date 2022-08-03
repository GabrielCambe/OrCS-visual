from PyQt5 import QtWidgets, QtGui, QtCore


class PackageObject(QtWidgets.QGraphicsObject):
    def __init__(self, parent, posx, posy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.polygon = QtGui.QPolygonF([
            QtCore.QPointF(0.0, 0.0),
            QtCore.QPointF(0.0, 20.0),
            QtCore.QPointF(80.0, 20.0),
            QtCore.QPointF(80.0, 0.0)
        ])

        self.setParentItem(parent)
        self.posx, self.posy = posx, posy
        self.setPos(self.posx, self.posy)        
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
        self.setPos(self.posx, self.posy)

        scene = self.scene()
        buffer = self.parentItem()
        scenePos = buffer.mapToScene(self.pos())

        for view in scene.views():
            window = view.parent()
            window.packages_to_send.append(self) # Add package to window
            buffer.packages.remove(self) # Remove package from buffer object

            self.setParentItem(None)
            self.setPos(scenePos)
            self.posx = self.pos().x()
            self.posy = self.pos().y()

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
