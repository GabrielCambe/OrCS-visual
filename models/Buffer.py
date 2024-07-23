import sys
import time
# import traceback

import matplotlib
import matplotlib.pyplot as plt


from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT
from matplotlib.backends.qt_compat import QtWidgets as MatPlotQtWidgets
from matplotlib.figure import Figure

import numpy as np

from PyQt5 import QtWidgets, QtGui, QtCore
from . import Package

class MyToolbar(NavigationToolbar2QT):
  def __init__(self, *args, **kwargs):
    NavigationToolbar2QT.__init__(self, *args, **kwargs)
    self.a = QtWidgets.QAction("Bye", self)
    self.a.setToolTip("GoodBye")
    self.a.triggered.connect(self.bye) 

  def bye(self):
    print ("See you next time")

class HistogramSubWindow(MatPlotQtWidgets.QMdiSubWindow):
    def __init__(self, _Id, _Name, buffer, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
       
        self._Id = _Id
        self.buffer = buffer

        self.setWindowTitle(f'{self.buffer._Name} - HISTOGRAMA')
        self.setGeometry(0, 0, int(self.parent().width()/7) , int(0.29 * self.parent().height()))
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.transparent)  
        self.icon = QtGui.QIcon(pixmap)
        self.setWindowIcon(self.icon) 

        self.save_in_settings = True


        self.matplotlib_widget = FigureCanvas(Figure(figsize=(int(self.width()/53), int(self.height()/53)), dpi=53))
        self.setWidget(self.matplotlib_widget)

        self._dynamic_ax = self.matplotlib_widget.figure.subplots()

        self.cycle = -1

        self.window = 500
        self.init_phases_plot()
        # self.init_histogram_plot()

        # Create a toolbar
        # self.toolbar = MyToolbar(self.matplotlib_widget, self)
        # self.toolbar = QtWidgets.QToolBar(self)

        # Set a layout for matplotlib_widget and add the toolbar to it0
        # layout = QtWidgets.QVBoxLayout()
        # layout.addWidget(self.toolbar)
        # self.matplotlib_widget.setLayout(layout)

        # Create an action (button)
        # self.plot_action = QtWidgets.QAction("Change Plot", self)
        # self.toolbar.addAction(self.plot_action)
        # self.plot_action.triggered.connect(self.toggle_plot) 

        self.phases_bars = []
        self.is_plot = True

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        print(f'You clicked on the window at coordinates: {event.x()}, {event.y()}')

        self.toggle_plot()

    def toggle_plot(self):
        self._dynamic_ax.clear()  # Clear the previous plot

        if self.plot_histogram:
            self.init_phases_plot()
            self.plot_phases_data()
        else:
            self.init_histogram_plot()
            self.plot_histogram_data()


    def init_phases_plot(self):
        self.setWindowTitle(f'{self.buffer._Name} - FASES')
        self.plot_histogram = False

        data = self.buffer.phases_data

        cycles = list(range(len(data)))
        self.bars = self._dynamic_ax.bar(cycles, data, width=1.0, align="center", color="royalblue")

        # seta os ticks do eixo y
        self._dynamic_ax.set_ylim([0, self.buffer.buffer_size])
        last = self.buffer.buffer_size
        step = int((self.buffer.buffer_size+1)/4)
        ticks = list(range(0, self.buffer.buffer_size, step if step != 0 else 1))
        if not last in ticks:
            if (last - ticks[-1]) <= int(step/2):
                ticks.pop(-1)
            ticks.append(self.buffer.buffer_size)
        self._dynamic_ax.set_yticks(ticks)

        # seta os ticks do eixo x
        self._dynamic_ax.set_xlim(-0.5, len(cycles)-0.5)
        last = len(cycles)
        ticks = np.linspace(0, last, num=len(cycles) if len(cycles) < 5 else 5, dtype=int)
        self._dynamic_ax.set_xticks(ticks)

    def init_histogram_plot(self):
        self.setWindowTitle(f'{self.buffer._Name} - HISTOGRAMA')
        self.plot_histogram = True

        data = self.buffer.occupancy_histogram_data

        positions = list(range(len(data[1])))
        counts = data[1]
        self.bars = self._dynamic_ax.bar(positions, counts, width=1.0, align="center", color="royalblue", ec="k")

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

    def plot_phases_data(self):
        data = self.buffer.phases_data
        new_cycle = self.cycle
        new_data = data[-1]

        new_bar = self._dynamic_ax.bar(new_cycle, new_data, width=1.0, align="center", color="royalblue")
        self.phases_bars.append(new_bar)
               
        if len(self.phases_bars) > self.window:
            self._dynamic_ax.clear()
            self._dynamic_ax.set_ylim([0, self.buffer.buffer_size])
            
            self.phases_bars.pop(0)
            for bar in self.phases_bars:
                self._dynamic_ax.add_patch(bar.get_children()[0])

            cycles = list(range(new_cycle - self.window +1, new_cycle + 1))
            self._dynamic_ax.set_xlim(cycles[0]-0.5, cycles[-1] + 0.5)
        else:
            cycles = list(range(new_cycle+1))
            self._dynamic_ax.set_xlim(-0.5, cycles[-1] + 0.5)

        # seta os ticks do eixo x
        last = cycles[-1]
        ticks = np.linspace(cycles[0], last, num=len(cycles) if len(cycles) < 5 else 5, dtype=int)
        self._dynamic_ax.set_xticks(ticks)

        self._dynamic_ax.figure.canvas.draw()

    def plot_histogram_data(self):
        data = self.buffer.occupancy_histogram_data
        current_cycle = data[0]
        positions = list(range(len(data[1])))
        counts = data[1]
        weigths = [0 if current_cycle == 0 else c/current_cycle for c in counts]

        if current_cycle >= 0:
            for bar, count in zip(self.bars.patches, weigths):
                bar.set_height(count)
            self._dynamic_ax.figure.canvas.draw()
    

    def closeEvent(self, event):
        self.matplotlib_widget.figure.clear()
        super().closeEvent(event)

    def setZoom(self, zoom_level):
        pass
        # # Apply zoom level to this subwindow
        # transform = QtGui.QTransform()
        # transform.scale(zoom_level, zoom_level)

        # self.widget().setTransform(transform)

    def plot(self, cycle):
        self.cycle = cycle
        
        if self.plot_histogram:
            self.plot_histogram_data()
        else:
            self.plot_phases_data()



class BufferSubWindow(QtWidgets.QMdiSubWindow):
    def __init__(self, _Id, _Name, _Type, buffers, BUFFER_TYPES, grid_geometry, window, save_in_settings=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        scene = QtWidgets.QGraphicsScene()
        buffers[_Id] = BufferObject(
            _Id, _Name, _Type,
            BUFFER_TYPES,
            grid_geometry,
            self.parent(),
            self
        )
        self.buffer = buffers[_Id]
        scene.addItem(buffers[_Id])
        view = QtWidgets.QGraphicsView()
        view.setBackgroundBrush(QtGui.QBrush(BUFFER_TYPES[_Type]['color'], QtCore.Qt.SolidPattern))
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
        self.is_plot = False

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

    def setZoom(self, zoom_level):
        # Apply zoom level to this subwindow
        transform = QtGui.QTransform()
        transform.scale(zoom_level, zoom_level)

        self.widget().setTransform(transform)

class BufferObject(QtWidgets.QGraphicsWidget):
    def __init__(self, _Id, _Name, _Type, BUFFER_TYPES, grid_geometry, mdi_area, mdi_sub_window, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._Id = _Id
        self._Name = _Name
        self._Type = _Type

        self.penWidth = 2.0
        self.BUFFER_TYPES = BUFFER_TYPES
        self.color = self.BUFFER_TYPES[self._Type]['color']
        self.is_container = self.BUFFER_TYPES[self._Type]['is_container']
        
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

        self.occupancy_histogram_data = [0, [int(0) for _ in range(self.buffer_size+1)]]
        self.phases_data = [0]

    def updateHistogramData(self, cycle, update_histogram=True):
        try:
            i = len(self.packages)
            self.occupancy_histogram_data[0] = cycle
            self.occupancy_histogram_data[1][i] += 1
            if len(self.phases_data) < cycle:
                self.phases_data.append(i)
            else:
                self.phases_data[cycle] = i

            if update_histogram:
                self.mdi_sub_window.histogram.plot(cycle)
        except Exception as e:
            # print(e)
            # traceback.print_exc()
            pass

    def clearHistogramData(self, cycle, update_histogram=True):
        try:
            self.occupancy_histogram_data = [0, [int(0) for _ in range(self.buffer_size+1)]]
            self.phases_data = [0]
            if update_histogram:
                self.mdi_sub_window.histogram.plot(cycle)
        except Exception as e:
            # print(e)
            # traceback.print_exc()
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

        try:
            freedPosition = self.packages[Id].position
            self.packages[Id].selectedChange.emit(False)
            
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
            # print("Warning: removePackage %s em %s" % (Id, self._Name))
            # traceback.print_exc()
            pass

        self.mdi_sub_window.setWindowTitle("%s %d/%d" % (self._Name[1:-1], len(self.packages), self.buffer_size))

    def updatePackage(self, _Id, _Content):
        # print(self._Name," updatePackage() ", _Id)
        
        try:
            self.packages[_Id].updateContent(_Content)
        except Exception as e:
            # print("Warning: updatePackage %s em %s" % (_Id, self._Name))
            # traceback.print_exc()
            pass

    def clearBuffer(self):
        keys = list(self.packages.keys())
        for key in keys:
            self.removePackage(key)
