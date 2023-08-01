import time
from PyQt5 import QtWidgets, QtGui, QtCore

PROGRAM_START = QtCore.Qt.FocusReason(0)
EDITING_FINISHED = QtCore.Qt.FocusReason(1)
CHANGED_MODE = QtCore.Qt.FocusReason(2)

import Buffer

PajeDefineContainerType = '0'
PajeCreateContainer = '1'
PajeDefineEventType = '3'
InsertPackage = '5'
RemovePackage = '6'
UpdatePackage = '7'
Clock = '8'
DefineStatusColor = '9'
DefineBufferColor = '10'

SCREEN = '"SCREEN"'
FETCH_BUFFER = '"FETCH_BUFFER"'
DECODE_BUFFER = '"DECODE_BUFFER"'
URS = '"URS"'
UFU = '"UFU"'
ROB = '"ROB"'
MOB_r = '"MOB_r"'
MOB_w = '"MOB_w"'

PACKAGE_STATE_FREE = 'PACKAGE_STATE_FREE' 
PACKAGE_STATE_WAIT = 'PACKAGE_STATE_WAIT'
PACKAGE_STATE_READY = 'PACKAGE_STATE_READY'

status_colors = {}
buffer_colors = {}


class WindoWidget(QtWidgets.QMainWindow):
    def __init__(self, title, parser, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self.parser = parser

        # Set window commons
        self.setWindowTitle(title)
        self.setGeometry(QtGui.QGuiApplication.primaryScreen().availableGeometry())

        self.scene = QtWidgets.QGraphicsScene(
            self.geometry().x(),
            self.geometry().y(),
            self.geometry().width() * 0.7,
            self.geometry().height() * 0.7
        )

        self.buffers = {}
        self.packages_to_send = []

        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setCentralWidget(self.view)

        # self.grabKeyboard()
        self.setFocus(PROGRAM_START)

        self.textItems = {}
        self.cycle = -1
        self.addText('cycle', self.cycle, 
            self.geometry().width() * 0.9,
            self.geometry().height() * 0.9
        )

        self.addText('mode', self.parser.mode, 
            self.geometry().width() - 100,
            self.geometry().height() * 0.9
        )
 
        self.addText('event', '', 
            50,
            self.geometry().height() * 0.9
        )

        self.halfBuffers = 0

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.processPajeEvent)
        self.jumpToCycle = -1
        

        # Buttons
        self.fastForwardLineEdit = QtWidgets.QLineEdit(self)
        self.fastForwardLineEdit.editingFinished.connect(lambda: self.setFocus(EDITING_FINISHED))
        self.fastForwardPushButton = QtWidgets.QPushButton(text="Fast Forward", parent=self)
        self.fastForwardPushButton.clicked.connect(self.fastForward)
        

        self.changeModeGroupBox = QtWidgets.QGroupBox('Mode', parent=self)
        
        self.eventModeButton = QtWidgets.QRadioButton('EVENT', parent=self)
        self.eventModeButton.toggled.connect(lambda: self.changeParserMode('EVENT'))
        self.cycleModeButton = QtWidgets.QRadioButton('CYCLE', parent=self)
        self.cycleModeButton.toggled.connect(lambda: self.changeParserMode('CYCLE'))
        self.cycleModeButton.setChecked(True)

        self.changeModeBoxLayout = QtWidgets.QHBoxLayout()
        self.changeModeBoxLayout.addWidget(self.eventModeButton)
        self.changeModeBoxLayout.addWidget(self.cycleModeButton)
        self.changeModeBoxLayout.addStretch(1)

        self.changeModeGroupBox.setGeometry(QtCore.QRect(
            self.geometry().width()*0.45,
            self.geometry().height()*0.85,
            160,
            60,
        ))
        self.changeModeGroupBox.setLayout(self.changeModeBoxLayout)


        self.fastForwardBoxLayout = QtWidgets.QHBoxLayout()
        self.fastForwardBoxLayout.addWidget(self.fastForwardLineEdit)
        self.fastForwardBoxLayout.addSpacing(5)
        self.fastForwardBoxLayout.addWidget(self.fastForwardPushButton)
        self.fastForwardBoxLayout.addStretch(1)

        self.fastForwardBoxLayout.setGeometry(QtCore.QRect(
            10,
            10,
            self.geometry().width()*0.525,
            self.geometry().height()*1.4
        ))

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addChildLayout(self.fastForwardBoxLayout)
        self.mainLayout.setGeometry(self.geometry())
        self.setLayout(self.mainLayout)


    def changeParserMode(self, mode):
        self.textItems['mode'].setHtml("<div style=\"text-align:bottom;\"> %s </div>" % mode)
        self.parser.changeMode(mode)
        self.setFocus(CHANGED_MODE)


    def fastForward(self):
        cycle = int(self.fastForwardLineEdit.text())
        
        if self.parser.mode == 'EVENT':
            while self.cycle != cycle:
                self.processPajeEvent()
        elif self.parser.mode == 'CYCLE':
            self.jumpToCycle = cycle
            self.timer.start(125)

        self.fastForwardLineEdit.setText('')


    def addText(self, label, text, ax, ay):
        self.textItems[label] = QtWidgets.QGraphicsTextItem()
        self.textItems[label].setPos(ax, ay)
        self.textItems[label].setDefaultTextColor(QtCore.Qt.red)
        self.textItems[label].setHtml("<div style=\"text-align:bottom;\"> %s </div>" % text)
        self.scene.addItem(self.textItems[label])        


    def addBuffer(self, Name, Type, buffer_colors):
        buffer = None

        if (
            Type == FETCH_BUFFER
            or Type == DECODE_BUFFER
            or Type == URS
            or Type == UFU
        ):
            buffer = Buffer.BufferObject(
                Name,
                Type,
                posx=10.0 + (210.0 * float(len(self.buffers)) + 1.0),
                posy=10.0,
                orientation='vertical',
                size='full',
                buffer_colors=buffer_colors
            )

        elif (
            Type == MOB_r
        ):
            self.halfBuffers = self.halfBuffers + 1
            multiplier = float(self.halfBuffers % 2)

            buffer = Buffer.BufferObject(
                Name,
                Type,
                posx=10.0 + (210.0 * float(len(self.buffers)) + 1.0),
                posy=10.0,
                orientation='vertical',
                size="half",
                buffer_colors=buffer_colors
            )

        elif (
            Type == MOB_w
        ):
            self.halfBuffers = self.halfBuffers + 1
            multiplier = 1.0 + float(self.halfBuffers % 2)

            buffer = Buffer.BufferObject(
                Name,
                Type,
                posx=10.0 + (210.0 * float(len(self.buffers) - 1) + 1.0),
                posy=10.0 + 15.0 + 230.0,
                orientation='vertical',
                size="half",
                buffer_colors=buffer_colors
            )

        elif (
            Type == ROB
        ):
            buffer = Buffer.BufferObject(
                Name,
                Type,
                posx=10.0 + (210.0 * float(len(self.buffers) - 1) + 1.0),
                posy=10.0,
                orientation='vertical',
                size="full",
                buffer_colors=buffer_colors
            )

        self.buffers[Name] = buffer
        # item = QtWidgets.QLayoutItem()
        # self.buffersLayout.addChildWidget(self.buffers[Name])
        self.scene.addItem(buffer)


    def processPajeEvent(self):
        pajeEvent = self.parser.getEvent()
        if pajeEvent == None:
            self.close()
            return            
        self.textItems['event'].setHtml("<div style=\"text-align:bottom;\"> %s </div>" % pajeEvent)

        split = pajeEvent.split()
        eventName = split[0]

        if eventName == PajeDefineContainerType:
            pass
       
        elif eventName == PajeDefineEventType:
            pass

        elif eventName == PajeCreateContainer:
            Name = split[2]
            Type = split[3]
            if Type == SCREEN:
                self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.gray, QtCore.Qt.SolidPattern))
            else:
                self.addBuffer(Name, Type, buffer_colors=buffer_colors)

        elif eventName == InsertPackage:
            Type = split[1]
            Id = split[2]
            BufferName = split[3]
            Content = split[4]               
            self.buffers[BufferName].addPackage(Type, Id, Content, status_colors=status_colors)

        elif eventName == RemovePackage:
            Id = split[2]
            BufferName = split[3]
            self.buffers[BufferName].removePackage(Id)
                
        elif eventName == UpdatePackage:
            Id = split[2]
            BufferName = split[3]
            Content = split[4]
            self.buffers[BufferName].updatePackage(Id, Content)

        elif eventName == Clock:
            Cycle = split[1]
            self.cycle = int(Cycle)
            self.textItems['cycle'].setHtml("<div style=\"text-align:bottom;\"> %s </div>" % self.cycle)
                
            if self.parser.mode == 'CYCLE' and (self.jumpToCycle == self.cycle or self.jumpToCycle == -1):
                self.timer.stop()
                self.jumpToCycle = -1

        elif eventName == DefineStatusColor:
            Status = split[1][1:-1]
            Color = split[2][1:-1]
            status_colors[Status] = QtGui.QColor(Color)

        elif eventName == DefineBufferColor:
            Type = split[1]
            Color = split[2][1:-1]
            buffer_colors[Type] = QtGui.QColor(Color)

            
        self.update()


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            if self.parser.mode == 'EVENT':
                self.processPajeEvent()
            elif self.parser.mode == 'CYCLE':
                self.timer.start(125)

        elif event.key() == QtCore.Qt.Key_Escape:
            self.close()
