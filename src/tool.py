import sys
from PyQt5 import QtWidgets

from Window import Visualizer

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    orcs_visualizer = Visualizer(title='OrCS Architecture Viualizer')
    orcs_visualizer.showMaximized()
    sys.exit(app.exec_())
