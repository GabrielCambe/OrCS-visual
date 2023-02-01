from PyQt5 import QtWidgets, QtGui, QtCore

import Package


class BufferObject(QtWidgets.QGraphicsObject):
    def __init__(self, posx, posy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.polygon = QtGui.QPolygonF([
            QtCore.QPointF(0.0, 0.0),
            QtCore.QPointF(0.0, 300.0),
            QtCore.QPointF(200.0, 300.0),
            QtCore.QPointF(200.0, 0.0)
        ])
        self.setPos(posx, posy)

        # self.newPackagePos = self.getNewPackagePos()            
        # self.packages = [ self.newPackage() for i in range(4) ]
        self.packages = []
        for i in range(4):
            self.packages.append(self.newPackage())

        self.penWidth = 2.0
        self.color = QtCore.Qt.blue

    # def getNewPackagePos(self, bufferPos={}):
    #     i = 0
    #     while True:
    #         yield { 'posx': 10.0, 'posy': 10.0 + (30 * i) }
    #         i = i + 1

    def getNewPackagePos(self):
        i = 0
        while True:
            posy = 10.0 + (30 * i)

            if len(self.packages) == 0:
                return { 'posx': 10.0, 'posy': posy }

            for package in self.packages:
                if package.posy != posy:
                    print(package.posy, posy)
                    return { 'posx': 10.0, 'posy': posy }

            i = i + 1

    def newPackage(self):
        # return Package.PackageObject(parent=self, **next(self.newPackagePos))
        return Package.PackageObject(parent=self, **self.getNewPackagePos())

    def mousePressEvent(self, event):
        self.color = QtCore.Qt.white

        scene = self.scene()
        # newPos = next(self.newPackagePos)
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
                self.packages.append(package)

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
            300.0 + self.penWidth
        )

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtCore.Qt.black, self.penWidth, QtCore.Qt.SolidLine))        
        painter.setBrush(QtGui.QBrush(self.color, QtCore.Qt.SolidPattern))
        painter.drawPolygon(self.polygon)
