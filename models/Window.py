import time
from PyQt5 import QtWidgets, QtGui, QtCore

from . import Trace
from . import Buffer


PROGRAM_START = QtCore.Qt.FocusReason(0)
EDITING_FINISHED = QtCore.Qt.FocusReason(1)
CHANGED_MODE = QtCore.Qt.FocusReason(2)
LOADED_TRACE = QtCore.Qt.FocusReason(3)

DefineBufferType = '0'
CreateBuffer = '1'
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
BUFFER_COLORS = {}

# TODO: Adicionar informações extras na message box de conteudo dos pacotes (ver caderno) 
    
# EXTRA:
    # TODO: corrigir erros ao settar geometria e usar mais de 1 tela
    # TODO: Usar strip("_\"") para remover trailing caracters em vez de [1:-1]
    # TODO: adicionar barra de execução, (tipo barra de play de video)
    # TODO: Usar QProgressDialog quando tiver criando o vetor com os dados e seus eventos
    # TODO: Crete custom scroolbar widgets for  the mdi subwindows
    # TODO:


class Visualizer(QtWidgets.QMainWindow):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self.parser = None
        self.cycle = -1
        self.jumpToCycle = -1
        self.text_widgets = {}
        self.buffers = {}
        self.inputs = {}
        self.sliders = {}
        self.buttons = {}
        self.selectors = {}
        self.search = None
        self.found = None
        self.execution_mode = 'STEP'
        self.advance_type = 'EVENT'
        self.advance_increment = 1
        self.advance_executed = 0
        self.is_playing = False
        # self.delay = 125
        self.delay = 1

        # Timer to execute cycle advances
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.processPajeEvent)

        # Set window commons
        self.setWindowTitle(title)
        # self.setGeometry(QtGui.QGuiApplication.screens()[-1].availableGeometry())
        self.setGeometry(QtGui.QGuiApplication.primaryScreen().availableGeometry())

        # Central Widget
        self.mdi_area = QtWidgets.QMdiArea()
        self.mdi_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi_area.setBackground(QtGui.QBrush(QtGui.QColor('#C3B9FF'), QtCore.Qt.SolidPattern))
        self.setCentralWidget(self.mdi_area)

        # Add text to the statusBar
        self.statusBar().setStyleSheet("QStatusBar { border-top: 1px solid gray; }")
        self.addText('cycle', "cycle:\t%s" % self.cycle, 150)

        # Add control input fields
        self.addPlayPauseButton(QtCore.Qt.TopDockWidgetArea)
        self.addDockSpacing(QtCore.Qt.TopDockWidgetArea)
        self.addSlider(
            "delay", "Delay",
            250, 40,
            QtCore.Qt.TopDockWidgetArea
        )

        self.addRadioField(
            "executionMode", "Modo de Execução",
            [
                {
                    'value': 'CONTINUOUS',
                    'display_name': 'Contínuo',
                    'callback': lambda: self.changeExecutionMode('CONTINUOUS')
                },
                {
                    'value': 'STEP',
                    'display_name': 'Step',
                    'callback': lambda: self.changeExecutionMode('STEP'),
                    'default': True
                }
            ],
            180, 40,
            QtCore.Qt.BottomDockWidgetArea
        )
        self.addDockSpacing(QtCore.Qt.BottomDockWidgetArea)
        
        self.addField(
            "advance", "Avançar (Seta Direita)",
            250, 40,
            QtCore.Qt.BottomDockWidgetArea
        )
        self.addDockSpacing(QtCore.Qt.BottomDockWidgetArea)

        self.addComplexField(
            "advanceUntil",
            "Avançar até",
            QtCore.Qt.BottomDockWidgetArea
        )
        

        # Trace menu and actions
        load_action = QtWidgets.QAction("Load", self)
        load_action.setShortcut("Ctrl+L")
        load_action.triggered.connect(self.loadTrace)

        advance_action = QtWidgets.QAction("Advance", self)
        advance_action.setShortcut("Right")
        advance_action.triggered.connect(self.advance)

        play_pause_action = QtWidgets.QAction("Play/Pause", self)
        play_pause_action.setShortcut("Space")
        play_pause_action.triggered.connect(lambda: self.toggle_play_pause())

        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.setShortcut("Esc")
        exit_action.triggered.connect(self.close)

        trace_menu = self.menuBar().addMenu("Trace")
        trace_menu.addAction(load_action)
        self.addAction(advance_action)
        self.addAction(play_pause_action)
        trace_menu.addAction(exit_action)

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

        fullscreen_action = QtWidgets.QAction("Fullscreen Mode", self)
        fullscreen_action.setShortcut("Ctrl+F")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)

        clear_action = QtWidgets.QAction("Clear Settings", self)
        clear_action.setShortcut("Del")
        clear_action.triggered.connect(self.settings.clear)
        self.addAction(clear_action)

        settings_menu = self.menuBar().addMenu("Other")
        settings_menu.addAction(fullscreen_action)
        settings_menu.addAction(clear_action)

        self.settings.beginGroup("Trace")
        
        self.tree = None
        
        file_path = self.settings.value("FilePath")
        self.addText('event', 'event:\t', 900)
        self.addText('trace', 'trace:\t', 600)

        if file_path:
            try:
                self.parser = Trace.PajeParser(file_path)
                self.text_widgets['trace'].setText('trace:\t%s' % file_path)
            except Exception as e:
                print(e)
                pass

        self.settings.endGroup()

        # Give the main window focus
        self.setFocus(PROGRAM_START)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()  # Restore normal size
        else:
            self.showFullScreen()  # Go fullscreen

    def toggle_play_pause(self):
        if self.is_playing:
            self.buttons["playPause"].setText("Play")
            self.timer.stop()
        else:
            if self.parser == None:
                self.loadTrace()
            self.buttons["playPause"].setText("Pause")
            self.timer.start(self.delay)

        self.is_playing = not self.is_playing

    def changeExecutionMode(self, mode):
        self.execution_mode = mode
        self.setFocus(CHANGED_MODE)

# Controls
    def addDockSpacing(self, dockArea):
        dock_widget = QtWidgets.QDockWidget(self)
        dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        # Create spacer widgets for adding spacing
        # spacer = QtWidgets.QWidget()
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)  # Optional: gives it a sunken appearance

        # spacer.setFixedSize(20, 40)  # Adjust the size as needed
        separator.setFixedSize(20, 40)  # Adjust the size as needed
        # Set the dock widget's content
        # dock_widget.setWidget(spacer)
        dock_widget.setWidget(separator)
        # Create content widgets for the dock widgets
        self.addDockWidget(dockArea, dock_widget)

    def addPlayPauseButton(self, dockArea):
        dock_widget = QtWidgets.QDockWidget(self)
        dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)

        # Create spacer widgets for adding spacing
        bottom_widget = QtWidgets.QWidget()
        bottom_widget.setFixedSize(150, 40)  # Adjust the size as needed

        bottom_layout = QtWidgets.QVBoxLayout()
        self.buttons["playPause"] = QtWidgets.QPushButton("Play")
        self.buttons["playPause"].clicked.connect(lambda: self.toggle_play_pause())
        bottom_layout.addWidget(self.buttons["playPause"])

        bottom_widget.setLayout(bottom_layout)
        dock_widget.setWidget(bottom_widget)

        # Create content widgets for the dock widgets
        self.addDockWidget(dockArea, dock_widget)

    def addText(self, label, text, width):
        self.text_widgets[label] = QtWidgets.QLabel(text)
        self.text_widgets[label].setStyleSheet("font-size: 12px; color: red; background-color: transparent;")
        self.text_widgets[label].setFixedWidth(width)
        self.statusBar().addWidget(self.text_widgets[label], 0)

    def addRadioField(self, name, display_name, fields, width, height, dockArea):
        # Create a dock widget
        dock_widget = QtWidgets.QDockWidget(display_name, self)
        dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)

        # Create a QHBoxLayout for the dock widget's content
        layout = QtWidgets.QHBoxLayout()

        # Create control fields
        for field in fields:
            self.buttons["%s:%s" % (name, field['value'])] = QtWidgets.QRadioButton(field['display_name'], parent=self)
            self.buttons["%s:%s" % (name, field['value'])].toggled.connect(field['callback'])
            layout.addWidget(self.buttons["%s:%s" % (name, field['value'])])
            if field.get('default'):
                self.buttons["%s:%s" % (name, field['value'])].setChecked(True)


        # Create a QWidget for the dock widget's content
        dock_content_widget = QtWidgets.QWidget()
        dock_content_widget.setFixedWidth(width)
        dock_content_widget.setFixedHeight(height)
        dock_content_widget.setLayout(layout)

        # Set the dock widget's content
        dock_widget.setWidget(dock_content_widget)

        # Add the dock widget to the main window
        self.addDockWidget(dockArea, dock_widget)

    def addField(self, name, display_name, width, height, dockArea):
        # Create a dock widget
        dock_widget = QtWidgets.QDockWidget(display_name, self)
        dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures )
        
        # Create a QHBoxLayout for the dock widget's content
        layout = QtWidgets.QHBoxLayout()

        # Create control fields
        self.inputs[name] = QtWidgets.QLineEdit(str(self.advance_increment))
        self.inputs[name].textChanged.connect(lambda increment: self.changeAdvanceIncrement(increment))
        layout.addWidget(self.inputs[name])

        self.selectors[name] = QtWidgets.QComboBox()
        self.selectors[name].addItems(['Evento', 'Ciclo'])
        self.selectors[name].currentTextChanged.connect(lambda text: self.changeAdvanceType(text))
        layout.addWidget(self.selectors[name])

        self.buttons[name] = QtWidgets.QPushButton(text="Confirmar")
        self.buttons[name].clicked.connect(lambda: self.advance())
        layout.addWidget(self.buttons[name])


        # Create a QWidget for the dock widget's content
        dock_content_widget = QtWidgets.QWidget()
        dock_content_widget.setFixedWidth(width)
        dock_content_widget.setFixedHeight(height)
        dock_content_widget.setLayout(layout)

        # Set the dock widget's content
        dock_widget.setWidget(dock_content_widget)

        # Add the dock widget to the main window
        self.addDockWidget(dockArea, dock_widget)

    def addComplexField(self, name, display, dockArea):
        # Create a dock widget
        dock_widget = QtWidgets.QDockWidget(display, self)
        dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        
        # Create selectors (combo boxes)
        self.selectors["Type"] = QtWidgets.QComboBox()
        self.selectors["Type"].addItems(['\"OperationPackage\"', '\"UopPackage\"'])
        self.selectors["Buffer"] = QtWidgets.QComboBox()
        self.selectors["Buffer"].setFixedWidth(200)
        
        # Create a line editor
        self.inputs[name] = QtWidgets.QLineEdit()
        # self.inputs[name].editingFinished.connect(editingFinishedCallback)
        
        # Create a button
        self.buttons[name] = QtWidgets.QPushButton('Avançar')
        self.buttons[name].clicked.connect(self.onSearch)
        
        # Create a QHBoxLayout for the dock widget's content
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.selectors["Type"])
        layout.addWidget(self.inputs[name])
        text_widget = QtWidgets.QLabel("entrar no")
        text_widget.setStyleSheet("font-size: 12px; background-color: transparent;")
        text_widget.setFixedWidth(50)
        layout.addWidget(text_widget)

        layout.addWidget(self.selectors["Buffer"])
        layout.addWidget(self.buttons[name])
       
        # Create a QWidget for the dock widget's content
        dock_content_widget = QtWidgets.QWidget()
        dock_content_widget.setFixedWidth(600)
        dock_content_widget.setFixedHeight(40)
        # dock_content_widget.setLayout(main_layout)
        dock_content_widget.setLayout(layout)

        # Set the dock widget's content
        dock_widget.setWidget(dock_content_widget)

        # Add the dock widget to the main window
        self.addDockWidget(dockArea, dock_widget)

    def addSlider(self, name, display_name, width, height, dockArea):
        # Create a dock widget
        dock_widget = QtWidgets.QDockWidget(display_name, self)
        dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures )
        
        # Create a QHBoxLayout for the dock widget's content
        layout = QtWidgets.QHBoxLayout()

        # Create control fields
        self.sliders[name] = QtWidgets.QSlider()
        self.sliders[name].setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.sliders[name].setTickInterval(50)
        self.sliders[name].setOrientation(1)  # Set slider orientation to horizontal (1) or vertical (2)
        self.sliders[name].setMinimum(1)
        self.sliders[name].setMaximum(1000)  
        # self.sliders[name].sliderPressed.connect(self.slider_moved) 
        self.sliders[name].valueChanged.connect(self.slider_moved)  # Connect slider movement to a function
        # self.sliders[name].sliderReleased.connect(self.slider_moved)  
        self.sliders[name].setValue(self.delay)

        layout.addWidget(self.sliders[name])
        
        # Create a QWidget for the dock widget's content
        dock_content_widget = QtWidgets.QWidget()
        dock_content_widget.setFixedWidth(width)
        dock_content_widget.setFixedHeight(height)
        dock_content_widget.setLayout(layout)

        # Set the dock widget's content
        dock_widget.setWidget(dock_content_widget)

        # Add the dock widget to the main window
        self.addDockWidget(dockArea, dock_widget)

# Events
    def processPajeEvent(self):
        pajeEvent = self.parser.getEvent()
        # print(pajeEvent, end='')

        if pajeEvent is None:
            print("pajeEvent is None")
            # TODO: Show alert and close on confirm
            return

        self.text_widgets['event'].setText('event:\t%s' % pajeEvent[:-1])

        split = pajeEvent.split()
        eventName = split[0]

        if eventName == DefineBufferType:
            Type = split[1]
            Color = split[2][1:-1]

            BUFFER_COLORS[Type] = QtGui.QColor(Color)
       
        elif eventName == CreateBuffer:
            Name = split[1]
            Type = split[2]
            Width = split[3]
            Size = split[4]

            if not self.loadSubWindowStates(Name, Type, BUFFER_COLORS=BUFFER_COLORS):
                self.addBuffer(
                    Name, Type,
                    BUFFER_COLORS=BUFFER_COLORS,
                    grid_geometry=(int(Width), int(Size))
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
                            self.buffers[BufferName].packages[Id].selectedChange.emit(True)
                            self.found = self.buffers[BufferName].packages[Id]
                            self.search = None

                            if self.execution_mode == 'CONTINUOUS':
                                self.toggle_play_pause()
    
                    else:
                        if self.search['Id'] == Id: 
                            self.buffers[BufferName].packages[Id].selectedChange.emit(True)
                            self.found = self.buffers[BufferName].packages[Id]
                            self.search = None

                            if self.execution_mode == 'CONTINUOUS':
                                self.toggle_play_pause()
    
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
                
            if self.execution_mode == 'CONTINUOUS':
                if self.advance_type == 'CYCLE':
                    if self.cycle >= self.jumpToCycle:
                        self.toggle_play_pause()

        elif eventName == DefineStatusColor:
            Status = split[1][1:-1]
            Color = split[2][1:-1]

            status_colors[Status] = QtGui.QColor(Color)
    
        if self.execution_mode == 'CONTINUOUS':
            if self.advance_type == 'EVENT':
                if self.advance_executed < self.advance_increment - 1:
                    self.advance_executed = self.advance_executed + 1
                else:
                    self.advance_executed = 0
                    self.toggle_play_pause()

        self.update()

    def advance(self):
        if self.execution_mode == 'STEP':
            if self.advance_type == 'EVENT':
                for i in range(self.advance_increment):
                    self.processPajeEvent()
            elif self.advance_type == 'CYCLE':
                self.jumpToCycle = self.cycle + self.advance_increment                
                while self.cycle < self.jumpToCycle:
                    self.processPajeEvent()
                self.jumpToCycle = -1
        elif self.execution_mode == 'CONTINUOUS':
            if self.advance_type == 'EVENT':
                self.toggle_play_pause()
            elif self.advance_type == 'CYCLE':
                self.jumpToCycle = self.cycle + self.advance_increment
                self.toggle_play_pause()

    def changeAdvanceType(self, text):
        if text == 'Ciclo':
            self.advance_type = 'CYCLE'
        elif text == 'Evento':
            self.advance_type = 'EVENT'
        self.setFocus(EDITING_FINISHED)

    def changeAdvanceIncrement(self, increment):
        try:
            self.advance_increment = int(increment)
        except:
            pass
        # self.setFocus(EDITING_FINISHED)

    def slider_moved(self):
        value = self.sliders["delay"].value()
        self.delay = value
        if self.timer.isActive():
            self.timer.stop()
            self.timer.start(self.delay)

    def onSearch(self):
        # Get the selected options from the selectors and input from line edit
        Type = self.selectors["Type"].currentText()
        _id = self.inputs['advanceUntil'].text()
        Buffer = self.selectors["Buffer"].currentText()

        if self.found:
            self.found.selectedChange.emit(False)
            self.found = None

        self.search = {
            'Type': Type,
            'Id': '\"%s\"' % _id,
            'Buffer': Buffer
        }

        if self.execution_mode == 'STEP':
            while not self.found:
                self.processPajeEvent()
        elif self.execution_mode == 'CONTINUOUS':
            self.toggle_play_pause()

    def addBuffer(self, Name, Type, BUFFER_COLORS, grid_geometry):
        self.selectors['Buffer'].addItem(Name)

        sub_window = Buffer.CustomQMdiSubWindow(
            Name, Type,
            self.buffers,
            BUFFER_COLORS,
            grid_geometry,
            self.mdi_area,
            is_container= Name in ['"Unified_Reservation_Station"', '"Unified_Functional_Units"'], 
            save_in_settings=True
        )
        sub_window.setParent(self.mdi_area)
        sub_window.show()
        
        self.setFocus(PROGRAM_START)

# Actions and Settings
    def loadTrace(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)

        if file_path:
            self.parser = Trace.PajeParser(file_path)
            self.text_widgets['trace'].setText('trace:\t%s' % file_path)
            self.buttons["executionMode:STEP"].setChecked(True)

            self.settings.beginGroup("Trace")
            self.settings.setValue("FilePath", file_path)
            self.settings.endGroup()

        self.setFocus(LOADED_TRACE)

    def loadSubWindowStates(self, Name, Type, BUFFER_COLORS=None):
        self.settings.beginGroup("SubWindows")
        sub_window_count = self.settings.beginReadArray("SubWindowList")

        loaded = False
        
        for i in range(sub_window_count):
            self.settings.setArrayIndex(i)

            if self.settings.value("Title") == Name:
                position = self.settings.value("Position")
                size = self.settings.value("Size")
                buffer_width = self.settings.value("BufferWidth")
                buffer_size = self.settings.value("BufferSize")

                self.addBuffer(
                    Name, Type, 
                    BUFFER_COLORS=BUFFER_COLORS,
                    grid_geometry=(int(buffer_width), int(buffer_size))
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
                if sub_window.save_in_settings:
                    self.settings.setArrayIndex(i)
                    self.settings.setValue("Title", sub_window.windowTitle())
                    self.settings.setValue("Position", sub_window.geometry().topLeft())
                    self.settings.setValue("Size", sub_window.geometry().size())
                    self.settings.setValue("BufferWidth", sub_window.buffer.buffer_width)
                    self.settings.setValue("BufferSize", sub_window.buffer.buffer_size)


            self.settings.endArray()
            self.settings.endGroup()

# Main Window
    def closeEvent(self, event):
        self.saveSubWindowStates()
        event.accept()
