from PyQt5 import QtWidgets, QtGui, QtCore

OperationPackage = '"OperationPackage"'
UopPackage = '"UopPackage"'

PACKAGE_STATE_FREE = 'PACKAGE_STATE_FREE' 
PACKAGE_STATE_WAIT = 'PACKAGE_STATE_WAIT'
PACKAGE_STATE_READY = 'PACKAGE_STATE_READY'

class CustomQMdiSubWindow(QtWidgets.QMdiSubWindow):
    def __init__(self, title, widget, closed_callback=None, save_in_settings=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.setWindowTitle(title)
        self.setWidget(widget)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.transparent)  
        self.icon = QtGui.QIcon(pixmap)
        self.setWindowIcon(self.icon) 

        self.closed_callback = closed_callback
        self.save_in_settings = save_in_settings

    def contextMenuEvent(self, event):
        event.reject()

    def closeEvent(self, event):
        if self.closed_callback != None:
            self.closed_callback()
        super().closeEvent(event)


class PackageObject(QtWidgets.QGraphicsWidget):
    selectedChange = QtCore.pyqtSignal(bool, name="selectedChange")

    def __init__(self, Id, Type, Content, status_colors, mdi_area, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selectedChange.connect(self.handleSelected)

        split = Content[1:-1].split(',')
        Status = split[0]
        Uop = split[1]
        Operation = split[2]

        if Type == OperationPackage:
            self.setGeometry(0, 0, 30.0, 20.0)
        elif Type == UopPackage:
            self.setGeometry(0, 0, 40.0, 20.0)

        self.title = "%s: %s" %  (Type, Id)
        self.content = "asm: %s\t" % Uop

        self.penWidth = 1.0
        self.polygon = QtGui.QPolygonF(self.geometry())

        self.status_colors = status_colors
        self.color = self.status_colors[Status]
        self.oldColor = None

        self.text_widgets = {}
        self.text = "%s" % (Id[1:-1]) if Operation == 'null' else "%s|%s" % (Operation, Id[1:-1])

        self.text_widgets["text"] = QtWidgets.QGraphicsProxyWidget(self)
        self.text_widgets["text"].setWidget(QtWidgets.QLabel(self.text))
        self.text_widgets["text"].widget().setGeometry(
            self.geometry().x(),
            self.geometry().y(),
            self.geometry().width(),
            self.geometry().height()
        )  
        self.text_widgets["text"].widget().setStyleSheet("font-size: 12px; color: white; background-color: transparent;")
        # self.text_widgets["text"].setAlignment(QtCore.Qt.AlignCenter)
        self.text_widgets["text"].widget().setAlignment(QtCore.Qt.AlignCenter)


        # Create a bounding box item to visualize the widget's geometry
        self.bounding_box = QtWidgets.QGraphicsRectItem(self.geometry(), parent=self)
        self.bounding_box.setPen(QtCore.Qt.black)  # Set the pen color

        self.mdi_area = mdi_area

        self.setAcceptHoverEvents(True)

    @QtCore.pyqtSlot(bool, name="selectedChange")
    def handleSelected(self, isSelected):
        if isSelected:
            self.bounding_box.setPen(QtCore.Qt.yellow)
        else:
            self.bounding_box.setPen(QtCore.Qt.black)
        
        self.update()
        # def changeColor(self):
        #     self.oldColor = self.color
        #     self.color = color
        # def restoreColor(self):
        #     self.color = self.oldColor
        #     self.update()


    def updateContent(self, Content):
        split = Content[1:-1].split(',')
        Status = split[0]
        Uop = split[1]
        Operation = split[2]

        self.color = self.status_colors[Status]
        self.content = "asm: %s\t" % Uop

        self.update()

    def mousePressEvent(self, event):
        self.selectedChange.emit(True)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        dictionary = {
            "content": self.content,
        }

        for key, value in dictionary.items():
            key_label = QtWidgets.QLabel(key)
            value_frame = QtWidgets.QFrame()
            value_label = QtWidgets.QLabel(str(value))

            # Style the value frame (you can customize this)
            value_frame.setFrameShape(QtWidgets.QFrame.Box)
            value_frame.setLineWidth(1)

            value_layout = QtWidgets.QVBoxLayout()
            value_layout.addWidget(value_label)
            value_frame.setLayout(value_layout)

            layout.addWidget(key_label)
            layout.addWidget(value_frame)

        container.setLayout(layout)

        sub_window = CustomQMdiSubWindow(self.title, container, closed_callback=lambda: self.selectedChange.emit(False))
        sub_window.setParent(self.mdi_area)
        sub_window.show()

        event.accept()

        

    # def hoverEnterEvent(self, event):
    #     # if self.parentItem() != None:
    #     #     self.anim = QtCore.QPropertyAnimation(self, b"pos")
    #     #     self.anim.setEndValue(
    #     #         QtCore.QPointF(
    #     #             self.pos().x() + 5.0,
    #     #             self.pos().y()
    #     #         )
    #     #     )
    #     #     self.anim.setDuration(50)
    #     #     self.anim.start()
    #     print("Mouse entered the widget")
    #     super().hoverEnterEvent(event)setWindowTitle
    #     # if self.parentItem() != None:
    #     #     self.anim = QtCore.QPropertyAnimation(self, b"pos")
    #     #     self.anim.setEndValue(
    #     #         QtCore.QPointF(
    #     #             self.pos().x() - 5.0,
    #     #             self.pos().y()
    #     #         )
    #     #     )
    #     #     self.anim.setDuration(50)
    #     #     self.anim.start()
    #     print("Mouse left the widget")
    #     super().hoverLeaveEvent(event)

    # def itemChange(self, change, value):
    #     print("change: ", change)
    #     return super().itemChange(change, value)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, 30.0, 20.0)

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtCore.Qt.black,  self.penWidth, QtCore.Qt.SolidLine))        
        painter.setBrush(QtGui.QBrush(self.color, QtCore.Qt.SolidPattern))
        painter.drawPolygon(self.polygon)
        super().paint(painter, option, widget)
