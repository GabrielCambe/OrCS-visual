import sys
from PyQt5 import QtWidgets, QtGui, QtCore

import Buffer

#TODO: implementar animação de um pacote sendo movido para outro
#TODO: pesquisar artgos sobre visualização de arquiteturas em software

class WindowWidget(QtWidgets.QMainWindow):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args,**kwargs)        

        self.setWindowTitle(title)
        self.setGeometry(QtGui.QGuiApplication.primaryScreen().availableGeometry())

        self.scene = QtWidgets.QGraphicsScene(
            self.geometry().x(),
            self.geometry().y(),
            self.geometry().width() * 0.7,
            self.geometry().height() * 0.7
        )
        self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.gray, QtCore.Qt.SolidPattern))

        self.buffers = [ Buffer.BufferObject(posx=10.0 + (210 * i), posy=10.0) for i in range(2) ]
        for buffer in self.buffers:
            self.scene.addItem(buffer)

        self.packages_to_send = []

        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setCentralWidget(self.view)

        self.grabKeyboard()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            print("Right")
        elif event.key() == QtCore.Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = WindowWidget(title='OrCS-visual')
    window.showMaximized()
    sys.exit(app.exec_())
