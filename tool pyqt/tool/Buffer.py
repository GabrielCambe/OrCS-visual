from PyQt5 import QtWidgets, QtGui, QtCore

import Package


class BufferObject(QtWidgets.QGraphicsObject):
    def __init__(self, posx, posy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.polygon = QtGui.QPolygonF([
            QtCore.QPointF(0.0, 0.0),
            QtCore.QPointF(0.0, 610.0),
            QtCore.QPointF(200.0, 610.0),
            QtCore.QPointF(200.0, 0.0)
        ])
        self.setPos(posx, posy)

        self.packages = {}
        self.packageHistory = []

        self.penWidth = 2.0
        self.color = QtCore.Qt.blue

    def addInstruction(self, text):
        self.packages[text] = self.newPackage(text)
        self.packageHistory.append(text)

    def removeInstruction(self, text):
        scene = self.scene()
        scene.removeItem(self.packages[text])
        del self.packages[text]

    def getNewPackagePos(self):
        return { 'posx': 10.0, 'posy': 10.0 + (30.0 * len(self.packageHistory)) }

    def newPackage(self, text):
        return Package.PackageObject(text=text, parent=self, **self.getNewPackagePos())

    def mousePressEvent(self, event):
        self.color = QtCore.Qt.white

        scene = self.scene()
        newPos = self.getNewPackagePos()
        bufferPos = QtCore.QPointF(
            newPos['posx'],
            newPos['posy'],
        )
        scenePos = self.mapToScene(bufferPos)

        for view in scene.views():
            window = view.parent()
            for package in window.packages_to_send:
                window.packages_to_send.remove(package)
                self.packages["to_move"] = package

                self.anim = QtCore.QPropertyAnimation(package, b"pos")
                self.anim.setEndValue(scenePos)
                self.anim.setDuration(500)
                self.anim.finished.connect(lambda : self.setPackagePos(bufferPos, package))
                self.anim.start()
                
        self.update()

    def setPackagePos(self, bufferPos, package):
        package.setParentItem(self)
        package.setPos(bufferPos)
        package.posx = package.pos().x()
        package.posy = package.pos().y()

    def mouseReleaseEvent(self, event):
        self.color = QtCore.Qt.blue
        self.update()

    def boundingRect(self):
        return QtCore.QRectF(
            0.0 - self.penWidth / 2,
            0.0 - self.penWidth / 2,
            200.0 + self.penWidth,
            610.0 + self.penWidth
        )

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtCore.Qt.black, self.penWidth, QtCore.Qt.SolidLine))        
        painter.setBrush(QtGui.QBrush(self.color, QtCore.Qt.SolidPattern))
        painter.drawPolygon(self.polygon)
