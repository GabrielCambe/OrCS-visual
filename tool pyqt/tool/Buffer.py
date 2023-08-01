from PyQt5 import QtWidgets, QtGui, QtCore

import Package


class BufferObject(QtWidgets.QGraphicsWidget):
    def __init__(self, Name, Type, posx, posy, buffer_colors, orientation='', size='', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bufferType = Type

        self.setPos(posx, posy)

        self.penWidth = 2.0
        self.buffer_colors = buffer_colors
        self.color = buffer_colors[self.bufferType]
        
        if size == 'full':
            self.multiplier = 1.0
        else: 
            self.multiplier = 0.5

        self.orientation = orientation
        if orientation == 'vertical':
            if size == 'full':
                ysize = 480.0
                xsize = 200.0
            else: 
                ysize = 470.0 * self.multiplier
                xsize = 200.0

            self.polygon = QtGui.QPolygonF([
                QtCore.QPointF(0.0, 0.0),
                QtCore.QPointF(0.0, ysize),
                QtCore.QPointF(xsize, ysize),
                QtCore.QPointF(xsize, 0.0)
            ])
        else:
            self.polygon = QtGui.QPolygonF([
                QtCore.QPointF(0.0  * self.multiplier, 0.0),
                QtCore.QPointF(0.0  * self.multiplier, 40.0),
                QtCore.QPointF((410.0  * self.multiplier + 1.0), 40.0),
                QtCore.QPointF((410.0 * self.multiplier + 1.0), 0.0)
            ])

        self.packages = {}
        self.packageHistory = []

        self.layout = QtWidgets.QGraphicsGridLayout()
        self.layout.setVerticalSpacing(25.0)
        self.setLayout(self.layout)

        self.Name = Name
        self.textItem = QtWidgets.QGraphicsProxyWidget()
        self.textItem.setWidget(QtWidgets.QLabel(self.Name))
        self.textItem.widget().setStyleSheet(
            "background-color:transparent;\
            font-size: 13px;\
            font-family: Arial;\
            color: white;"
        )
        self.layout.addItem(self.textItem, 0, 0, QtCore.Qt.AlignAbsolute)


    def addPackage(self, Type, Id, Content, status_colors):
        self.packages[Id] = Package.PackageObject(Id, Type, Content, posx=0, posy=0, status_colors=status_colors)
        self.layout.addItem(self.packages[Id], len(self.packages), 0)
        self.packageHistory.append(Id)

    def removePackage(self, Id):
        scene = self.scene()
        scene.removeItem(self.packages[Id])
        del self.packages[Id]

    # def removePackage(self, Id):
    #     self.layout.removeItem(self.packages[Id])
    #     self.layout.activate()
    #     del self.packages[Id]

    def updatePackage(self, Id, Content):
        self.packages[Id].updateContent(Content)

    def moveInstruction(self, text, destBufferKey):
        package = self.packages[text]
        scenePos = self.mapToScene(package.pos())

        package.setParentItem(None)
        package.setPos(scenePos)
        package.posx = package.pos().x()
        package.posy = package.pos().y()

        print("startPos: ", scenePos)

        scene = package.scene()

        for view in scene.views():
            window = view.parent()
            destBuffer = window.buffers[destBufferKey]

            newPos = destBuffer.getNewPackagePos()
            destBufferPos = QtCore.QPointF(
                newPos['posx'],
                newPos['posy'],
            )
            destBufferScenePos = destBuffer.mapToScene(destBufferPos)
            print("endPos: ", destBufferScenePos)

            destBuffer.packages[text] = package
            destBuffer.packageHistory.append(text)
            
            self.anim = QtCore.QPropertyAnimation(package, b"pos")
            self.anim.setEndValue(destBufferScenePos)
            self.anim.setDuration(250)
            self.anim.finished.connect(lambda : destBuffer.setPackagePos(destBufferPos, package))
            self.anim.start()

        del self.packages[text]
        self.update()

    def mousePressEvent(self, event):
        self.color = QtCore.Qt.white

        # scene = self.scene()
        # newPos = self.getNewPackagePos()
        # bufferPos = QtCore.QPointF(
        #     newPos['posx'],
        #     newPos['posy'],
        # )
        # scenePos = self.mapToScene(bufferPos)

        # for view in scene.views():
        #     window = view.parent()
        #     for package in window.packages_to_send:
        #         window.packages_to_send.remove(package)
        #         self.packages["to_move"] = package

        #         self.anim = QtCore.QPropertyAnimation(package, b"pos")
        #         self.anim.setEndValue(scenePos)
        #         self.anim.setDuration(500)
        #         self.anim.finished.connect(lambda : self.setPackagePos(bufferPos, package))
        #         self.anim.start()
                
        self.update()

    def setPackagePos(self, bufferPos, package):
        package.setParentItem(self)
        package.setPos(bufferPos)
        package.posx = package.pos().x()
        package.posy = package.pos().y()

    def mouseReleaseEvent(self, event):
        self.color = self.buffer_colors[self.bufferType]
        self.update()

    def boundingRect(self):
        if self.orientation == 'vertical':
            return QtCore.QRectF(
                0.0 - self.penWidth / 2,
                0.0 - self.penWidth / 2,
                200.0 + self.penWidth,
                480.0 + self.penWidth
            )
        else:
            return QtCore.QRectF(
                0.0 - self.penWidth / 2,
                0.0 - self.penWidth / 2,
                410.0 + 1.0 + self.penWidth,
                40.0 + self.penWidth
            )

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtCore.Qt.black, self.penWidth, QtCore.Qt.SolidLine))        
        painter.setBrush(QtGui.QBrush(self.color, QtCore.Qt.SolidPattern))
        painter.drawPolygon(self.polygon)
