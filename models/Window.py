import time
# import traceback
from PyQt5 import QtWidgets, QtGui, QtCore

from . import Trace
from . import Buffer


# Screen focus reasons
PROGRAM_STARTED = QtCore.Qt.FocusReason(0)
EDITING_FINISHED = QtCore.Qt.FocusReason(1)
CHANGED_MODE = QtCore.Qt.FocusReason(2)
LOADED_TRACE = QtCore.Qt.FocusReason(3)
CLICKED= QtCore.Qt.FocusReason(4)
CREATED_SUBWINDOW = QtCore.Qt.FocusReason(5)

# Paje Events
DefineBufferType = '0'
CreateBuffer = '1'
DefinePackageType = '2'
InsertPackage = '5'
RemovePackage = '6'
UpdatePackage = '7'
Clock = '8'
DefineStatusColor = '9'
DefineBufferColor = '10'

# Auxiliary dictionaries
STATUS_COLORS = {}
BUFFER_TYPES = {}
BUFFER_IDS = {}
PACKAGE_TYPES = {}


class CustomSlider(QtWidgets.QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def event(self, e):
        if e.type() == QtCore.QEvent.ToolTip:
            QtWidgets.QToolTip.showText(e.globalPos(), str(self.value()), self)
        return super().event(e)

class ZoomableMdiArea(QtWidgets.QMdiArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.zoom_level = 1

    def wheelEvent(self, event):
        # Control key + Scroll for zooming
        if event.modifiers() == QtCore.Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_level += 0.1
            elif delta < 0:
                self.zoom_level -= 0.1
            self.zoom_level = max(0.1, self.zoom_level)  # Prevent zoom_level from going below 0.1

            # Apply zoom to each subwindow
            for window in self.subWindowList():
                window.setZoom(self.zoom_level)
        else:
            super().wheelEvent(event)


class Visualizer(QtWidgets.QMainWindow):
    def __init__(
        self, title,
        trace=None, plot_name=None,
        skip_exit_confirmation=False, play=False,
        show_histogram=False,
        *args, **kwargs
    ):
        super().__init__(*args,**kwargs)

        self.skip_exit_confirmation = skip_exit_confirmation
        self.play = play
        self.plot_name = plot_name
        self.trace = trace
        self.show_histogram = show_histogram

        self.parser = None
        self.cycle = int(-1)
        self.jumpToCycle = int(-1)
        self.text_widgets = {}
        self.buffers = {}
        self.inputs = {}
        self.sliders = {}
        self.buttons = {}
        self.selectors = {}
        self.sub_windows = {}
        self.search = None
        self.found = None
        self.execution_mode = 'STEP'
        self.advance_type = 'EVENT'
        self.advance_increment = int(1)
        self.advance_executed = int(0)
        self.is_playing = {"value": False, "triggered": None}
        self.delay = int(1)

        # Timer to execute cycle advances
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.processPajeEvent)

        # Set window commons
        self.setWindowTitle(title)
        # self.setGeometry(QtGui.QGuiApplication.screens()[-1].availableGeometry())
        self.setGeometry(QtGui.QGuiApplication.primaryScreen().availableGeometry())

        # Central Widget
        # self.mdi_area = QtWidgets.QMdiArea()
        self.mdi_area = ZoomableMdiArea()
        self.mdi_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi_area.setBackground(QtGui.QBrush(QtGui.QColor('#C3B9FF'), QtCore.Qt.SolidPattern))
        self.setCentralWidget(self.mdi_area)

        # Add text to the statusBar
        self.statusBar().setStyleSheet("QStatusBar { border-top: 1px solid gray; }")
        self.addText('cycle', "ciclo:\t%s" % self.cycle, 150)

        # Add control input fields
        self.addPlayPauseButton(QtCore.Qt.TopDockWidgetArea)
        self.addDockSpacing(QtCore.Qt.TopDockWidgetArea)
        self.addSlider(
            "delay", "Intervalo (1~1000 ms)",
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
                    'display_name': 'Salto',
                    'callback': lambda: self.changeExecutionMode('STEP'),
                    'default': True
                },
                {
                    'value': 'QUICKSTEP',
                    'display_name': 'Salto Rápido',
                    'callback': lambda: self.changeExecutionMode('QUICKSTEP'),
                }
            ],
            280, 40,
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
        load_action = QtWidgets.QAction("Carregar", self)
        load_action.setShortcut("Ctrl+L")
        load_action.triggered.connect(self.loadTrace)

        advance_action = QtWidgets.QAction("Avançar", self)
        advance_action.setShortcut("Right")
        advance_action.triggered.connect(self.advance)

        play_pause_action = QtWidgets.QAction("Iniciar/Pausar", self)
        play_pause_action.setShortcut("Space")
        play_pause_action.triggered.connect(lambda: self.toggle_play_pause(True))

        reset_action = QtWidgets.QAction("Reiniciar", self)
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(self.resetWindow)

        exit_action = QtWidgets.QAction("Sair", self)
        exit_action.setShortcut("Esc")
        exit_action.triggered.connect(self.close)

        trace_menu = self.menuBar().addMenu("Traço")
        trace_menu.addAction(load_action)
        self.addAction(advance_action)
        self.addAction(play_pause_action)
        trace_menu.addAction(exit_action)

        # Buffer menu and actions
        cascade_action = QtWidgets.QAction("Cascata", self)
        cascade_action.setShortcut("C")
        cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        self.addAction(cascade_action)

        tile_action = QtWidgets.QAction("Ladrilho", self)
        tile_action.setShortcut("T")
        tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        self.addAction(tile_action)

        buffer_menu = self.menuBar().addMenu("Buffer")
        buffer_menu.addAction(cascade_action)
        buffer_menu.addAction(tile_action)


        # Settings menu and actions
        # Create settings
        self.settings = QtCore.QSettings("HiPES", "VOrCS")

        fullscreen_action = QtWidgets.QAction("Tela Cheia", self)
        fullscreen_action.setShortcut("Ctrl+F")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)

        clear_action = QtWidgets.QAction("Limpar Configurações", self)
        clear_action.setShortcut("Del")
        clear_action.triggered.connect(self.clear)
        self.addAction(clear_action)

        settings_menu = self.menuBar().addMenu("Outros")
        settings_menu.addAction(fullscreen_action)
        settings_menu.addAction(clear_action)

        self.settings.beginGroup("Trace")
        
        if self.trace != None:
            self.settings.setValue("FilePath", self.trace)

        file_path = self.settings.value("FilePath") 
        self.addText('event', 'evento:\t', 900)
        self.addText('trace', 'traço:\t', 600)

        if file_path:
            try:
                self.parser = Trace.PajeParser(file_path)
                self.text_widgets['trace'].setText('traço:\t%s...' % file_path[:88] if len(file_path) > 88 else 'traço:\t%s' % file_path)
            except Exception as e:
                # print(e)
                # traceback.print_exc()
                pass

        self.settings.endGroup()

        # Give the main window focus
        self.setFocus(PROGRAM_STARTED)

        self.events = 0

        self.advance_start_time = 0
        self.advance_start_event = 0
        self.advance_start_cycle = 0
        self.advance_processing_time = 0

        if self.play:
            self.toggle_play_pause(True)

        # self.statusBar().showMessage("Ready")

    def perf(self, start=False, end=False, reset=False):
        if start:
            self.advance_start_time = time.perf_counter()
            self.advance_start_event = self.events
            self.advance_start_cycle = self.cycle

        elif end:
            self.advance_processing_time = time.perf_counter() - self.advance_start_time
            print("========== Advance ======================")
            print(f"processing_time: {self.advance_processing_time:.3f} seconds")
            print("\t %.3f events/second" % ((self.events - self.advance_start_event)/self.advance_processing_time))
            print("\t %.3f cycles/second" % ((self.cycle - self.advance_start_cycle)/self.advance_processing_time))
            print("=========================================\n")

        if reset:
            self.advance_start_time = 0
            self.advance_start_event = 0
            self.advance_start_cycle = 0
            self.advance_processing_time = 0

    def clear(self):
        self.settings.clear()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()  # Restore normal size
        else:
            self.showFullScreen()  # Go fullscreen

    def toggle_play_pause(self, triggered_by_click=False):
        self.is_playing["triggered"] = triggered_by_click

        if self.is_playing.get("value", False):
            self.buttons["playPause"].setText("Iniciar")
            self.is_playing["value"] = not self.is_playing["value"]
            self.timer.stop()

            self.perf(end=True, reset=True)

        else:
            if (self.execution_mode != 'CONTINUOUS'):
                self.buttons["executionMode:CONTINUOUS"].setChecked(True)

            if self.parser == None:
                self.loadTrace()

            self.perf(start=True)

            self.buttons["playPause"].setText("Pausar")
            self.is_playing["value"] = not self.is_playing["value"]
            self.timer.start(self.delay)

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
        dock_widget = QtWidgets.QDockWidget("Avançar (Espaço)", self)
        dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)

        # Create spacer widgets for adding spacing
        bottom_widget = QtWidgets.QWidget()
        bottom_widget.setFixedSize(250, 40)  # Adjust the size as needed

        bottom_layout = QtWidgets.QHBoxLayout()
        self.buttons["playPause"] = QtWidgets.QPushButton("Iniciar")
        self.buttons["playPause"].clicked.connect(lambda: self.toggle_play_pause(True))
        bottom_layout.addWidget(self.buttons["playPause"])

        self.buttons["reset"] = QtWidgets.QPushButton("Reiniciar")
        self.buttons["reset"].clicked.connect(self.resetWindow)
        bottom_layout.addWidget(self.buttons["reset"])

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

        self.buttons[name] = QtWidgets.QPushButton(text="Avançar")
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
        self.selectors["Type"].setFixedWidth(200)
        self.selectors["Buffer"] = QtWidgets.QComboBox()
        self.selectors["Buffer"].setFixedWidth(100)
        
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
        self.sliders[name] = CustomSlider()        
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

        if pajeEvent == '\n':
            return

        if pajeEvent is None:
            if self.is_playing.get("value", False):
                self.toggle_play_pause(self.is_playing.get("triggered", False))

            if self.skip_exit_confirmation:
                return self.close()
            
            # print("pajeEvent is None")
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
            msgBox.setText("O traço terminou de ser processado.")
            msgBox.setWindowTitle("Traço Finalizado")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Close)
            msgBox.button(QtWidgets.QMessageBox.Close).setText("Fechar")
            reset_button = msgBox.addButton("Reiniciar", QtWidgets.QMessageBox.ActionRole)
            reset_button.clicked.connect(self.resetWindow)
            msgBox.exec()
            return
        
        self.events = self.events + 1

        evt = pajeEvent[:-1]
        self.text_widgets['event'].setText('evento:\t%s...' % evt[:88] if len(evt) > 88 else 'evento:\t%s' % evt)

        split = self.parser.splitEvent(pajeEvent)
        print(split)
        eventName = split[0]

        # Definition events
        if eventName == DefineBufferType:
            _Type = split[1]
            _Color = split[2].strip("\"")
            _IsContainer = eval(split[3])

            BUFFER_TYPES[_Type] = {"color": QtGui.QColor(_Color), "is_container": _IsContainer}
       
        elif eventName == CreateBuffer:
            _Id = int(split[1])
            _Name = split[2]
            _Type = split[3]
            _Width = int(split[4])
            _Size = int(split[5])

            BUFFER_IDS[_Name] = _Id

            if not self.loadSubWindowStates(
                _Id, _Name, _Type,
                self,
                BUFFER_TYPES=BUFFER_TYPES,
                grid_geometry=(_Width, _Size)
            ):
                self.addBuffer(
                    _Id, _Name, _Type,
                    self,
                    BUFFER_TYPES=BUFFER_TYPES,
                    grid_geometry=(_Width, _Size),
                )
            
            if self.show_histogram:
                _histogramId = (0-int(_Id))-1
                if not self.loadHistogramSubwindowState(
                    _histogramId,
                    _Name,
                    self.buffers[_Id],
                    self.sub_windows[_Id],
                    self.mdi_area
                ):
                    # print("addHistogram", _histogramId)
                    self.sub_windows[_Id].histogram = Buffer.HistogramSubWindow(
                        _histogramId,
                        _Name,
                        self.buffers[_Id],
                        self.mdi_area
                    )
                    self.sub_windows[_Id].histogram.showNormal()

        elif eventName == DefinePackageType:
            _Id = int(split[1])
            _Name = split[2]
            
            PACKAGE_TYPES[_Id] = _Name

            self.selectors["Type"].addItem(PACKAGE_TYPES[_Id])

        elif eventName == DefineStatusColor:
            _Status = split[1].strip("\"")
            _Color = split[2].strip("\"")

            STATUS_COLORS[_Status] = QtGui.QColor(_Color)
    
        # Execution events        
        if eventName == InsertPackage:
            _TypeId = int(split[1])
            _Id = split[2]
            _BufferIds = eval(split[3])
            _Content = eval(split[4])

            searchEnded = False
            for _BufferId in _BufferIds:
                if self.search:
                    if self.search['BufferId'] == _BufferId:
                        if self.search['Type'] == '\"OperationPackage\"' and PACKAGE_TYPES[_TypeId] == '\"UopPackage\"':
                            if self.search['Id'] == _Content.get('operation'):
                                searchEnded = True
                                self.search = None
                                if self.execution_mode == 'CONTINUOUS':
                                    self.toggle_play_pause()
                        else:
                            if self.search['Id'] == _Id: 
                                searchEnded = True
                                self.search = None
                                if self.execution_mode == 'CONTINUOUS':
                                    self.toggle_play_pause()

            if self.execution_mode != "QUICKSTEP" or searchEnded:
                self.buffers[_BufferId].addPackage(
                    PACKAGE_TYPES[_TypeId], _Id, _Content,
                    STATUS_COLORS=STATUS_COLORS
                )
            
            if searchEnded:
                self.buffers[_BufferId].packages[_Id].selectedChange.emit(True)
                self.found = self.buffers[_BufferId].packages[_Id]
 
        elif eventName == UpdatePackage:
            _TypeId = int(split[1])
            _Id = split[2]
            _BufferIds = eval(split[3])
            _Content = eval(split[4])

            if self.execution_mode != "QUICKSTEP":
                for _BufferId in _BufferIds:
                    self.buffers[_BufferId].updatePackage(_Id, _Content)

        elif eventName == RemovePackage:
            _TypeId = int(split[1])
            _Id = split[2]
            _BufferIds = eval(split[3])

            if self.execution_mode != "QUICKSTEP":
                for _BufferId in _BufferIds:
                    self.buffers[_BufferId].removePackage(_Id)
                
        elif eventName == Clock:
            _Cycle = int(split[1])

            self.cycle = _Cycle

            if self.execution_mode != "QUICKSTEP" or self.cycle == self.jumpToCycle:
                if self.execution_mode == 'CONTINUOUS' and self.search == None and not self.is_playing.get("triggered", False):
                    if self.advance_type == 'CYCLE':
                        if self.cycle >= self.jumpToCycle:
                            self.toggle_play_pause()

                self.text_widgets['cycle'].setText('ciclo:\t%s...' % str(self.cycle)[:88] if len(str(self.cycle)) > 88 else 'ciclo:\t%s' % self.cycle)
     
                for bufferKey in self.buffers:
                    buffer = self.buffers.get(bufferKey)
                    buffer.updateHistogramData(self.cycle, update_histogram=self.show_histogram)

        # Handle advancing
        if self.execution_mode == 'CONTINUOUS' and self.search == None and not self.is_playing.get("triggered", False):
            if self.advance_type == 'EVENT':
                if self.advance_executed < self.advance_increment - 1:
                    self.advance_executed = self.advance_executed + 1
                else:
                    self.advance_executed = 0
                    self.toggle_play_pause()

        if self.execution_mode != "QUICKSTEP":
            self.update()

    def advance(self):
        if self.parser == None:
            self.loadTrace()

        self.perf(start=True)

        if self.execution_mode == 'STEP' or self.execution_mode == 'QUICKSTEP':
            if self.advance_type == 'EVENT':
                for i in range(self.advance_increment):
                    self.processPajeEvent()
            elif self.advance_type == 'CYCLE':
                self.jumpToCycle = self.cycle + self.advance_increment                
                while self.cycle < self.jumpToCycle:
                    self.processPajeEvent()
                self.jumpToCycle = -1

            self.perf(end=True, reset=True)

            if self.execution_mode == 'QUICKSTEP':
                self.clearBuffers()
                self.text_widgets['cycle'].setText('ciclo:\t%s...' % str(self.cycle)[:88] if len(str(self.cycle)) > 88 else 'ciclo:\t%s' % self.cycle)

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
        except Exception as e:
            # print(e)
            # traceback.print_exc()
            pass
        # self.setFocus(EDITING_FINISHED)

    def slider_moved(self):
        value = self.sliders["delay"].value()
        self.delay = value
        if self.timer.isActive():
            self.timer.stop()
            self.timer.start(self.delay)

    def onSearch(self):
        if self.found:
            self.found.selectedChange.emit(False)
            self.found = None

        self.search = {
            'Type': self.selectors['Type'].currentText(),
            'Id': self.inputs['advanceUntil'].text(),
            'BufferId': BUFFER_IDS[self.selectors['Buffer'].currentText()]
        }

        if self.execution_mode == 'STEP' or self.execution_mode == 'QUICKSTEP':
            while not self.found:
                self.processPajeEvent()
        elif self.execution_mode == 'CONTINUOUS':
            self.toggle_play_pause()

    def addBuffer(self, _Id, _Name, _Type, window, BUFFER_TYPES, grid_geometry):
        # print("addBuffer", _Id)
        self.selectors['Buffer'].addItem(_Name)

        sub_window = Buffer.BufferSubWindow(
            _Id, _Name, _Type,
            self.buffers,
            BUFFER_TYPES,
            grid_geometry,
            window,
            save_in_settings=True,
            parent=self.mdi_area,
        )
        self.sub_windows[_Id] = sub_window
        sub_window.showNormal()
        
        self.setFocus(CREATED_SUBWINDOW)

        return sub_window

    def clearBuffers(self):
        for key in self.buffers.keys():
            self.buffers[key].clearBuffer()
            self.buffers[key].clearHistogramData(self.cycle, update_histogram=self.show_histogram)
            

    # Actions and Settings
    def loadTrace(self):
        if self.is_playing.get("value", False):
            self.toggle_play_pause(self.is_playing.get("triggered", False))

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)

        if file_path:
            self.resetWindow()
            self.parser = Trace.PajeParser(file_path)
            self.text_widgets['trace'].setText('traço:\t%s...' % file_path[:88] if len(file_path) > 88 else 'traço:\t%s' % file_path)
            self.buttons["executionMode:STEP"].setChecked(True)

            self.settings.beginGroup("Trace")
            self.settings.setValue("FilePath", file_path)
            self.settings.endGroup()

        self.setFocus(LOADED_TRACE)

    def loadSubWindowStates(self,
        _Id, _Name, _Type,
        window,
        BUFFER_TYPES=None,
        grid_geometry=None
    ):
        # print("loadSubWindowStates")
        loaded = False

        self.settings.beginGroup("SubWindows")
        sub_window_count = self.settings.beginReadArray("SubWindowList")

        # print("sub_window_count", sub_window_count)
        
        for i in range(sub_window_count):
            # print("i", i, "sub_window_count", sub_window_count)
            self.settings.setArrayIndex(i)

            if self.settings.value("_Id", type=int) == _Id:
                # print("loaded", _Name)
                x = self.settings.value("x", type=int)
                y = self.settings.value("y", type=int)
                width = self.settings.value("width", type=int)
                height = self.settings.value("height", type=int)
                hidden = self.settings.value("hidden", type=bool)

                sub_window = self.addBuffer(
                    _Id, _Name, _Type,
                    window,
                    BUFFER_TYPES=BUFFER_TYPES,
                    grid_geometry=grid_geometry,
                )

                sub_window.setGeometry(x, y, width, height)

                if hidden:
                    sub_window.hide()

                loaded = True

        self.settings.endArray()
        self.settings.endGroup()

        return loaded

    def loadHistogramSubwindowState(self, _Id, _Name, buffer, sub_window, parent):
        # print("loadHistogramSubwindowState")
        loaded = False

        self.settings.beginGroup("Histograms")
        sub_window_count = self.settings.beginReadArray("HistogramList")

        # print("sub_window_count", sub_window_count)

        for i in range(sub_window_count):
            # print("i", i, "sub_window_count", sub_window_count)
            self.settings.setArrayIndex(i)

            if self.settings.value("_Id", type=int) == _Id:
                # print("loaded", _Name)
                x = self.settings.value("x", type=int)
                y = self.settings.value("y", type=int)
                width = self.settings.value("width", type=int)
                height = self.settings.value("height", type=int)
                hidden = self.settings.value("hidden", type=bool)

                # print("addHistogram", _Id)
                sub_window.histogram = Buffer.HistogramSubWindow(_Id, _Name, buffer, parent=parent)
                # print("setGeometry", x, y, width, height)
                sub_window.histogram.showNormal()
                sub_window.histogram.setGeometry(x, y, width, height)

                if hidden:
                    sub_window.histogram.hide()

                loaded = True

        self.settings.endArray()
        self.settings.endGroup()

        return loaded

    def saveSubWindowStates(self):
        # print("saveSubWindowStates")
        if len(self.mdi_area.subWindowList()) > 0:
            i = 0
            self.settings.beginGroup("SubWindows")
            self.settings.beginWriteArray("SubWindowList")

            for sub_window in self.mdi_area.subWindowList():
                if sub_window.save_in_settings and not sub_window.is_plot:
                    # print("saved", sub_window.windowTitle())
                    self.settings.setArrayIndex(i)
                    self.settings.setValue("_Id", sub_window.buffer._Id)
                    self.settings.setValue("x", sub_window.geometry().x())
                    self.settings.setValue("y", sub_window.geometry().y())
                    self.settings.setValue("width", sub_window.geometry().width())
                    self.settings.setValue("height", sub_window.geometry().height())
                    self.settings.setValue("hidden", sub_window.isHidden())
                    i = i + 1
                # else:
                #     print("not saved", sub_window.windowTitle())

            self.settings.endArray()
            self.settings.endGroup()

    def saveHistogramSubWindowStates(self):
        # print("saveHistogramSubWindowStates")
        if len(self.mdi_area.subWindowList()) > 0:
            i = 0
            self.settings.beginGroup("Histograms")
            self.settings.beginWriteArray("HistogramList")

            for sub_window in self.mdi_area.subWindowList():
                if sub_window.save_in_settings and sub_window.is_plot:
                    # print("saved", sub_window.windowTitle())
                    self.settings.setArrayIndex(i)
                    self.settings.setValue("_Id", sub_window._Id)
                    self.settings.setValue("x", sub_window.geometry().x())
                    self.settings.setValue("y", sub_window.geometry().y())
                    self.settings.setValue("width", sub_window.geometry().width())
                    self.settings.setValue("height", sub_window.geometry().height())
                    self.settings.setValue("hidden", sub_window.isHidden())
                    i = i + 1
                # else:
                #     print("not saved", sub_window.windowTitle())

            self.settings.endArray()
            self.settings.endGroup()

    # Main Window
    def closeEvent(self, event):
        # print("closeEvent")
        self.saveSubWindowStates()
        if self.show_histogram:
            self.saveHistogramSubWindowStates()
        
        with open("occupancy_data.txt" if self.plot_name == None else "%s_occupancy.txt" % self.plot_name, "w+") as file:
            file.write("cycle:%s\n" % self.cycle)
            for buffer_name, buffer in self.buffers.items():
                file.write("%s:%s\n" % (buffer._Name, buffer.occupancy_histogram_data[1]))

        with open("phases_data.txt" if self.plot_name == None else "%s_phases.txt" % self.plot_name, "w+") as file:
            for buffer_name, buffer in self.buffers.items():
                file.write("%s:%s\n" % (buffer._Name, buffer.phases_data))

        # with open("timing_data.txt" if self.plot_name == None else "%s_timing_data.txt" % self.plot_name, "w+") as file:
        #     try:
        #         file.write("processing_time: %d seconds\n" % self.processing_time)
        #         file.write("\t %f events/second\n" % (self.events/self.processing_time))
        #         file.write("\t %f cycles/second\n" %  ((self.cycle + 1)/self.processing_time))
        #     except Exception as e:
        #         file.write("Profiling error: %s\n" % e)

        event.accept()

    def resetWindow(self):
        # self.saveSubWindowStates()
        # if self.show_histogram:
        #     self.saveHistogramSubWindowStates()

        if self.is_playing.get("value", False):
            self.toggle_play_pause(self.is_playing.get("triggered", False))

        for i in range(0, self.selectors['Type'].count()):
            self.selectors['Type'].removeItem(0)

        for i in range(0, self.selectors['Buffer'].count()):
            self.selectors['Buffer'].removeItem(0)

        buffersIds = list(self.buffers.keys())
        for bufferId in buffersIds:
            packageIds = list(self.buffers[bufferId].packages.keys())
            for packageId in packageIds:
                self.buffers[bufferId].removePackage(packageId)

        subwindowIds = list(self.sub_windows.keys())
        for subwindowId in subwindowIds:
            if self.show_histogram:
                self.sub_windows[subwindowId].histogram.close()
            self.mdi_area.removeSubWindow(self.sub_windows[subwindowId])

        parser = self.parser
        del parser
        self.cycle = int(-1)
        self.jumpToCycle = int(-1)
        self.search = None
        self.found = None
        self.advance_executed = int(0)

        
        self.text_widgets['event'].setText('evento:\t%s' % "")
        self.text_widgets['cycle'].setText('ciclo:\t%s' % "-1")
        self.text_widgets['trace'].setText('traço:\t%s' % "")

        self.settings.beginGroup("Trace")
        file_path = self.settings.value("FilePath")

        if file_path:
            try:
                self.parser = Trace.PajeParser(file_path)
                self.text_widgets['trace'].setText('traço:\t%s...' % file_path[:88] if len(file_path) > 88 else 'traço:\t%s' % file_path)
                
            except Exception as e:
                # print(e)
                # traceback.print_exc()
                pass

        self.settings.endGroup()
