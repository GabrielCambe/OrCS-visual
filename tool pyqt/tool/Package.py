from PyQt5 import QtWidgets, QtGui, QtCore

OperationPackage = '"OperationPackage"'
UopPackage = '"UopPackage"'

PACKAGE_STATE_FREE = 'PACKAGE_STATE_FREE' 
PACKAGE_STATE_WAIT = 'PACKAGE_STATE_WAIT'
PACKAGE_STATE_READY = 'PACKAGE_STATE_READY'

class PackageObject(QtWidgets.QGraphicsWidget):
    def __init__(self, Id, Type, Content, posx, posy, status_colors, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if Type == OperationPackage:
            pass
        elif Type == UopPackage:
            pass

        split = Content[1:-1].split(',')
        Status = split[0]
        Uop = split[1]
        Operation = split[2]

        self.text = "%s" % (Id[1:-1]) if Operation == 'null' else "%s - %s: %s" % (Operation, Id[1:-1], Uop)

        self.posx, self.posy = posx, posy
        self.setGeometry(self.posx, self.posy, 180.0, 20.0)  
        self.penWidth = 1.0

        self.polygon = QtGui.QPolygonF(
            self.geometry()
        )

        self.status_colors = status_colors
        self.color = self.status_colors[Status]

        self.textItem = QtWidgets.QGraphicsTextItem()
        self.textItem.setParentItem(self)
        self.textItem.setDefaultTextColor(QtCore.Qt.white)
        self.textItem.setTextWidth(self.boundingRect().width())
        self.textItem.setHtml("<div style=\"text-align:center;\"> %s </div>" % self.text)

        self.setAcceptHoverEvents(True)

    def updateContent(self, Content):
        split = Content[1:-1].split(',')
        Status = split[0]
        Uop = split[1]
        Operation = split[2]

        self.color = self.status_colors[Status]

        self.update()

    def mousePressEvent(self, event):
        self.color = QtCore.Qt.white
        # self.setPos(self.posx, self.posy)

        # scene = self.scene()
        # buffer = self.parentItem()
        # scenePos = buffer.mapToScene(self.pos())

        # for view in scene.views():
        #     window = view.parent()
        #     window.packages_to_send.append(self) # Add package to window
        #     buffer.packages.remove(self) # Remove package from buffer object

        #     self.setParentItem(None)
        #     self.setPos(scenePos)
        #     self.posx = self.pos().x()
        #     self.posy = self.pos().y()

        self.update()

    def mouseReleaseEvent(self, event):
        self.color = QtCore.Qt.red
        self.update()

    def hoverEnterEvent(self, event):
        if self.parentItem() != None:
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
        if self.parentItem() != None:
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
            180.0 + self.penWidth,
            20.0 + self.penWidth
        )

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtCore.Qt.black,  self.penWidth, QtCore.Qt.SolidLine))        
        painter.setBrush(QtGui.QBrush(self.color, QtCore.Qt.SolidPattern))
        painter.drawPolygon(self.polygon)
