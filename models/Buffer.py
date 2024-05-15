import sys
import time

import matplotlib
import matplotlib.pyplot as plt


from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.qt_compat import QtWidgets as MatPlotQtWidgets
from matplotlib.figure import Figure

import numpy as np

from PyQt5 import QtWidgets, QtGui, QtCore
from . import Package

class HistogramSubWindow(MatPlotQtWidgets.QMdiSubWindow):
    def __init__(self, _Id, _Name, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
       
        self._Id = _Id
        self.setWindowTitle(_Name)
        self.setGeometry(0, 0, int(self.parent().width()/7) , int(0.29 * self.parent().height()))
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint)
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.transparent)  
        self.icon = QtGui.QIcon(pixmap)
        self.setWindowIcon(self.icon) 

        self.save_in_settings = True

        self.matplotlib_widget = FigureCanvas(Figure(figsize=(6, 4), dpi=60))
        self.setWidget(self.matplotlib_widget)

        self._dynamic_ax = self.matplotlib_widget.figure.subplots()

        positions = list(range(len(data[1])))
        counts = data[1]
        self.bars = self._dynamic_ax.bar(positions, counts, width=1.0, align="center")

        # seta os ticks do eixo y
        self._dynamic_ax.set_ylim([0.0,1.0])
        self._dynamic_ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])

        # seta os ticks do eixo x
        self._dynamic_ax.set_xlim(-0.5, len(positions)-0.5)
        last = len(positions)-1
        step = int((len(positions)+1)/4)
        ticks = list(range(0, len(positions), step if step != 0 else 1))
        if not last in ticks:
            if (last - ticks[-1]) <= int(step/2):
                ticks.pop(-1)
            ticks.append(len(positions)-1)
        self._dynamic_ax.set_xticks(ticks)

        self.is_histogram = True

    def closeEvent(self, event):
        self.matplotlib_widget.figure.clear()
        super().closeEvent(event)

    def plot(self, data):
        current_cycle = data[0]
        positions = list(range(len(data[1])))
        counts = data[1]
        weigths = [c/current_cycle for c in counts]

        if current_cycle >= 0:
            for bar, count in zip(self.bars.patches, weigths):
                bar.set_height(count)
            self._dynamic_ax.figure.canvas.draw()

class BufferSubWindow(QtWidgets.QMdiSubWindow):
    def __init__(self, _Id, _Name, _Type, buffers, BUFFER_COLORS, grid_geometry, window, is_container=False, save_in_settings=False, *args, **kwargs):
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
        self.setGeometry(0, 0, int(self.parent().width()/7) , int(0.7 * self.parent().height()))
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint)
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.transparent)  
        self.icon = QtGui.QIcon(pixmap)
        self.setWindowIcon(self.icon) 

        self.save_in_settings = save_in_settings
        self.is_histogram = False

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
        self.position = 0

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

        self.occupancy_histogram_data = [0, [int(0) for _ in range(self.buffer_size+1)]]

    def updateHistogramData(self, cycle):
        i = len(self.packages)
        self.occupancy_histogram_data[0] = cycle
        self.occupancy_histogram_data[1][i] += 1 
        try:
            self.mdi_sub_window.histogram.plot(self.occupancy_histogram_data)
        except Exception as e:
            pass

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
            ((package.position) // self.column_size) % self.row_size,
            (package.position) % self.column_size
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
                        scene.removeItem(package)
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
