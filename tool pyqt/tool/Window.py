import time
from PyQt5 import QtWidgets, QtGui, QtCore

import Trace
import Buffer


PROGRAM_START = QtCore.Qt.FocusReason(0)
EDITING_FINISHED = QtCore.Qt.FocusReason(1)
CHANGED_MODE = QtCore.Qt.FocusReason(2)
LOADED_TRACE = QtCore.Qt.FocusReason(3)

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

# TODO: Retomar planejamento do caderno



# TODO: Checar se o traço do OrCS está gerando múltiplos opcodes para cada Operation
#       checar se as instruções MOV estão sendo criadas uops (operation 3 e 5 do traço Real)
# TODO: Adicionar ações
    # avancar 1
    # avancar até próximo clock
# TODO: Adicionar informações extras na message box de conteudo dos pacotes (ver caderno)





# TODO: pensei em adicionar (0, linha do evento, evento inverso), que tal criar os eventos inversos no código do orcs?
# TODO: adicionar ponteiros para eventos de clock  para as linhas em vez das linhas em si
    # veja quantos clocks tem e vá construindo
    # realize busca binária ou busca linear em cima de um vetor de ponteiros para pegar as linhas 
    


# Possíveis caminhos
    # TODO: colocar pela posição no buffer do OrCS na inserção do package, não o packageHistory lenght
    # TODO: adicionar barra de execução, (tipo barra de play de video)
    # TODO: Usar QProgressDialog quando tiver criando o vetor com os dados e seus eventos
    # TODO: Escolher entre
        # TODO: Adicionar informações extras no proprio pacote qundo passar o mouse em cima, mudar a forma do pacote
        # TODO: Criar uma custom message box c mais infos e remover espaço da messagebox
        # TODO: Abrir uma nova janela mdi ao invés de uma messagebox para que você possa aompanhar as mudanças no conteudo da instrução
    # TODO:

class CustomQGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, buffer=None, *args, **kwargs):
        self.buffer = buffer
        super().__init__(*args, **kwargs)

    def resizeEvent(self, event):
        self.buffer.setPos(0, 0)
        self.buffer.setGeometry(QtCore.QRectF(0, 0, event.size().width(), event.size().height()))

        super().resizeEvent(event)


class Visualizer(QtWidgets.QMainWindow):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self.parser = None
        self.cycle = -1
        self.jumpToCycle = -2
        self.text_widgets = {}
        self.buffers = {}
        self.inputs = {}
        self.buttons = {}
        self.selectors = {}
        self.search = None
        self.found = None

        
        # Timer to execute cycle advances
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.processPajeEvent)

        # Set window commons
        self.setWindowTitle(title)
        self.setGeometry(QtGui.QGuiApplication.screens()[-1].availableGeometry())
        # TODO: corrigir erros ao settar geometria e usar mais de 1 tela

        # Central Widget
        self.mdi_area = QtWidgets.QMdiArea()
        self.setCentralWidget(self.mdi_area)

        # Add text to the statusBar
        self.statusBar().setStyleSheet("QStatusBar { border-top: 1px solid gray; }")
        self.addText('cycle', "cycle:\t%s" % self.cycle, 70)

        # Add control input fields
        self.addField(
            "fastForward",
            buttonText="Fast Forward",
            inputType=QtWidgets.QLineEdit,
            editingFinishedCallback=lambda: self.setFocus(EDITING_FINISHED),
            buttonType=QtWidgets.QPushButton,
            clickedCallback=lambda: self.fastForward("fastForward")
        )

        self.addRadioField("changeMode")

        self.addComplexField("advanceUntil")


        # Trace menu and actions
        load_action = QtWidgets.QAction("Load", self)
        load_action.setShortcut("Ctrl+L")
        load_action.triggered.connect(self.loadTrace)
        self.addAction(load_action)

        trace_menu = self.menuBar().addMenu("Trace")
        trace_menu.addAction(load_action)

        
        # Buffer menu and actions
        cascade_action = QtWidgets.QAction("Cascade", self)
        cascade_action.setShortcut("C")
        cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        self.addAction(cascade_action)

        tile_action = QtWidgets.QAction("Tile", self)
        tile_action.setShortcut("T")
        tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        self.addAction(tile_action)

        buffer_menu = self.menuBar().addMenu("Buffer")
        buffer_menu.addAction(cascade_action)
        buffer_menu.addAction(tile_action)


        # Settings menu and actions
        # Create settings
        self.settings = QtCore.QSettings("HiPES", "OrCS-Architecture-Viualizer")

        clear_action = QtWidgets.QAction("Clear", self)
        clear_action.triggered.connect(self.settings.clear)
        self.addAction(clear_action)

        settings_menu = self.menuBar().addMenu("Settings")
        settings_menu.addAction(clear_action)

        self.settings.beginGroup("Trace")
        
        self.tree = None
        
        file_path = self.settings.value("FilePath")
        self.addText('event', 'event:\t', 1000)
        self.addText('trace', 'trace:\t', 600)

        if file_path:
            self.parser = Trace.PajeParser(Trace.FileReader(file_path))
            self.text_widgets['trace'].setText('trace:\t%s' % file_path)
            self.buttons["changeMode:CYCLE"].setChecked(True)

        self.settings.endGroup()

        # Give the main window focus
        self.setFocus(PROGRAM_START)

    def loadTrace(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)", options=options)

        if file_path:
            self.parser = Trace.PajeParser(Trace.FileReader(file_path))
            self.text_widgets['trace'].setText('trace:\t%s' % file_path)
            self.buttons["changeMode:CYCLE"].setChecked(True)

            self.settings.beginGroup("Trace")
            self.settings.setValue("FilePath", file_path)
            self.settings.endGroup()

        self.setFocus(LOADED_TRACE)

    def changeParserMode(self, mode):
        if self.parser != None:
            self.parser.changeMode(mode)
        
        self.setFocus(CHANGED_MODE)

    def fastForward(self, Name):
        self.jumpToCycle = int(self.inputs[Name].text())
        
        if self.parser.mode == 'EVENT':
            while self.processPajeEvent():
                pass
        elif self.parser.mode == 'CYCLE':
            self.timer.start(125)

        self.inputs[Name].setText('')

    def addText(self, label, text, width):
        self.text_widgets[label] = QtWidgets.QLabel(text)
        self.text_widgets[label].setStyleSheet("font-size: 12px; color: red; background-color: transparent;")
        self.text_widgets[label].setFixedWidth(width)
        self.statusBar().addWidget(self.text_widgets[label], 0)

    def addField(self, Name, buttonText="Finish", inputType=QtWidgets.QLineEdit, editingFinishedCallback=lambda: print('editing_finished'), buttonType=QtWidgets.QPushButton, clickedCallback=lambda: print("clicked"),
    ):
        # Create a dock widget
        dock_widget = QtWidgets.QDockWidget(Name, self)
        dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures )
        
        # Create control fields
        self.inputs[Name] = inputType()
        self.inputs[Name].editingFinished.connect(editingFinishedCallback)
        self.buttons[Name] = buttonType(text=buttonText)
        self.buttons[Name].clicked.connect(clickedCallback)

        # Create a QHBoxLayout for the dock widget's content
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.inputs[Name])
        layout.addWidget(self.buttons[Name])

        # Create a QWidget for the dock widget's content
        dock_content_widget = QtWidgets.QWidget()
        dock_content_widget.setFixedWidth(250)
        dock_content_widget.setFixedHeight(40)
        dock_content_widget.setLayout(layout)

        # Set the dock widget's content
        dock_widget.setWidget(dock_content_widget)

        # Add the dock widget to the main window
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)

    def addComplexField(self, Name):
        # Create a dock widget
        dock_widget = QtWidgets.QDockWidget(Name, self)
        dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures )
        
        # Create selectors (combo boxes)
        self.selectors["Type"] = QtWidgets.QComboBox()
        self.selectors["Type"].addItems(['\"OperationPackage\"', '\"UopPackage\"'])
        self.selectors["Buffer"] = QtWidgets.QComboBox()
        self.selectors["Buffer"].setFixedWidth(200)
        
        # Create a line editor
        self.inputs[Name] = QtWidgets.QLineEdit()
        # self.inputs[Name].editingFinished.connect(editingFinishedCallback)
        
        # Create a button
        self.buttons[Name] = QtWidgets.QPushButton('Advance')
        self.buttons[Name].clicked.connect(self.onSearch)
        
        # Create a QHBoxLayout for the dock widget's content
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.selectors["Type"])
        layout.addWidget(self.inputs[Name])
        layout.addWidget(self.selectors["Buffer"])
        layout.addWidget(self.buttons[Name])
       
        # Create a QWidget for the dock widget's content
        dock_content_widget = QtWidgets.QWidget()
        dock_content_widget.setFixedWidth(600)
        dock_content_widget.setFixedHeight(40)
        # dock_content_widget.setLayout(main_layout)
        dock_content_widget.setLayout(layout)

        # Set the dock widget's content
        dock_widget.setWidget(dock_content_widget)

        # Add the dock widget to the main window
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)

    def onSearch(self):
        # Get the selected options from the selectors and input from line edit
        Type = self.selectors["Type"].currentText()
        _id = self.inputs['advanceUntil'].text()
        Buffer = self.selectors["Buffer"].currentText()

        if self.found:
            self.found.selectedChange.emit(False)

        self.search = {
            'Type': Type,
            'Id': '\"%s\"' % _id,
            'Buffer': Buffer
        }

        if self.parser.mode == 'EVENT':
            while self.processPajeEvent():
                pass
        elif self.parser.mode == 'CYCLE':
            self.timer.start(125)

    def addRadioField(self, Name):
        # Create a dock widget
        dock_widget = QtWidgets.QDockWidget(Name, self)
        dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        
        # Create control fields
        self.buttons["%s:%s" % (Name, 'EVENT')] = QtWidgets.QRadioButton('EVENT', parent=self)
        self.buttons["%s:%s" % (Name, 'EVENT')].toggled.connect(lambda: self.changeParserMode('EVENT'))
            
        self.buttons["%s:%s" % (Name, 'CYCLE')] = QtWidgets.QRadioButton('CYCLE', parent=self)
        self.buttons["%s:%s" % (Name, 'CYCLE')].toggled.connect(lambda: self.changeParserMode('CYCLE'))

        # Create a QHBoxLayout for the dock widget's content
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.buttons["%s:%s" % (Name, 'EVENT')])
        layout.addWidget(self.buttons["%s:%s" % (Name, 'CYCLE')])

        # Create a QWidget for the dock widget's content
        dock_content_widget = QtWidgets.QWidget()
        dock_content_widget.setFixedWidth(180)
        dock_content_widget.setFixedHeight(40)
        dock_content_widget.setLayout(layout)

        # Set the dock widget's content
        dock_widget.setWidget(dock_content_widget)

        # Add the dock widget to the main window
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)

    def processPajeEvent(self):
        pajeEvent = self.parser.getEvent()

        if pajeEvent == None:
            self.close()
            return False

        self.text_widgets['event'].setText('event:\t%s' % pajeEvent[:-1])

        split = pajeEvent.split()
        eventName = split[0]

        if eventName == PajeDefineContainerType:
            pass
       
        elif eventName == PajeDefineEventType:
            pass

        elif eventName == PajeCreateContainer:
            Name = split[2]
            Type = split[3]
            Width = int(split[4])
            Size = int(split[5])

            if Type == SCREEN:
                self.mdi_area.setBackground(QtGui.QBrush(QtGui.QColor('#C3B9FF'), QtCore.Qt.SolidPattern))
            else:
                if not self.loadSubWindowStates(Name, Type, buffer_colors=buffer_colors):
                    self.addBuffer(
                        Name, Type,
                        buffer_colors=buffer_colors,
                        grid_geometry=(Width, Size)
                    )

        elif eventName == InsertPackage:
            Type = split[1]
            Id = split[2]
            BufferName = split[3]
            Content = split[4]


            self.buffers[BufferName].addPackage(Type, Id, Content, status_colors=status_colors)

            if self.search:
                if self.search['Buffer'] == BufferName:
                    if self.search['Type'] == '\"OperationPackage\"' and Type == '\"UopPackage\"':
                        split = Content[1:-1].split(',')
                        Operation = split[2]

                        if self.search['Id'][1:-1] == Operation:
                            self.found = self.buffers[BufferName].packages[Id]
                            self.search = None

                            self.buffers[BufferName].packages[Id].selectedChange.emit(True)
    
                            if self.parser.mode == 'CYCLE':
                                self.timer.stop()
    
                            self.update()
                            return False

                    else:
                        if self.search['Id'] == Id: 
                            self.found = self.buffers[BufferName].packages[Id]
                            self.search = None

                            self.buffers[BufferName].packages[Id].selectedChange.emit(True)
    
                            if self.parser.mode == 'CYCLE':
                                self.timer.stop()
    
                            self.update()
                            return False

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
            self.text_widgets['cycle'].setText('cycle:\t%s' % self.cycle)
                
            if self.parser.mode == 'CYCLE':
                if self.jumpToCycle != -2:
                    if (self.jumpToCycle == self.cycle):
                        self.jumpToCycle = -2
                        self.timer.stop()
                else:
                    if not self.search:
                        self.timer.stop()
            else:
                if self.jumpToCycle != -2:
                    if (self.jumpToCycle == self.cycle):
                        self.jumpToCycle = -2

        elif eventName == DefineStatusColor:
            Status = split[1][1:-1]
            Color = split[2][1:-1]
            status_colors[Status] = QtGui.QColor(Color)

        elif eventName == DefineBufferColor:
            Type = split[1]
            Color = split[2][1:-1]
            buffer_colors[Type] = QtGui.QColor(Color)
    
        self.update()
        return self.jumpToCycle != -2

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            if self.parser != None:
                if self.parser.mode == 'EVENT':
                    self.processPajeEvent()
                elif self.parser.mode == 'CYCLE':
                    self.timer.start(125)
            event.accept()
        
        elif event.key() == QtCore.Qt.Key_Escape:
            self.close()
            event.accept()

        super().keyPressEvent(event)

    def addBuffer(self, Name, Type, buffer_colors, grid_geometry):
        self.buffers[Name] = Buffer.BufferObject(Name, Type, buffer_colors=buffer_colors, grid_geometry=grid_geometry)
        self.selectors['Buffer'].addItem(Name)

        scene = QtWidgets.QGraphicsScene()
        scene.addItem(self.buffers[Name])
        view = CustomQGraphicsView(buffer=self.buffers[Name])
        view.setScene(scene)

        sub_window = self.mdi_area.addSubWindow(view, flags=QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint)
        sub_window.setWindowTitle(Name)
        sub_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        sub_window.setGeometry(0, 0, 200, 480)

        sub_window.show()
        
        self.setFocus(PROGRAM_START)



    def loadSubWindowStates(self, Name, Type, buffer_colors=None):
        self.settings.beginGroup("SubWindows")
        sub_window_count = self.settings.beginReadArray("SubWindowList")

        loaded = False
        
        for i in range(sub_window_count):
            self.settings.setArrayIndex(i)
            title = self.settings.value("Title")
            if (title == Name):
                position = self.settings.value("Position")
                size = self.settings.value("Size")
                buffer_width = self.settings.value("BufferWidth")
                buffer_size = self.settings.value("BufferSize")

                self.addBuffer(
                    Name, Type, 
                    buffer_colors=buffer_colors,
                    grid_geometry=(buffer_width, buffer_size)
                )

                sub_window = self.mdi_area.subWindowList()[-1]
                sub_window.setGeometry(QtCore.QRect(position, size))

                loaded = True

        self.settings.endArray()
        self.settings.endGroup()

        return loaded

    def saveSubWindowStates(self):
        if len(self.mdi_area.subWindowList()) > 0:
            self.settings.beginGroup("SubWindows")
            self.settings.beginWriteArray("SubWindowList")

            for i, sub_window in enumerate(self.mdi_area.subWindowList()):
                self.settings.setArrayIndex(i)
                self.settings.setValue("Title", sub_window.windowTitle())
                self.settings.setValue("Position", sub_window.geometry().topLeft())
                self.settings.setValue("Size", sub_window.geometry().size())
                self.settings.setValue("BufferWidth", sub_window.widget().buffer.buffer_width)
                self.settings.setValue("BufferSize", sub_window.widget().buffer.buffer_size)


            self.settings.endArray()
            self.settings.endGroup()

    def closeEvent(self, event):
        self.saveSubWindowStates()
        event.accept()


