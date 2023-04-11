from PyQt5 import QtWidgets, QtGui, QtCore

import Buffer

class WindoWidget(QtWidgets.QMainWindow):
    def __init__(self, title, parser, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self.parser = parser

        self.setWindowTitle(title)
        self.setGeometry(QtGui.QGuiApplication.primaryScreen().availableGeometry())

        self.scene = QtWidgets.QGraphicsScene(
            self.geometry().x(),
            self.geometry().y(),
            self.geometry().width() * 0.7,
            self.geometry().height() * 0.7
        )
        self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.gray, QtCore.Qt.SolidPattern))

        # self.buffers = []
        self.buffers = {}
        self.packages_to_send = []

        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setCentralWidget(self.view)

        self.grabKeyboard()

        if self.parser.mode == 'CYCLE':
            self.cycle = -1
            self.textItem = QtWidgets.QGraphicsTextItem()
            self.textItem.setPos(
                self.geometry().width() * 0.9,
                self.geometry().height() * 0.9
            )
            self.textItem.setDefaultTextColor(QtCore.Qt.red)
            self.textItem.setHtml("<div style=\"text-align:bottom;\"> %s </div>" % self.cycle)
            self.scene.addItem(self.textItem)        

        self.textItem2 = QtWidgets.QGraphicsTextItem()
        self.textItem2.setPos(
            self.geometry().width() - 100,
            self.geometry().height() * 0.9
        )
        self.textItem2.setDefaultTextColor(QtCore.Qt.red)
        self.textItem2.setHtml("<div style=\"text-align:bottom;\"> %s </div>" % self.parser.mode)
        self.scene.addItem(self.textItem2)        



    def addBuffer(self, key):
        buffer = Buffer.BufferObject(posx=10.0 + (210 * len(self.buffers)+1), posy=10.0)
        # self.buffers.append(buffer)
        self.buffers[key] = buffer
        self.scene.addItem(buffer)        
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            pajeEvent = self.parser.getEvent()
            if pajeEvent == None:
                self.close()
                return
            
            split = pajeEvent.split()
            
            if self.parser.mode == 'EVENT':
                if split[0] == '0':
                    return
                elif split[0] == '3':
                    return
                elif split[0] == '1':
                    if split[2] == '"Fetch_Buffer"':
                        self.addBuffer("FETCH")
                    elif split[2] == '"Decode_Buffer"':
                        self.addBuffer("DECODE")

                elif split[0] == '5':
                    self.buffers["FETCH"].addInstruction(split[1])
                elif split[0] == '6':
                    self.buffers["FETCH"].moveInstruction(split[1], "DECODE")
                    # self.buffers["FETCH"].removeInstruction(split[1])
                    # self.buffers["DECODE"].addInstruction(split[1])

                print(split)
            
            elif self.parser.mode == 'CYCLE':
                self.cycle = self.cycle + 1
                self.textItem.setHtml("<div style=\"text-align:bottom;\"> %s </div>" % self.cycle)
                pass

        elif event.key() == QtCore.Qt.Key_Escape:
            self.close()
