from PyQt5 import QtWidgets, QtGui, QtCore

import Package


class BufferObject(QtWidgets.QGraphicsWidget):
    def __init__(self, Name, Type, buffer_colors, grid_geometry, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.Name = Name
        self.bufferType = Type

        self.penWidth = 2.0
        self.buffer_colors = buffer_colors
        self.color = buffer_colors[self.bufferType]
        
        self.packages = {}
        self.packageHistory = []

        self.layout = QtWidgets.QGraphicsGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(15.0)

        self.buffer_width = int(grid_geometry[0])
        self.buffer_size = int(grid_geometry[1])

        # for j in range(0, self.buffer_width):
        #     self.layout.setColumnStretchFactor(j, 0)
        #     self.layout.setColumnFixedWidth(j, 30.0)

        self.sub_window = None


    def addPackage(self, Type, Id, Content, status_colors):
        self.packageHistory.append(Id)

        column_size = self.buffer_width
        row_size = self.buffer_size // self.buffer_width
        if self.buffer_size % self.buffer_width != 0:
            row_size = row_size + 1

        # _id = int(Id[1:-1])
        _id = len(self.packageHistory)
        grid_position = (
            (_id - 1) // column_size % row_size,
            (_id - 1) % column_size
        )

        self.packages[Id] = Package.PackageObject(Id, Type, Content, status_colors=status_colors, parent=self)
        self.layout.addItem(self.packages[Id], *grid_position)
        for i in range(0, self.layout.rowCount() - 1):
            self.layout.setRowStretchFactor(i, 0)
            self.layout.setRowFixedHeight(i, 20.0)
        self.layout.setRowStretchFactor(self.layout.rowCount() - 1, 1)
        

    def removePackage(self, Id):
        scene = self.scene()
        scene.removeItem(self.packages[Id])
        del self.packages[Id]

    def updatePackage(self, Id, Content):
        self.packages[Id].updateContent(Content)

    def mousePressEvent(self, event):
        self.color = QtCore.Qt.white
        self.update()

    def mouseReleaseEvent(self, event):
        self.color = self.buffer_colors[self.bufferType]
        self.update()

    def boundingRect(self):
        return QtCore.QRectF(
            self.geometry().x(),
            self.geometry().y(),
            self.geometry().width(),
            self.geometry().height()
        )

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtCore.Qt.black, self.penWidth, QtCore.Qt.SolidLine))        
        painter.setBrush(QtGui.QBrush(self.color, QtCore.Qt.SolidPattern))
        painter.drawRect(self.boundingRect())
