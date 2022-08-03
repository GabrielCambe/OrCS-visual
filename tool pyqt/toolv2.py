import sys

from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLabel
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon, QColor


class PackageWidget(QWidget):
    def __init__(self, posx, posy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(posx, posy, 80, 20)

        self.label = QLabel(self)
        self.label.setText("posy %s" % posy)
        self.label.setStyleSheet('color:white;padding:0 20;background-color:red;')

class BufferWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(10, 10, 200, 300)
        self.frame = QFrame(self)
        self.frame.setGeometry(10, 10, 200, 300)
        self.frame.setStyleSheet('background-color:blue;')

        self.packages = [
            PackageWidget(parent=self.frame, posx=10, posy=10),
            PackageWidget(parent=self.frame, posx=10, posy=31),
            PackageWidget(parent=self.frame, posx=10, posy=52),
            PackageWidget(parent=self.frame, posx=10, posy=73)
        ]

class Window(QWidget):
    def __init__(self, width, height, title, *args, **kwargs):
        self.app = QApplication(sys.argv)

        super().__init__(*args,**kwargs)        
        self.setWindowTitle(title)
        self.setGeometry(0, 0, width, height)

        BufferWidget(parent=self)

    def run(self):
        self.show()
        sys.exit(self.app.exec_())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    window = Window(
        width=1280,
        height=720, 
        title="OrCS-visual", 
    )    
    window.run()
