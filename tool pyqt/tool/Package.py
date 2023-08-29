from PyQt5 import QtWidgets, QtGui, QtCore

OperationPackage = '"OperationPackage"'
UopPackage = '"UopPackage"'

PACKAGE_STATE_FREE = 'PACKAGE_STATE_FREE' 
PACKAGE_STATE_WAIT = 'PACKAGE_STATE_WAIT'
PACKAGE_STATE_READY = 'PACKAGE_STATE_READY'

class PackageObject(QtWidgets.QGraphicsWidget):
    selectedChange = QtCore.pyqtSignal(bool, name="selectedChange")

    def __init__(self, Id, Type, Content, status_colors, *args, **kwargs):
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

        # Create and show a QMessageBox without an icon
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.NoIcon)
        msg_box.setWindowTitle(self.title)
        msg_box.setText(self.content)
        msg_box.finished.connect(lambda: self.selectedChange.emit(False))
        msg_box.exec_()

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
    #     super().hoverEnterEvent(event)

    # def hoverLeaveEvent(self, event):
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
