import json
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

    def __init__(self, Id, Type, Content, STATUS_COLORS, mdi_area, position, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Package Data
        split = Content[1:-1].split(',')
        Status = split[0]
        Uop = split[1]
        Operation = split[2]

        self.STATUS_COLORS = STATUS_COLORS
        
        self._Id = Id
        self._Type = Type
        self._fillColor = self.STATUS_COLORS[Status]

        # SubWindow Data
        self._mdiArea = mdi_area
        self.title = "%s: %s" %  (self._Type, self._Id)
        self.content = str({"asm": Uop})
        self.sub_window = None

        # Package Label
        self.text_widgets = {}
        
        self.text_Id = "%s" % (self._Id[1:-1]) if Operation == 'null' else "%s|%s" % (Operation, self._Id[1:-1])
        if len(self.text_Id) > 2:
            self.display_text = "...%s" % self._Id[1:-1][-2:]
        else:
            self.display_text = self._Id[1:-1][-2:]
        
        self.text_widgets["text"] = QtWidgets.QGraphicsProxyWidget(self)
        self.text_widgets["text"].setWidget(QtWidgets.QLabel(self.display_text))
        self.text_widgets["text"].widget().setGeometry(0.0, 0.0, 0.0, 0.0)  
        self.text_widgets["text"].widget().setStyleSheet("font-size: 12px; color: white; background-color: transparent;")
        self.text_widgets["text"].widget().setAlignment(QtCore.Qt.AlignCenter)

        self.text_Id_width = self.stringWidth(self.text_Id) + 10.0
        self.display_text_width = self.stringWidth("000") + 10.0

        # Widget Geometry
        self.setGeometry(
            0.0, 0.0,
            self.display_text_width, 15.0
        )
        self.bounding_rect = QtCore.QRectF(0.0, 0.0, 0.0, 0.0)
        self.setMinimumSize(self.display_text_width, 15.0)
        
        # Drawing Settings
        # self.bounding_box = None
        self.render = False
        self.penWidth = 1.0
        self.penColor = QtCore.Qt.black
        self.oldZvalue = 0.0

        # Package Widget Configuration
        self.setAcceptHoverEvents(True)
        self.selectedChange.connect(self.handleSelected)
        self.is_Selected = False

        self.position = position

    def printGeometry(self):
        print(
            self.geometry().x(),
            self.geometry().y(),
            self.geometry().width(),
            self.geometry().height()
        )

    def stringWidth(self, text):
        return self.text_widgets["text"].widget().fontMetrics().width(text)

    @QtCore.pyqtSlot(bool, name="selectedChange")
    def handleSelected(self, isSelected):
        self.is_Selected = isSelected
        if isSelected:
            # self.bounding_box.setPen(QtCore.Qt.yellow)
            self.penColor = QtCore.Qt.yellow

            container = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout()

            for key, value in eval(self.content).items():
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

            self.sub_window = CustomQMdiSubWindow(
                self.title, container,
                closed_callback=lambda: self.selectedChange.emit(False)
            )
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.sub_window.setParent(self._mdiArea)
            self.sub_window.show()

        else:
            # self.bounding_box.setPen(QtCore.Qt.black)
            self.penColor = QtCore.Qt.black

            if self.sub_window != None:
                self.sub_window.close()
                self.sub_window = None

        self.update()

    def updateContent(self, Content):
        split = Content[1:-1].split(',')
        Status = split[0]
        Uop = split[1]
        Operation = split[2]

        self._fillColor = self.STATUS_COLORS[Status]
        self.content = str({"asm": Uop})

        self.update()

    def resizeEvent(self, event):
        try:
            if self.render == False:
                self.text_widgets["text"].widget().setGeometry(
                    0.0, 0.0,
                    self.display_text_width, 15.0
                )  
                self.bounding_rect = QtCore.QRectF(
                    0.0, 0.0,
                    self.display_text_width, 15.0
                )
                # self.bounding_box = QtWidgets.QGraphicsRectItem(0.0, 0.0, 30.0, 15.0, parent=self)
                # self.bounding_box.setPen(QtCore.Qt.black)
                # self.bounding_box.setPen(QtCore.Qt.white)

                self.render = True
        except Exception:
            pass
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if self.is_Selected == False:
            self.selectedChange.emit(True)
        else:
            self.selectedChange.emit(False)
        event.accept()

    def hoverEnterEvent(self, event):
        self.text_widgets["text"].widget().setText(self.text_Id)
        self.text_widgets["text"].widget().setGeometry(
            0.0, 0.0,
            self.text_Id_width, 15.0
        )
        xDelta = (self.text_Id_width - self.display_text_width) / 2
        self.setGeometry(
            self.geometry().x() - xDelta, self.geometry().y(),
            self.text_Id_width, 15.0
        )
        self.bounding_rect = QtCore.QRectF(
            0.0, 0.0,
            self.text_Id_width, 15.0
        )       
        self.penColor = QtCore.Qt.white        
        self.oldZvalue = self.zValue()
        self.setZValue(self.oldZvalue + 1000.0)


        # self.animation = QtCore.QPropertyAnimation(self, b"geometry")
        # self.animation.setStartValue(self.geometry())
        # self.animation.setEndValue(self.geometry().adjusted(0, 0, +20.0, +20.0))
        # self.animation.setDuration(150)
        # self.animation.start(QtCore.QPropertyAnimation.DeleteWhenStopped)

        self.update()

        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.text_widgets["text"].widget().setText(self.display_text)
        self.text_widgets["text"].widget().setGeometry(
            0.0, 0.0,
            self.display_text_width, 15.0
        )
        xDelta = (self.text_Id_width - self.display_text_width) / 2
        self.setGeometry(
            self.geometry().x() + xDelta, self.geometry().y(),
            self.display_text_width, 15.0
        )
        self.bounding_rect = QtCore.QRectF(
            0.0, 0.0,
            self.display_text_width, 15.0
        )
        if not self.is_Selected:
            self.penColor = QtCore.Qt.black
        self.setZValue(self.oldZvalue)

        # self.animation = QtCore.QPropertyAnimation(self, b"geometry")
        # self.animation.setStartValue(self.geometry())
        # self.animation.setEndValue(self.geometry().adjusted(0, 0, +20.0, +20.0))
        # self.animation.setDuration(150)
        # self.animation.start(QtCore.QPropertyAnimation.DeleteWhenStopped)

        self.update()

        super().hoverLeaveEvent(event)

    # Defines the area wheere the widget can be clicked
    def boundingRect(self):
        return self.bounding_rect

    def paint(self, painter, option, widget):
        painter.setPen(
            QtGui.QPen(
                self.penColor,
                self.penWidth,
                QtCore.Qt.SolidLine
            )
        )
        painter.setBrush(
            QtGui.QBrush(
                self._fillColor,
                QtCore.Qt.SolidPattern
            )
        )

        # self.bounding_box.setPen(QtCore.Qt.red)

        if self.render == True:
            painter.drawRect(self.bounding_rect)

        super().paint(painter, option, widget)
