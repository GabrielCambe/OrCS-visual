import sys

from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon


class FileReader():
    def __init__(self, file_path):
        self.file_path = file_path
        self.current_line = ''
        self.open_file()

    def open_file(self):
        self.file = open(self.file_path, 'r')

    def get_line(self):
        self.current_line = self.file.readline()
        if self.current_line == '':
            return None
        else:
            return self.current_line

    def close_file(self):
        self.file.close()


class TriangleWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(0, 0, 50, 50)

        # anti-clockwise beginning on top side
        self.points = [
            QPoint(0, 0),
            QPoint(0, 100),
            QPoint(100, 100)
        ]
        self.poly = QPolygon(self.points)

    def paintEvent(self, event):
        self.painter = QPainter(self)
        # Line thickness
        self.painter.setPen(QPen(Qt.black,  1, Qt.SolidLine))        
        # Fill pattern
        self.painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        self.painter.drawPolygon(self.poly)
        self.painter.end()


class Window(QWidget):
    def __init__(self, width, height, title, *args, **kwargs):
        self.app = QApplication(sys.argv)

        self.title = title
        self.width, self.height = (width, height)
        self.background_color = (127,127,127)
        self.running = False

        super().__init__(*args,**kwargs)
        
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.width, self.height)

        self.shapes = {}
        self.file_reader = FileReader("/home/gabriel/Documentos/HiPES/OrCS-visual/commands.txt")
        # self.file_reader = FileReader("/home/gabriel/Documents/OrCS-visual/tool/commands.txt")

        # self.resize(600, 600)
        # self.child.setStyleSheet("background-color:red;border-radius:15px;")
        
    def run(self):
        self.show()
        # for child in self.children():
        #     child.show() 
        sys.exit(self.app.exec_())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.file_reader.get_line()
                
            current_line = self.file_reader.current_line.strip()
            print(current_line)

            if current_line == "spawn triangle as t1":
                self.shapes["triangle_widget"] = TriangleWidget(parent=self)
                self.shapes["triangle_widget"].show()

            if current_line == "move t1 right":
                self.anim = QPropertyAnimation(self.shapes["triangle_widget"], b"pos")
                self.anim.setEndValue(QPoint(200, 0))
                self.anim.setDuration(1500)
                self.anim.start()

            if current_line == "move t1 left":
                self.anim = QPropertyAnimation(self.shapes["triangle_widget"], b"pos")
                self.anim.setEndValue(QPoint(0, 0))
                self.anim.setDuration(1500)
                self.anim.start()

            elif current_line == "delete t1":
                self.shapes["triangle_widget"].close()

            elif current_line == "":
                self.close()

        elif event.key() == Qt.Key_Escape:
            self.close()

        self.update()

    def paintEvent(self, event):
        shape = self.shapes.get("triangle", None)
        if shape:
            shape.draw()


if __name__ == "__main__":
    window = Window(
        width=640,
        height=360, 
        title="OrCS-visual", 
    )    
    window.run()
