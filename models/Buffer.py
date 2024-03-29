from PyQt5 import QtWidgets, QtGui, QtCore
from . import Package


class CustomQMdiSubWindow(QtWidgets.QMdiSubWindow):
    def __init__(self, _Id, _Name, _Type, buffers, BUFFER_COLORS, grid_geometry, is_container=False, save_in_settings=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        scene = QtWidgets.QGraphicsScene()
        buffers[_Id] = BufferObject(
            _Id, _Name, _Type,
            BUFFER_COLORS,
            grid_geometry,
            self.parent(),
            self,
            is_container=is_container
        )
        self.buffer = buffers[_Id]
        scene.addItem(buffers[_Id])
        view = QtWidgets.QGraphicsView()
        view.setBackgroundBrush(QtGui.QBrush(BUFFER_COLORS[_Type], QtCore.Qt.SolidPattern))
        view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setWidget(view)        
        self.widget().setScene(scene)
        
        self.setWindowTitle("%s %d/%d" % (_Name[1:-1], 0, grid_geometry[1]))
        self.setGeometry(0, 0, int(self.parent().width()/7) , self.parent().height())
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint)
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.transparent)  
        self.icon = QtGui.QIcon(pixmap)
        self.setWindowIcon(self.icon) 

        self.save_in_settings = save_in_settings

    def contextMenuEvent(self, event):
        event.ignore()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.widget().setGeometry(self.childrenRect())
        self.buffer.setGeometry(
            0.0, 0.0,
            float(self.childrenRect().width()),
            float(self.childrenRect().height())
        )
        self.update()
        

class BufferObject(QtWidgets.QGraphicsWidget):
    def __init__(self, _Id, _Name, _Type, buffer_colors, grid_geometry, mdi_area, mdi_sub_window, is_container, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._Id = _Id
        self._Name = _Name
        self._Type = _Type

        self.penWidth = 2.0
        self.buffer_colors = buffer_colors
        self.color = buffer_colors[self._Type]
        
        self.packages = {}
        self.position = 1

        self.layout = QtWidgets.QGraphicsGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(5.0)

        self.buffer_width = grid_geometry[0]
        self.buffer_size = grid_geometry[1]

        self.mdi_area = mdi_area
        self.mdi_sub_window = mdi_sub_window

        self.column_size = self.buffer_width
        self.row_size = self.buffer_size // self.buffer_width
        if self.buffer_size % self.buffer_width != 0:
            self.row_size = self.row_size + 1

        self.is_container = is_container


    def addPackage(self, _Type, _Id, _Content, STATUS_COLORS):
        # print(self._Name," addPackage() ", _Id)

        self.packages[_Id] = Package.PackageObject(
            _Id, _Type, _Content, STATUS_COLORS,
            self.mdi_area, self.position,
            parent=self
        )

        self.addToLayout(self.packages[_Id])
        self.position = self.position + 1

        self.mdi_sub_window.setWindowTitle("%s %d/%d" % (self._Name[1:-1], len(self.packages), self.buffer_size))
    
    def addToLayout(self, package):
        grid_position = (
            ((package.position - 1) // self.column_size) % self.row_size,
            (package.position - 1) % self.column_size
        )
        self.layout.addItem(package, *grid_position)
        for i in range(0, self.layout.rowCount() - 1):
            self.layout.setRowStretchFactor(i, 0)
            self.layout.setRowFixedHeight(i, 20.0)
        self.layout.setRowStretchFactor(self.layout.rowCount() - 1, 1)

    def removeFromLayout(self, package):
        self.layout.removeItem(package)

    def removePackage(self, Id):
        # print(self._Name," removePackage() ", Id)
        scene = self.scene()

        freedPosition = self.packages[Id].position
        self.packages[Id].selectedChange.emit(False)

        try:
            scene.removeItem(self.packages[Id])
            del self.packages[Id]

            if self.is_container:
                for packageKey in self.packages:
                    package = self.packages.get(packageKey)
                    if package.position > freedPosition:
                        # print("%s: " % package._Id, package.position, freedPosition)
                        scene.removeItem(package)
                        # self.removeFromLayout(package)
                        package.position = package.position - 1
                        self.addToLayout(package)
                        self.update()

                self.position = self.position - 1

        except Exception as e:
            print("Warning: removePackage %s em %s" % (Id, self._Name))

        self.mdi_sub_window.setWindowTitle("%s %d/%d" % (self._Name[1:-1], len(self.packages), self.buffer_size))

    def updatePackage(self, _Id, _Content):
        # print(self._Name," updatePackage() ", _Id)
        
        try:
            self.packages[_Id].updateContent(_Content)
        except Exception as e:
            print("Warning: updatePackage %s em %s" % (_Id, self._Name))
